#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <queue>
#include <cmath>
#include <random>
#include <chrono>

using namespace std;

int N, M;
double R;
vector<string> grid;
vector<vector<int>> grid_status; // -1: empty, -2: pond, >=0: group_id
int total_grass = 0;

struct ActiveGroup {
    int id;
    int T;
    int P;
    long long V;
    vector<pair<int, int>> cells;
};
vector<ActiveGroup> active_groups;

struct Candidate {
    int x, y;
    int adj_count;
    int dist_to_start;

    bool operator<(const Candidate& other) const {
        if (adj_count != other.adj_count) {
            return adj_count < other.adj_count; // 隣接数が多いものを優先
        }
        return dist_to_start > other.dist_to_start; // 距離が小さいものを優先
    }
};

struct CandidateRegion {
    vector<pair<int, int>> cells;
    int edges;
    double score;
};

// 評価関数: 端詰め・コンパクト度を総合評価
double evaluate_region(const vector<pair<int, int>>& cells, int edges) {
    int touch_wall_or_other = 0;
    long long dist_sum = 0;
    for (auto p : cells) {
        dist_sum += (p.first * p.first + p.second * p.second);
        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        for (int d = 0; d < 4; ++d) {
            int nx = p.first + dx[d], ny = p.second + dy[d];
            if (nx < 0 || nx >= N || ny < 0 || ny >= N) {
                touch_wall_or_other++; // 外周
            } else if (grid_status[nx][ny] != -1) {
                touch_wall_or_other++; // 池か他のグループ
            }
        }
    }
    // edges(内部辺)が多い=コンパクト, touchが多い=端に寄っている, dist_sumが小さい=左上に寄っている
    return edges * 1000.0 + touch_wall_or_other * 50.0 - dist_sum * 0.1;
}

// Bounding Box (L∞ norm) を意識したBFS
vector<pair<int, int>> grow_region(int start_x, int start_y, int P) {
    vector<pair<int, int>> region;
    vector<vector<bool>> in_S(N, vector<bool>(N, false));
    vector<vector<int>> adj_count(N, vector<int>(N, 0));

    priority_queue<Candidate> pq;

    auto add_to_S = [&](int x, int y) {
        in_S[x][y] = true;
        region.push_back({x, y});

        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        for (int d = 0; d < 4; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && grid_status[nx][ny] == -1) {
                if (!in_S[nx][ny]) {
                    adj_count[nx][ny]++;
                    // L∞ノルムを使って正方形を形成しやすくする
                    int dist = max(abs(nx - start_x), abs(ny - start_y));
                    pq.push({nx, ny, adj_count[nx][ny], dist});
                }
            }
        }
    };

    add_to_S(start_x, start_y);

    while (region.size() < P && !pq.empty()) {
        Candidate curr = pq.top();
        pq.pop();

        if (in_S[curr.x][curr.y]) continue;
        if (curr.adj_count != adj_count[curr.x][curr.y]) continue;

        add_to_S(curr.x, curr.y);
    }

    if (region.size() < P) return {};
    return region;
}

int get_internal_edges(const vector<pair<int, int>>& region) {
    int count = 0;
    static vector<vector<bool>> marked(50, vector<bool>(50, false));
    for (auto p : region) marked[p.first][p.second] = true;

    for (auto p : region) {
        int x = p.first, y = p.second;
        int dx[] = {1, 0}, dy[] = {0, 1};
        for (int d = 0; d < 2; ++d) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && marked[nx][ny]) {
                count++;
            }
        }
    }
    for (auto p : region) marked[p.first][p.second] = false;
    return count;
}

// Lowlinkによる関節点検出アルゴリズム（削除可能マスをO(P)で列挙）
vector<int> get_removable_nodes(int P, const vector<vector<int>>& adj) {
    vector<int> ord(P, 0), low(P, 0);
    vector<bool> is_art(P, false);
    int timer = 0;

    auto dfs = [&](auto& self, int u, int p) -> void {
        ord[u] = low[u] = ++timer;
        int children = 0;
        for (int v : adj[u]) {
            if (v == p) continue;
            if (ord[v]) {
                low[u] = min(low[u], ord[v]);
            } else {
                children++;
                self(self, v, u);
                low[u] = min(low[u], low[v]);
                if (p != -1 && low[v] >= ord[u]) is_art[u] = true;
            }
        }
        if (p == -1 && children > 1) is_art[u] = true;
    };

    if (P > 0) dfs(dfs, 0, -1);

    vector<int> removables;
    for (int i = 0; i < P; ++i) {
        if (!is_art[i]) removables.push_back(i);
    }
    return removables;
}

