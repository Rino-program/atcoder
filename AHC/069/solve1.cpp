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
        for(int d=0; d<4; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if(nx >= 0 && nx < N && ny >= 0 && ny < N && grid_status[nx][ny] == -1) {
                if(!in_S[nx][ny]) {
                    adj_count[nx][ny]++;
                    int dist = abs(nx - start_x) + abs(ny - start_y);
                    pq.push({nx, ny, adj_count[nx][ny], dist});
                }
            }
        }
    };

    add_to_S(start_x, start_y);

    while(region.size() < P && !pq.empty()) {
        Candidate curr = pq.top();
        pq.pop();

        if(in_S[curr.x][curr.y]) continue;
        if(curr.adj_count != adj_count[curr.x][curr.y]) {
            continue; // 古い情報は無視（最新のものが既にキューに登録済み）
        }

        add_to_S(curr.x, curr.y);
    }

    if(region.size() < P) {
        return {};
    }
    return region;
}

int get_internal_edges(const vector<pair<int, int>>& region) {
    int count = 0;
    static vector<vector<bool>> marked(50, vector<bool>(50, false));
    for(auto p : region) marked[p.first][p.second] = true;

    for(auto p : region) {
        int x = p.first;
        int y = p.second;
        int dx[] = {1, 0};
        int dy[] = {0, 1};
        for(int d=0; d<2; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if(nx >= 0 && nx < N && ny >= 0 && ny < N) {
                if(marked[nx][ny]) {
                    count++;
                }
            }
        }
    }

    for(auto p : region) marked[p.first][p.second] = false;
    return count;
}

bool check_connectivity_without(int remove_idx, int P, const vector<vector<int>>& adj) {
    int start_idx = (remove_idx == 0) ? 1 : 0;
    vector<bool> visited(P, false);
    queue<int> q;
    q.push(start_idx);
    visited[start_idx] = true;
    int count = 1;

    while(!q.empty()) {
        int u = q.front();
        q.pop();
        for(int v : adj[u]) {
            if(v == remove_idx) continue;
            if(!visited[v]) {
                visited[v] = true;
                count++;
                q.push(v);
            }
        }
    }
    return count == P - 1;
}

