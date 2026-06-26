#include <bits/stdc++.h>
using namespace std;
using namespace std::chrono;

int N = 20, M = 50, K = 10;
vector<string> grid;

int to_id(int i, int j) { return i * N + j; }
pair<int, int> to_pos(int id) { return {id / N, id % N}; }

int calc_T(const vector<vector<int>>& door_h, 
           const vector<vector<int>>& door_v, 
           const vector<vector<int>>& switch_map) {
    auto is_open = [&](int g, int mask) {
        if (g == -1) return true;
        int k = g / 2;
        return ((mask >> k) & 1) == (g & 1);
    };

    static int dist[1024][20][20];
    memset(dist, -1, sizeof(dist));
    dist[0][0][0] = 0;

    struct State { int mask, r, c; };
    queue<State> que;
    que.push({0, 0, 0});

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!que.empty()) {
        auto [mask, i, j] = que.front();
        que.pop();
        int d = dist[mask][i][j];

        if (i == N - 1 && j == N - 1) return d;

        for (int dir = 0; dir < 4; ++dir) {
            int ni = i + dr[dir], nj = j + dc[dir];
            if (ni < 0 || ni >= N || nj < 0 || nj >= N) continue;
            if (grid[ni][nj] == '#') continue;

            int g = -1;
            if (dir == 1) g = door_h[i][j];
            else if (dir == 0) g = door_h[ni][nj];
            else if (dir == 3) g = door_v[i][j];
            else if (dir == 2) g = door_v[ni][nj];

            if (!is_open(g, mask)) continue;

            if (dist[mask][ni][nj] == -1) {
                dist[mask][ni][nj] = d + 1;
                que.push({mask, ni, nj});
            }
        }

        int s = switch_map[i][j];
        if (s != -1) {
            int nmask = mask ^ (1 << s);
            if (dist[nmask][i][j] == -1) {
                dist[nmask][i][j] = d + 1;
                que.push({nmask, i, j});
            }
        }
    }
    return 0;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    auto start_time = steady_clock::now();
    
    if (!(cin >> N >> M >> K)) return 0;
    grid.resize(N);
    for (int i = 0; i < N; ++i) cin >> grid[i];
    
    int best_score = -1;
    vector<vector<int>> best_door_h, best_door_v, best_switch_map;
    mt19937 rng(1337);
    
    int loop_cnt = 0;
    while (true) {
        if ((loop_cnt & 15) == 0) {
            auto now = steady_clock::now();
            if (duration_cast<duration<double>>(now - start_time).count() > 1.90) break;
        }
        loop_cnt++;
        
        vector<pair<int, int>> tree_edges;
        vector<int> parent(N * N, -1);
        vector<vector<bool>> visited(N, vector<bool>(N, false));
        int dr[] = {-1, 1, 0, 0};
        int dc[] = {0, 0, -1, 1};
        
        // 1. 直進優先のDFSで「深い層」を持つ木を生成
        auto dfs = [&](auto& self, int r, int c, int p_id, int last_dir) -> void {
            visited[r][c] = true;
            parent[to_id(r, c)] = p_id;
            
            vector<int> dirs = {0, 1, 2, 3};
            if (last_dir != -1 && uniform_int_distribution<int>(0, 100)(rng) < 70) {
                auto it = find(dirs.begin(), dirs.end(), last_dir);
                if (it != dirs.end()) {
                    dirs.erase(it);
                    shuffle(dirs.begin(), dirs.end(), rng);
                    dirs.insert(dirs.begin(), last_dir); // 直進を優先
                }
            } else {
                shuffle(dirs.begin(), dirs.end(), rng);
            }
            
            for (int d : dirs) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr >= 0 && nr < N && nc >= 0 && nc < N && grid[nr][nc] == '.' && !visited[nr][nc]) {
                    tree_edges.push_back({to_id(r, c), to_id(nr, nc)});
                    if (nr == N - 1 && nc == N - 1) {
                        visited[nr][nc] = true;
                        parent[to_id(nr, nc)] = to_id(r, c);
                        continue; // ゴールは必ず端（葉）にする
                    }
                    self(self, nr, nc, to_id(r, c), d);
                }
            }
        };
        dfs(dfs, 0, 0, -1, -1);
        
        // 2. 木に含まれないバックエッジ（迂回路）を抽出
        vector<pair<int, int>> back_edges;
        set<pair<int,int>> tree_edge_set;
        for (auto& e : tree_edges) tree_edge_set.insert({min(e.first, e.second), max(e.first, e.second)});
        
        for (int i = 0; i < N; ++i) {
            for (int j = 0; j < N; ++j) {
                if (grid[i][j] != '.') continue;
                int u = to_id(i, j);
                if (i + 1 < N && grid[i+1][j] == '.') {
                    int v = to_id(i+1, j);
                    if (!tree_edge_set.count({min(u, v), max(u, v)})) back_edges.push_back({u, v});
                }
                if (j + 1 < N && grid[i][j+1] == '.') {
                    int v = to_id(i, j+1);
                    if (!tree_edge_set.count({min(u, v), max(u, v)})) back_edges.push_back({u, v});
                }
            }
        }
        
        int B = back_edges.size();
        if (B > M) continue; // 安全装置 (制約上あり得ないが念のため)
        
        // 3. 葉ノードの抽出
        vector<int> leaves;
        vector<int> deg(N * N, 0);
        for (auto& e : tree_edges) { deg[e.first]++; deg[e.second]++; }
        for (int i = 0; i < N; ++i) {
            for (int j = 0; j < N; ++j) {
                int u = to_id(i, j);
                if (grid[i][j] == '.' && u != 0 && u != N * N - 1 && deg[u] == 1) {
                    leaves.push_back(u);
                }
            }
        }
        
        int max_switches = min({9, M - B, (int)leaves.size()});
        if (max_switches < 2) continue;
        
        // 4. 木上の全点対最短距離を事前計算
        vector<vector<int>> adj(N * N);
        for (auto& e : tree_edges) {
            adj[e.first].push_back(e.second);
            adj[e.second].push_back(e.first);
        }
        
        vector<vector<int>> distT(N * N, vector<int>(N * N, -1));
        auto bfs_dist = [&](int start) {
            queue<int> q; q.push(start);
            distT[start][start] = 0;
            while (!q.empty()) {
                int u = q.front(); q.pop();
                for (int v : adj[u]) {
                    if (distT[start][v] == -1) {
                        distT[start][v] = distT[start][u] + 1;
                        q.push(v);
                    }
                }
            }
        };
        bfs_dist(0);
        bfs_dist(N * N - 1);
        for (int u : leaves) bfs_dist(u);
        
        // 5. 焼きなましによる「最もエグい往復ルート」の探索
        int C = max_switches;
        vector<int> P(C);
        vector<int> cand = leaves;
        shuffle(cand.begin(), cand.end(), rng);
        for (int i = 0; i < C; ++i) P[i] = cand[i];
        
        auto calc_score = [&](const vector<int>& p) {
            int s = distT[0][p[0]];
            for (int i = 0; i < C - 1; ++i) s += distT[p[i]][p[i+1]];
            s += distT[p[C-1]][N * N - 1];
            return s + C; // スイッチを押すターンも加算
        };
        
        int cur_score = calc_score(P);
        for (int iter = 0; iter < 1000; ++iter) {
            vector<int> next_P = P;
            int type = uniform_int_distribution<int>(0, 1)(rng);
            if (type == 0 && C >= 2) {
                int i = uniform_int_distribution<int>(0, C - 1)(rng);
                int j = uniform_int_distribution<int>(0, C - 1)(rng);
                swap(next_P[i], next_P[j]);
            } else if (cand.size() > C) {
                int i = uniform_int_distribution<int>(0, C - 1)(rng);
                int new_v = leaves[uniform_int_distribution<int>(0, leaves.size() - 1)(rng)];
                bool ok = true;
                for (int x : next_P) if (x == new_v) ok = false;
                if (ok) next_P[i] = new_v;
            }
            
            int nxt_score = calc_score(next_P);
            if (nxt_score >= cur_score) { // 山登りで更新
                cur_score = nxt_score;
                P = next_P;
            }
        }
        
        // 6. ベストスコアなら盤面を採用
        if (cur_score > best_score) {
            best_score = cur_score;
            best_door_h.assign(N, vector<int>(N, -1));
            best_door_v.assign(N, vector<int>(N, -1));
            best_switch_map.assign(N, vector<int>(N, -1));
            
            auto place_door = [&](int u, int p, int g) {
                if (p == -1) return;
                int ur = u / N, uc = u % N, pr = p / N, pc = p % N;
                if (ur == pr) best_door_v[ur][min(uc, pc)] = g;
                else best_door_h[min(ur, pr)][uc] = g;
            };
            
            // 全ての迂回路を「永遠に開かない扉(19)」で完全封鎖
            for (auto& e : back_edges) place_door(e.first, e.second, 19);
            
            // スイッチと連動扉の配置
            for (int i = 0; i < C; ++i) {
                int r = P[i] / N, c = P[i] % N;
                best_switch_map[r][c] = i;
                if (i > 0) place_door(P[i], parent[P[i]], 2 * (i - 1) + 1);
            }
            // 最後の扉をゴール前に配置
            place_door(N * N - 1, parent[N * N - 1], 2 * (C - 1) + 1);
        }
    }
    
    // 7. 最終出力
    vector<tuple<int, int, int, int>> doors;
    for (int i = 0; i < N - 1; ++i) {
        for (int j = 0; j < N; ++j) {
            if (best_door_h[i][j] != -1) doors.push_back({0, i, j, best_door_h[i][j]});
        }
    }
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N - 1; ++j) {
            if (best_door_v[i][j] != -1) doors.push_back({1, i, j, best_door_v[i][j]});
        }
    }
    cout << doors.size() << "\n";
    for (auto& d : doors) cout << get<0>(d) << " " << get<1>(d) << " " << get<2>(d) << " " << get<3>(d) << "\n";
    
    vector<tuple<int, int, int>> switches;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (best_switch_map[i][j] != -1) switches.push_back({i, j, best_switch_map[i][j]});
        }
    }
    cout << switches.size() << "\n";
    for (auto& s : switches) cout << get<0>(s) << " " << get<1>(s) << " " << get<2>(s) << "\n";
    
    return 0;
}