vector<pair<int, int>> refine_region(vector<pair<int, int>> region) {
    int P = region.size();
    if (P <= 1) return region;

    int dx[] = {-1, 1, 0, 0}, dy[] = {0, 0, -1, 1};
    int max_iter = 100; // 高速化により試行回数を確保
    bool improved = true;

    while (improved && max_iter-- > 0) {
        improved = false;

        vector<vector<int>> s_idx(N, vector<int>(N, -1));
        for (int i = 0; i < P; ++i) {
            s_idx[region[i].first][region[i].second] = i;
        }

        vector<vector<int>> adj(P);
        for (int i = 0; i < P; ++i) {
            int x = region[i].first, y = region[i].second;
            for (int d = 0; d < 4; ++d) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    int n_idx = s_idx[nx][ny];
                    if (n_idx != -1) adj[i].push_back(n_idx);
                }
            }
        }

        // Lowlinkで削除可能な頂点(関節点でない頂点)を高速に取得
        vector<int> removables = get_removable_nodes(P, adj);

        vector<pair<int, int>> addables;
        vector<vector<bool>> addable_visited(N, vector<bool>(N, false));
        for (int i = 0; i < P; ++i) {
            int x = region[i].first, y = region[i].second;
            for (int d = 0; d < 4; ++d) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    if (grid_status[nx][ny] == -1 && s_idx[nx][ny] == -1) {
                        if (!addable_visited[nx][ny]) {
                            addable_visited[nx][ny] = true;
                            addables.push_back({nx, ny});
                        }
                    }
                }
            }
        }

        int best_delta = 0;
        int best_u_idx = -1;
        pair<int, int> best_v = {-1, -1};

        for (int u_idx : removables) {
            int neighbors_u = adj[u_idx].size();
            for (auto v : addables) {
                int neighbors_v = 0;
                bool is_adj = false;
                for (int d = 0; d < 4; ++d) {
                    int nx = v.first + dx[d], ny = v.second + dy[d];
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                        int idx = s_idx[nx][ny];
                        if (idx != -1) {
                            neighbors_v++;
                            if (idx == u_idx) is_adj = true;
                        }
                    }
                }
                int delta = neighbors_v - neighbors_u - (is_adj ? 1 : 0);
                if (delta > best_delta) {
                    best_delta = delta;
                    best_u_idx = u_idx;
                    best_v = v;
                }
            }
        }

        if (best_delta > 0) {
            region[best_u_idx] = best_v;
            improved = true;
        }
    }
    return region;
}

// 候補生成のラッパー
CandidateRegion generate_best_candidate(int P, vector<pair<int, int>>& empty_cells, mt19937& rng) {
    CandidateRegion best_cand;
    best_cand.score = -1e18;
    best_cand.edges = -1;

    if ((int)empty_cells.size() < P) return best_cand;

    int K = 150000 / (P * P);
    if (K < 15) K = 15;
    if (K > 200) K = 200;

    shuffle(empty_cells.begin(), empty_cells.end(), rng);
    int actual_K = min((int)empty_cells.size(), K);

    vector<CandidateRegion> candidates;
    for (int k = 0; k < actual_K; ++k) {
        auto start = empty_cells[k];
        auto reg = grow_region(start.first, start.second, P);
        if (!reg.empty()) {
            int edges = get_internal_edges(reg);
            double score = evaluate_region(reg, edges);
            candidates.push_back({reg, edges, score});
        }
    }

    if (!candidates.empty()) {
        sort(candidates.begin(), candidates.end(), [](const CandidateRegion& a, const CandidateRegion& b) {
            return a.score > b.score;
        });

        int num_to_refine = min((int)candidates.size(), 10);
        for (int r = 0; r < num_to_refine; ++r) {
            auto reg = candidates[r].cells;
            auto refined_reg = refine_region(reg);
            int edges = get_internal_edges(refined_reg);
            double score = evaluate_region(refined_reg, edges);
            if (score > best_cand.score) {
                best_cand = {refined_reg, edges, score};
            }
        }
    }
    return best_cand;
}