vector<pair<int, int>> refine_region(vector<pair<int, int>> region) {
    int P = region.size();
    if (P <= 1) return region;

    int dx[] = {-1, 1, 0, 0};
    int dy[] = {0, 0, -1, 1};

    int max_iter = 100;
    bool improved = true;

    while(improved && max_iter-- > 0) {
        improved = false;

        vector<vector<int>> s_idx(N, vector<int>(N, -1));
        for(int i=0; i<P; ++i) {
            s_idx[region[i].first][region[i].second] = i;
        }

        vector<vector<int>> adj(P);
        for(int i=0; i<P; ++i) {
            int x = region[i].first;
            int y = region[i].second;
            for(int d=0; d<4; ++d) {
                int nx = x + dx[d];
                int ny = y + dy[d];
                if(nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    int n_idx = s_idx[nx][ny];
                    if(n_idx != -1) {
                        adj[i].push_back(n_idx);
                    }
                }
            }
        }

        vector<int> removables;
        for(int i=0; i<P; ++i) {
            if(check_connectivity_without(i, P, adj)) {
                removables.push_back(i);
            }
        }

        vector<pair<int, int>> addables;
        vector<vector<bool>> addable_visited(N, vector<bool>(N, false));
        for(int i=0; i<P; ++i) {
            int x = region[i].first;
            int y = region[i].second;
            for(int d=0; d<4; ++d) {
                int nx = x + dx[d];
                int ny = y + dy[d];
                if(nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    if(grid_status[nx][ny] == -1 && s_idx[nx][ny] == -1) {
                        if(!addable_visited[nx][ny]) {
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

        for(int u_idx : removables) {
            int neighbors_u = adj[u_idx].size();
            for(auto v : addables) {
                int neighbors_v = 0;
                bool is_adj = false;
                for(int d=0; d<4; ++d) {
                    int nx = v.first + dx[d];
                    int ny = v.second + dy[d];
                    if(nx >= 0 && nx < N && ny >= 0 && ny < N) {
                        int idx = s_idx[nx][ny];
                        if(idx != -1) {
                            neighbors_v++;
                            if(idx == u_idx) is_adj = true;
                        }
                    }
                }
                int delta = neighbors_v - neighbors_u - (is_adj ? 1 : 0);
                if(delta > best_delta) {
                    best_delta = delta;
                    best_u_idx = u_idx;
                    best_v = v;
                }
            }
        }

        if(best_delta > 0) {
            region[best_u_idx] = best_v;
            improved = true;
        }
    }

    return region;
}

struct CandidateRegion {
    vector<pair<int, int>> cells;
    int edges;
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N >> M >> R)) return 0;
    grid.resize(N);
    for(int i=0; i<N; ++i) {
        cin >> grid[i];
    }

    grid_status.assign(N, vector<int>(N, -1));
    for(int i=0; i<N; ++i) {
        for(int j=0; j<N; ++j) {
            if(grid[i][j] == '#') {
                grid_status[i][j] = -2;
            } else {
                total_grass++;
            }
        }
    }

    mt19937 rng(42);

    for(int i=0; i<M; ++i) {
        int id, S, T, P;
        long long V;
        if (!(cin >> id >> S >> T >> P >> V)) break;

        // 1. 退去処理
        vector<ActiveGroup> next_active;
        for(auto& ag : active_groups) {
            if(ag.T < S) {
                for(auto p : ag.cells) {
                    grid_status[p.first][p.second] = -1;
                }
            } else {
                next_active.push_back(ag);
            }
        }
        active_groups = next_active;

        // 2. 移動の出力 (本ベースラインでは行わないため、0を出力)
        cout << 0 << "\n";

        // 3. 配置検討
        vector<pair<int, int>> empty_cells;
        for(int r=0; r<N; ++r) {
            for(int c=0; c<N; ++c) {
                if(grid_status[r][c] == -1) {
                    empty_cells.push_back({r, c});
                }
            }
        }

        bool accepted = false;
        CandidateRegion best_cand;
        best_cand.edges = -1;

        if((int)empty_cells.size() >= P) {
            // サイズに応じてサンプリング数を調整（2.0sの時間制限を考慮）
            int K = 100;
            if (P > 0) {
                K = 150000 / (P * P);
                if (K < 10) K = 10;
                if (K > 150) K = 150;
            }

            shuffle(empty_cells.begin(), empty_cells.end(), rng);
            int actual_K = min((int)empty_cells.size(), K);

            vector<CandidateRegion> candidates;
            for(int k=0; k<actual_K; ++k) {
                auto start = empty_cells[k];
                auto reg = grow_region(start.first, start.second, P);
                if(!reg.empty()) {
                    int edges = get_internal_edges(reg);
                    candidates.push_back({reg, edges});
                }
            }

            if(!candidates.empty()) {
                sort(candidates.begin(), candidates.end(), [](const CandidateRegion& a, const CandidateRegion& b) {
                    return a.edges > b.edges;
                });

                // 上位候補をローカルサーチでさらに丸める
                int num_to_refine = min((int)candidates.size(), 5);
                vector<CandidateRegion> refined_candidates;

                for(int r=0; r<num_to_refine; ++r) {
                    auto reg = candidates[r].cells;
                    auto refined_reg = refine_region(reg);
                    int edges = get_internal_edges(refined_reg);
                    refined_candidates.push_back({refined_reg, edges});
                }

                sort(refined_candidates.begin(), refined_candidates.end(), [](const CandidateRegion& a, const CandidateRegion& b) {
                    return a.edges > b.edges;
                });

                best_cand = refined_candidates[0];

                // 境界線の長さ L からコンパクト度 C を算出
                int L = 4 * P - 2 * best_cand.edges;
                double C = 4.0 * sqrt(P) / L;

                // 動的なしきい値判断
                double u = (double)empty_cells.size() / total_grass;
                double min_C = 0.45 + 0.35 * (1.0 - u);

                double V_std = P * pow(T - S, 0.9);
                double ratio = V / V_std;

                if (ratio < 0.5) {
                    min_C += 0.15;
                } else if (ratio < 1.0) {
                    min_C += 0.05;
                } else if (ratio > 2.0) {
                    min_C -= 0.15;
                } else if (ratio > 1.5) {
                    min_C -= 0.05;
                }

                min_C = max(0.35, min(0.95, min_C));

                if (C >= min_C) {
                    accepted = true;
                }
            }
        }

        if(accepted) {
            cout << "Yes\n";
            for(auto p : best_cand.cells) {
                cout << p.first << " " << p.second << "\n";
                grid_status[p.first][p.second] = id;
            }
            cout << flush;

            ActiveGroup ag;
            ag.id = id;
            ag.T = T;
            ag.cells = best_cand.cells;
            active_groups.push_back(ag);
        } else {
            cout << "No\n" << flush;
        }
    }

    return 0;
}