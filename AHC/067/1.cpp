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

        // 行動 1: 移動
        for (int dir = 0; dir < 4; ++dir) {
            int ni = i + dr[dir];
            int nj = j + dc[dir];

            if (ni < 0 || ni >= N || nj < 0 || nj >= N) continue;
            if (grid[ni][nj] == '#') continue;

            int g = -1;
            if (dir == 1) g = door_h[i][j];       // 下
            else if (dir == 0) g = door_h[ni][nj]; // 上
            else if (dir == 3) g = door_v[i][j];   // 右
            else if (dir == 2) g = door_v[ni][nj]; // 左

            if (!is_open(g, mask)) continue;

            if (dist[mask][ni][nj] == -1) {
                dist[mask][ni][nj] = d + 1;
                que.push({mask, ni, nj});
            }
        }

        // 行動 2: スイッチ
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
    
    pair<int,int> block_pos = {-1, -1};
    for(int i=0; i<N; ++i) {
        for(int j=0; j<N; ++j) {
            if(grid[i][j] == '#') {
                block_pos = {i, j};
                break;
            }
        }
        if(block_pos.first != -1) break;
    }
    
    int best_score = -1;
    vector<vector<int>> best_door_h, best_door_v, best_switch_map;
    mt19937 rng(42);
    
    int loop_cnt = 0;
    while (true) {
        if ((loop_cnt & 31) == 0) {
            auto now = steady_clock::now();
            if (duration_cast<duration<double>>(now - start_time).count() > 1.90) break;
        }
        loop_cnt++;
        
        // 1. ランダムDFSで全域木を作成 (ゴールは必ず葉にする)
        vector<vector<bool>> visited(N, vector<bool>(N, false));
        vector<pair<int, int>> tree_edges;
        vector<int> parent(N * N, -1);
        
        auto dfs = [&](auto& self, int r, int c, int p_id) -> void {
            visited[r][c] = true;
            parent[to_id(r, c)] = p_id;
            
            vector<int> dirs = {0, 1, 2, 3};
            shuffle(dirs.begin(), dirs.end(), rng);
            
            int dr[] = {-1, 1, 0, 0};
            int dc[] = {0, 0, -1, 1};
            for (int d : dirs) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr >= 0 && nr < N && nc >= 0 && nc < N && grid[nr][nc] == '.' && !visited[nr][nc]) {
                    tree_edges.push_back({to_id(r, c), to_id(nr, nc)});
                    if (nr == N - 1 && nc == N - 1) {
                        visited[nr][nc] = true;
                        parent[to_id(nr, nc)] = to_id(r, c);
                        continue; // ゴールから先は探索しない
                    }
                    self(self, nr, nc, to_id(r, c));
                }
            }
        };
        dfs(dfs, 0, 0, -1);
        
        // 2. 木に含まれない不要辺(閉路を作る辺)を収集
        vector<pair<int, int>> e_out;
        set<pair<int,int>> tree_edge_set;
        for(auto& e : tree_edges) tree_edge_set.insert({min(e.first, e.second), max(e.first, e.second)});
        
        for(int i=0; i<N; ++i) {
            for(int j=0; j<N; ++j) {
                if(grid[i][j] != '.') continue;
                int u = to_id(i, j);
                if(i+1 < N && grid[i+1][j] == '.') {
                    int v = to_id(i+1, j);
                    if(!tree_edge_set.count({min(u,v), max(u,v)})) e_out.push_back({u, v});
                }
                if(j+1 < N && grid[i][j+1] == '.') {
                    int v = to_id(i, j+1);
                    if(!tree_edge_set.count({min(u,v), max(u,v)})) e_out.push_back({u, v});
                }
            }
        }
        
        // 3. ギミックのサイズをランダムに決定
        int c_size = uniform_int_distribution<int>(3, 9)(rng);
        
        vector<int> deg(N*N, 0);
        for(auto& e : tree_edges) { deg[e.first]++; deg[e.second]++; }
        vector<int> leaves;
        for(int i=0; i<N; ++i) {
            for(int j=0; j<N; ++j) {
                if(grid[i][j] == '.') {
                    int u = to_id(i, j);
                    if(u == 0 || u == N*N-1) continue;
                    if(deg[u] == 1) leaves.push_back(u); // 葉ノードの収集
                }
            }
        }
        
        if (leaves.size() < c_size) continue;
        
        // 4. 木上の最短距離を計算して最適な訪問順序を探る
        vector<vector<int>> adj(N*N);
        for(auto& e : tree_edges) {
            adj[e.first].push_back(e.second);
            adj[e.second].push_back(e.first);
        }
        
        auto get_dist = [&](int start) {
            vector<int> d(N*N, -1);
            queue<int> q; q.push(start); d[start] = 0;
            while(!q.empty()) {
                int u = q.front(); q.pop();
                for(int v : adj[u]) {
                    if(d[v] == -1) { d[v] = d[u] + 1; q.push(v); }
                }
            }
            return d;
        };
        
        vector<vector<int>> distT(N*N);
        vector<int> targets = leaves;
        targets.push_back(0); targets.push_back(N*N-1);
        for(int t : targets) distT[t] = get_dist(t);
        
        int T_approx_max = -1;
        vector<int> best_path;
        
        for(int iter=0; iter<50; ++iter) {
            vector<int> path;
            vector<int> cand = leaves;
            shuffle(cand.begin(), cand.end(), rng);
            for(int i=0; i<c_size; ++i) path.push_back(cand[i]);
            
            int L = distT[0][path[0]];
            for(int i=0; i<c_size-1; ++i) L += distT[path[i]][path[i+1]];
            L += distT[path[c_size-1]][N*N-1];
            
            if (L > T_approx_max) {
                T_approx_max = L;
                best_path = path;
            }
        }
        
        // 5. 盤面へのギミックの配置
        vector<vector<int>> door_h(N, vector<int>(N, -1));
        vector<vector<int>> door_v(N, vector<int>(N, -1));
        vector<vector<int>> switch_map(N, vector<int>(N, -1));
        
        if (block_pos.first != -1) switch_map[block_pos.first][block_pos.second] = 9;
        
        shuffle(e_out.begin(), e_out.end(), rng);
        int block_cnt = min((int)e_out.size(), 50 - c_size);
        for(int i=0; i<block_cnt; ++i) { // 不要辺の封鎖
            int u = e_out[i].first, v = e_out[i].second;
            int ur = u / N, uc = u % N, vr = v / N, vc = v % N;
            if (ur == vr) door_v[ur][min(uc, vc)] = 19;
            else door_h[min(ur, vr)][uc] = 19;
        }
        
        auto place_door = [&](int u, int g) {
            int p = parent[u];
            if (p == -1) return;
            int ur = u / N, uc = u % N, pr = p / N, pc = p % N;
            if (ur == pr) door_v[ur][min(uc, pc)] = g;
            else door_h[min(ur, pr)][uc] = g;
        };
        
        for(int i=0; i<c_size; ++i) {
            int u = best_path[i];
            auto [ur, uc] = to_pos(u);
            switch_map[ur][uc] = i;
            if (i > 0) place_door(u, 2 * (i - 1) + 1); // 次のスイッチの前に扉
        }
        place_door(N*N-1, 2 * (c_size - 1) + 1); // ゴールの前に最後の扉
        
        // 6. 評価
        int T = calc_T(door_h, door_v, switch_map);
        if (T > best_score) {
            best_score = T;
            best_door_h = door_h;
            best_door_v = door_v;
            best_switch_map = switch_map;
        }
    }
    
    // 7. 出力整形
    vector<tuple<int, int, int, int>> doors;
    for(int i=0; i<N-1; ++i) {
        for(int j=0; j<N; ++j) {
            if(best_door_h[i][j] != -1) doors.push_back({0, i, j, best_door_h[i][j]});
        }
    }
    for(int i=0; i<N; ++i) {
        for(int j=0; j<N-1; ++j) {
            if(best_door_v[i][j] != -1) doors.push_back({1, i, j, best_door_v[i][j]});
        }
    }
    cout << doors.size() << "\n";
    for(auto& d : doors) cout << get<0>(d) << " " << get<1>(d) << " " << get<2>(d) << " " << get<3>(d) << "\n";
    
    vector<tuple<int, int, int>> switches;
    for(int i=0; i<N; ++i) {
        for(int j=0; j<N; ++j) {
            if(best_switch_map[i][j] != -1) switches.push_back({i, j, best_switch_map[i][j]});
        }
    }
    cout << switches.size() << "\n";
    for(auto& s : switches) cout << get<0>(s) << " " << get<1>(s) << " " << get<2>(s) << "\n";
    
    return 0;
}