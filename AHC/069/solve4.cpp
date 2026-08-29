#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <queue>
#include <cmath>
#include <random>
#include <chrono>

using namespace std;

// タイマー管理
auto start_time = chrono::high_resolution_clock::now();
double get_time() {
    auto now = chrono::high_resolution_clock::now();
    return chrono::duration<double>(now - start_time).count();
}

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
    double current_c;
    vector<pair<int, int>> cells;
};
vector<ActiveGroup> active_groups;

struct Candidate {
    int x, y;
    int adj_count;
    int dist_to_start;

    bool operator<(const Candidate& other) const {
        if (adj_count != other.adj_count) {
            return adj_count < other.adj_count;
        }
        return dist_to_start > other.dist_to_start;
    }
};

struct CandidateRegion {
    vector<pair<int, int>> cells;
    int edges;
    double score;
};

// 再利用可能な静的作業配列
static bool in_S_buf[50][50];
static int adj_count_buf[50][50];
static int s_idx_buf[50][50];
static bool addable_visited_buf[50][50];
static bool marked_buf[50][50];

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
                touch_wall_or_other++;
            } else if (grid_status[nx][ny] != -1) {
                touch_wall_or_other++;
            }
        }
    }
    return edges * 1000.0 + touch_wall_or_other * 50.0 - dist_sum * 0.1;
}

vector<pair<int, int>> grow_region(int start_x, int start_y, int P) {
    vector<pair<int, int>> region;
    region.reserve(P);

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            in_S_buf[i][j] = false;
            adj_count_buf[i][j] = 0;
        }
    }

    priority_queue<Candidate> pq;

    auto add_to_S = [&](int x, int y) {
        in_S_buf[x][y] = true;
        region.push_back({x, y});

        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        for (int d = 0; d < 4; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && grid_status[nx][ny] == -1) {
                if (!in_S_buf[nx][ny]) {
                    adj_count_buf[nx][ny]++;
                    int dist = max(abs(nx - start_x), abs(ny - start_y));
                    pq.push({nx, ny, adj_count_buf[nx][ny], dist});
                }
            }
        }
    };

    add_to_S(start_x, start_y);

    while ((int)region.size() < P && !pq.empty()) {
        Candidate curr = pq.top();
        pq.pop();

        if (in_S_buf[curr.x][curr.y]) continue;
        if (curr.adj_count != adj_count_buf[curr.x][curr.y]) continue;

        add_to_S(curr.x, curr.y);
    }

    if ((int)region.size() < P) return {};
    return region;
}

int get_internal_edges(const vector<pair<int, int>>& region) {
    int count = 0;
    for (auto p : region) marked_buf[p.first][p.second] = true;

    for (auto p : region) {
        int x = p.first, y = p.second;
        int dx[] = {1, 0}, dy[] = {0, 1};
        for (int d = 0; d < 2; ++d) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && marked_buf[nx][ny]) {
                count++;
            }
        }
    }
    for (auto p : region) marked_buf[p.first][p.second] = false;
    return count;
}

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