int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N >> M >> R)) return 0;
    grid.resize(N);
    for (int i = 0; i < N; ++i) {
        cin >> grid[i];
    }

    grid_status.assign(N, vector<int>(N, -1));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (grid[i][j] == '#') {
                grid_status[i][j] = -2;
            } else {
                total_grass++;
            }
        }
    }

    mt19937 rng(42);

    for (int i = 0; i < M; ++i) {
        int id, S, T, P;
        long long V;
        if (!(cin >> id >> S >> T >> P >> V)) break;

        // 1. 退去処理
        vector<ActiveGroup> next_active;
        for (auto& ag : active_groups) {
            if (ag.T < S) {
                for (auto p : ag.cells) {
                    grid_status[p.first][p.second] = -1;
                }
            } else {
                next_active.push_back(ag);
            }
        }
        active_groups = next_active;

        vector<pair<int, int>> empty_cells;
        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                if (grid_status[r][c] == -1) empty_cells.push_back({r, c});
            }
        }

        // 2. 移動の出力 (Rが小さい場合のみ、スコア改善が見込める安価な1グループを移動)
        vector<pair<int, vector<pair<int, int>>>> movements;
        if (R < 0.05 && active_groups.size() > 0) {
            int best_move_idx = -1;
            CandidateRegion best_move_cand;
            best_move_cand.score = -1e18;
            double best_score_improvement = 0;

            for (size_t idx = 0; idx < active_groups.size(); ++idx) {
                auto& ag = active_groups[idx];
                long long move_cost = max((long long)round(ag.V * R), 1LL);
                
                if (move_cost < 100) { // 移動コストが安いグループのみ検討
                    // 一時的に除去
                    for (auto p : ag.cells) grid_status[p.first][p.second] = -1;
                    
                    int current_edges = get_internal_edges(ag.cells);
                    double current_score = evaluate_region(ag.cells, current_edges);
                    
                    vector<pair<int, int>> cur_empty = empty_cells;
                    for (auto p : ag.cells) cur_empty.push_back(p);

                    CandidateRegion cand = generate_best_candidate(ag.P, cur_empty, rng);
                    
                    // スコアが大幅に改善する場合のみ採用
                    if (cand.score > current_score + 3000.0) {
                        if (cand.score - current_score > best_score_improvement) {
                            best_score_improvement = cand.score - current_score;
                            best_move_idx = idx;
                            best_move_cand = cand;
                        }
                    }
                    
                    // 戻す
                    for (auto p : ag.cells) grid_status[p.first][p.second] = ag.id;
                }
            }

            if (best_move_idx != -1) {
                auto& ag = active_groups[best_move_idx];
                for (auto p : ag.cells) grid_status[p.first][p.second] = -1; // 古い位置を消す
                
                ag.cells = best_move_cand.cells;
                for (auto p : ag.cells) grid_status[p.first][p.second] = ag.id; // 新しい位置を塗る
                
                movements.push_back({ag.id, ag.cells});
                
                // empty_cellsを再構築
                empty_cells.clear();
                for (int r = 0; r < N; ++r) {
                    for (int c = 0; c < N; ++c) {
                        if (grid_status[r][c] == -1) empty_cells.push_back({r, c});
                    }
                }
            }
        }

        cout << movements.size() << "\n";
        for (auto& mv : movements) {
            cout << mv.first << "\n";
            for (auto p : mv.second) cout << p.first << " " << p.second << "\n";
        }

        // 3. 配置検討と利益率による足切り
        bool accepted = false;
        CandidateRegion best_cand;
        
        // 利益率の足切り判定
        double u = (double)empty_cells.size() / total_grass;
        double V_std = P * pow(T - S, 0.9);
        double ratio = V / V_std;
        
        // 空きが少ないほど、高利益率を要求
        double require_ratio = 0.2 + 1.2 * (1.0 - u); 
        
        if (ratio >= require_ratio) {
            best_cand = generate_best_candidate(P, empty_cells, rng);

            if (best_cand.edges != -1) {
                int L = 4 * P - 2 * best_cand.edges;
                double C = 4.0 * sqrt(P) / L;

                double min_C = 0.45 + 0.35 * (1.0 - u);
                if (ratio < 0.5) min_C += 0.15;
                else if (ratio < 1.0) min_C += 0.05;
                else if (ratio > 2.0) min_C -= 0.15;
                else if (ratio > 1.5) min_C -= 0.05;

                min_C = max(0.35, min(0.95, min_C));

                if (C >= min_C) {
                    accepted = true;
                }
            }
        }

        // 4. 出力
        if (accepted) {
            cout << "Yes\n";
            for (auto p : best_cand.cells) {
                cout << p.first << " " << p.second << "\n";
                grid_status[p.first][p.second] = id;
            }
            cout << flush;

            ActiveGroup ag;
            ag.id = id; ag.T = T; ag.P = P; ag.V = V;
            ag.cells = best_cand.cells;
            active_groups.push_back(ag);
        } else {
            cout << "No\n" << flush;
        }
    }

    return 0;
}