vector<pair<int, int>> refine_region(vector<pair<int, int>> region, int max_iter = 25) {
    int P = region.size();
    if (P <= 1) return region;

    int dx[] = {-1, 1, 0, 0}, dy[] = {0, 0, -1, 1};
    bool improved = true;

    while (improved && max_iter-- > 0) {
        improved = false;

        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                s_idx_buf[i][j] = -1;

        for (int i = 0; i < P; ++i) {
            s_idx_buf[region[i].first][region[i].second] = i;
        }

        vector<vector<int>> adj(P);
        for (int i = 0; i < P; ++i) {
            int x = region[i].first, y = region[i].second;
            for (int d = 0; d < 4; ++d) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    int n_idx = s_idx_buf[nx][ny];
                    if (n_idx != -1) adj[i].push_back(n_idx);
                }
            }
        }

        vector<int> removables = get_removable_nodes(P, adj);

        vector<pair<int, int>> addables;
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                addable_visited_buf[i][j] = false;

        for (int i = 0; i < P; ++i) {
            int x = region[i].first, y = region[i].second;
            for (int d = 0; d < 4; ++d) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    if (grid_status[nx][ny] == -1 && s_idx_buf[nx][ny] == -1) {
                        if (!addable_visited_buf[nx][ny]) {
                            addable_visited_buf[nx][ny] = true;
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
                        int idx = s_idx_buf[nx][ny];
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

CandidateRegion generate_best_candidate(int P, vector<pair<int, int>>& empty_cells, mt19937& rng, int max_K = 100, int refine_top = 3) {
    CandidateRegion best_cand;
    best_cand.score = -1e18;
    best_cand.edges = -1;

    if ((int)empty_cells.size() < P) return best_cand;

    int K = 150000 / (P * P);
    if (K < 10) K = 10;
    if (K > max_K) K = max_K;

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

        int num_to_refine = min((int)candidates.size(), refine_top);
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

        // 2. 移動処理 (時間が1.7秒未満かつRが低い場合のみ、コンパクト度が低い上位2件程度を検討)
        vector<pair<int, vector<pair<int, int>>>> movements;
        if (get_time() < 1.7 && R < 0.04 && !active_groups.empty()) {
            // コンパクト度が低い順にソートして候補を絞り込む
            vector<pair<double, int>> move_candidates;
            for (size_t idx = 0; idx < active_groups.size(); ++idx) {
                auto& ag = active_groups[idx];
                long long move_cost = max((long long)round(ag.V * R), 1LL);
                if (move_cost < 100) {
                    move_candidates.push_back({ag.current_c, (int)idx});
                }
            }
            sort(move_candidates.begin(), move_candidates.end());

            int best_move_idx = -1;
            CandidateRegion best_move_cand;
            best_move_cand.score = -1e18;
            double best_score_improvement = 0;

            // 上位 2 つのみ検討
            int examine_cnt = min((int)move_candidates.size(), 2);
            for (int c_i = 0; c_i < examine_cnt; ++c_i) {
                int idx = move_candidates[c_i].second;
                auto& ag = active_groups[idx];

                for (auto p : ag.cells) grid_status[p.first][p.second] = -1;

                int current_edges = get_internal_edges(ag.cells);
                double current_score = evaluate_region(ag.cells, current_edges);

                vector<pair<int, int>> cur_empty = empty_cells;
                for (auto p : ag.cells) cur_empty.push_back(p);

                // 移動検討時は探索パラメーターを軽量化 (max_K=30, refine_top=1)
                CandidateRegion cand = generate_best_candidate(ag.P, cur_empty, rng, 30, 1);

                if (cand.score > current_score + 3000.0) {
                    if (cand.score - current_score > best_score_improvement) {
                        best_score_improvement = cand.score - current_score;
                        best_move_idx = idx;
                        best_move_cand = cand;
                    }
                }

                for (auto p : ag.cells) grid_status[p.first][p.second] = ag.id;
            }

            if (best_move_idx != -1) {
                auto& ag = active_groups[best_move_idx];
                for (auto p : ag.cells) grid_status[p.first][p.second] = -1;

                ag.cells = best_move_cand.cells;
                for (auto p : ag.cells) grid_status[p.first][p.second] = ag.id;

                int edges = get_internal_edges(ag.cells);
                int L = 4 * ag.P - 2 * edges;
                ag.current_c = 4.0 * sqrt(ag.P) / L;

                movements.push_back({ag.id, ag.cells});

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

        // 3. 配置検討
        bool accepted = false;
        CandidateRegion best_cand;

        double u = (double)empty_cells.size() / total_grass;
        double V_std = P * pow(T - S, 0.9);
        double ratio = V / V_std;

        double require_ratio = 0.2 + 1.2 * (1.0 - u);

        if (ratio >= require_ratio) {
            // 残り時間が迫っている場合は軽量化
            int max_k = (get_time() > 1.5) ? 30 : 80;
            int ref_top = (get_time() > 1.5) ? 1 : 3;
            best_cand = generate_best_candidate(P, empty_cells, rng, max_k, ref_top);

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

            int edges = get_internal_edges(best_cand.cells);
            int L = 4 * P - 2 * edges;
            double C = 4.0 * sqrt(P) / L;

            ActiveGroup ag;
            ag.id = id; ag.T = T; ag.P = P; ag.V = V; ag.current_c = C;
            ag.cells = best_cand.cells;
            active_groups.push_back(ag);
        } else {
            cout << "No\n" << flush;
        }
    }

    return 0;
}