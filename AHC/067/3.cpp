#include <bits/stdc++.h>
using namespace std;
using namespace std::chrono;

int N = 20, M = 50, K = 10;
vector<string> grid;

int to_id(int i, int j) { return i * N + j; }

// BFSによるシミュレータ（スコア計算）
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

    int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};

    while (!que.empty()) {
        auto [mask, i, j] = que.front();
        que.pop();
        int d = dist[mask][i][j];

        if (i == N - 1 && j == N - 1) return d;

        for (int dir = 0; dir < 4; ++dir) {
            int ni = i + dr[dir], nj = j + dc[dir];
            if (ni < 0 || ni >= N || nj < 0 || nj >= N || grid[ni][nj] == '#') continue;

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

struct Branch {
    int spine_idx;
    int leaf_id;
    int length;
};

struct EvalResult {
    long long proxy_score;
    int B;
    int best_K;
    int S;
    vector<int> spine;
    vector<Branch> selected_branches;
    vector<pair<int, int>> dangerous_back_edges;
    vector<int> parent;
};

// 木構造を評価し、Proxy Scoreを返す
EvalResult evaluate_tree(const vector<vector<int>>& tree_adj, const vector<pair<int, int>>& non_tree_edges) {
    EvalResult res;
    vector<int> parent(N * N, -1);
    queue<int> q;
    q.push(0);
    parent[0] = 0;
    
    // 1. BFSで親ポインタを構築
    while (!q.empty()) {
        int curr = q.front(); q.pop();
        for (int nxt : tree_adj[curr]) {
            if (parent[nxt] == -1) {
                parent[nxt] = curr;
                q.push(nxt);
            }
        }
    }
    
    int goal = N * N - 1;
    if (parent[goal] == -1) { res.proxy_score = -1e9; return res; } // ゴール未到達は弾く
    
    // 2. 背骨(Spine)の抽出
    vector<int> spine;
    int curr = goal;
    while (curr != 0) { spine.push_back(curr); curr = parent[curr]; }
    spine.push_back(0);
    reverse(spine.begin(), spine.end());
    vector<int> in_spine(N * N, -1);
    for (int i = 0; i < spine.size(); ++i) in_spine[spine[i]] = i;
    
    // 3. 枝(Branch)の探索
    vector<int> branch_id(N * N, -1);
    vector<Branch> branches;
    int b_id = 0;
    for (int i = 0; i < spine.size(); ++i) {
        int sp_node = spine[i];
        for (int nxt : tree_adj[sp_node]) {
            if (in_spine[nxt] != -1) continue;
            int deepest_node = nxt;
            int max_depth = 0;
            vector<int> q_branch;
            q_branch.push_back(nxt);
            branch_id[nxt] = b_id;
            vector<int> b_depth(N * N, 0);
            b_depth[nxt] = 1;
            int head = 0;
            while (head < q_branch.size()) {
                int c = q_branch[head++];
                if (b_depth[c] > max_depth) {
                    max_depth = b_depth[c];
                    deepest_node = c;
                }
                for (int nn : tree_adj[c]) {
                    if (nn == sp_node || branch_id[nn] == b_id) continue;
                    branch_id[nn] = b_id;
                    b_depth[nn] = b_depth[c] + 1;
                    q_branch.push_back(nn);
                }
            }
            branches.push_back({i, deepest_node, max_depth});
            b_id++;
        }
    }
    
    // 4. 危険な非木辺（迂回路）をカウント
    vector<pair<int, int>> dangerous_edges;
    for (auto& e : non_tree_edges) {
        int u = e.first, v = e.second;
        int su = in_spine[u], sv = in_spine[v];
        int bu = branch_id[u], bv = branch_id[v];
        bool dangerous = true;
        if (su == -1 && sv == -1 && bu == bv) dangerous = false; // 同じ枝内のループは安全
        if (dangerous) dangerous_edges.push_back(e);
    }
    
    res.B = dangerous_edges.size();
    res.dangerous_back_edges = dangerous_edges;
    
    // 5. 構築可能なハノイ段数 K を計算
    map<int, Branch> best_branch;
    for (auto& b : branches) {
        if (best_branch.find(b.spine_idx) == best_branch.end() || best_branch[b.spine_idx].length < b.length)
            best_branch[b.spine_idx] = b;
    }
    vector<Branch> available;
    for (auto& kv : best_branch) available.push_back(kv.second);
    sort(available.begin(), available.end(), [](const Branch& a, const Branch& b){ return a.length > b.length; });
    
    int S = spine.size() - 1;
    res.S = S;
    int best_K = 0;
    
    for (int cand_K = min(10, K); cand_K >= 1; --cand_K) {
        if (res.B > M) break; // 扉の数が足りない
        if (cand_K * (cand_K + 1) / 2 > M - res.B) continue;
        if (S < cand_K) continue;
        vector<Branch> valid_for_K;
        for (auto& b : available) if (b.spine_idx <= S - cand_K) valid_for_K.push_back(b);
        if (valid_for_K.size() < cand_K) continue;
        bool ok = true;
        for (int i = 0; i < cand_K; ++i) {
            if (valid_for_K[i].length < cand_K - 1 - i) ok = false;
        }
        if (ok) {
            best_K = cand_K;
            res.selected_branches.assign(valid_for_K.begin(), valid_for_K.begin() + cand_K);
            break;
        }
    }
    
    res.best_K = best_K;
    res.spine = spine;
    res.parent = parent;
    
    // Proxy Score の計算
    if (res.B > M) {
        res.proxy_score = -res.B * 10000; // 扉制限オーバーは強くペナルティ
    } else {
        long long sum_b = 0;
        for (int i = 0; i < min((int)available.size(), 10); ++i) sum_b += available[i].length;
        res.proxy_score = best_K * 1000000LL + S * 1000LL + sum_b - res.B * 10LL;
    }
    
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    auto start_time = steady_clock::now();
    if (!(cin >> N >> M >> K)) return 0;
    grid.resize(N);
    for (int i = 0; i < N; ++i) cin >> grid[i];
    
    mt19937 rng(42);
    int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    
    vector<vector<int>> tree_adj(N * N);
    vector<pair<int, int>> non_tree_edges;
    vector<pair<int, int>> all_grid_edges;
    
    // 初期状態の生成 (ランダムDFS)
    vector<bool> visited(N * N, false);
    auto dfs = [&](auto& self, int r, int c, int p_id) -> void {
        visited[to_id(r, c)] = true;
        vector<int> dirs = {0, 1, 2, 3};
        shuffle(dirs.begin(), dirs.end(), rng);
        for (int d : dirs) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N && grid[nr][nc] == '.') {
                int u = to_id(r, c), v = to_id(nr, nc);
                if (u < v) all_grid_edges.push_back({u, v});
                if (!visited[to_id(nr, nc)]) {
                    tree_adj[u].push_back(v);
                    tree_adj[v].push_back(u);
                    self(self, nr, nc, u);
                } else if (p_id != to_id(nr, nc) && u < v) {
                    non_tree_edges.push_back({u, v});
                }
            }
        }
    };
    dfs(dfs, 0, 0, -1);
    
    EvalResult current_state = evaluate_tree(tree_adj, non_tree_edges);
    long long absolute_best_proxy = current_state.proxy_score;
    
    int best_score = -1;
    vector<vector<int>> best_door_h(N, vector<int>(N, -1)), best_door_v(N, vector<int>(N, -1)), best_switch_map(N, vector<int>(N, -1));
    
    double temp_start = 100.0;
    double temp_end = 1.0;
    int iter = 0;
    
    // 焼きなまし法 (Simulated Annealing)
    while (true) {
        if ((iter & 63) == 0) {
            auto now = steady_clock::now();
            double elapsed = duration_cast<duration<double>>(now - start_time).count();
            if (elapsed > 1.90) break;
            double temp = temp_start * pow(temp_end / temp_start, elapsed / 1.90);
        }
        iter++;
        
        if (non_tree_edges.empty()) break;
        
        // 1. 追加する非木辺を選ぶ
        int add_idx = uniform_int_distribution<int>(0, non_tree_edges.size() - 1)(rng);
        auto [u, v] = non_tree_edges[add_idx];
        
        // 2. 木の閉路を見つける
        vector<int> path_parent(N * N, -1);
        queue<int> q;
        q.push(u);
        path_parent[u] = u;
        while (!q.empty()) {
            int curr = q.front(); q.pop();
            if (curr == v) break;
            for (int nxt : tree_adj[curr]) {
                if (path_parent[nxt] == -1) {
                    path_parent[nxt] = curr;
                    q.push(nxt);
                }
            }
        }
        
        vector<pair<int, int>> path_edges;
        int curr = v;
        while (curr != u) {
            int p = path_parent[curr];
            path_edges.push_back({min(curr, p), max(curr, p)});
            curr = p;
        }
        
        // 3. 削除する辺を選ぶ
        int rem_idx = uniform_int_distribution<int>(0, path_edges.size() - 1)(rng);
        auto [ru, rv] = path_edges[rem_idx];
        
        // 4. 状態の更新
        non_tree_edges[add_idx] = {ru, rv};
        tree_adj[ru].erase(find(tree_adj[ru].begin(), tree_adj[ru].end(), rv));
        tree_adj[rv].erase(find(tree_adj[rv].begin(), tree_adj[rv].end(), ru));
        tree_adj[u].push_back(v);
        tree_adj[v].push_back(u);
        
        EvalResult next_state = evaluate_tree(tree_adj, non_tree_edges);
        
        // 5. 遷移の受容判定
        bool accept = false;
        if (next_state.proxy_score >= current_state.proxy_score) accept = true;
        else {
            double diff = next_state.proxy_score - current_state.proxy_score;
            double temp = temp_start; // 簡易的な温度適用
            if (exp(diff / temp) > uniform_real_distribution<double>(0.0, 1.0)(rng)) accept = true;
        }
        
        if (accept) {
            current_state = next_state;
            
            // 過去最高Proxy Scoreを更新したら、実際のスコア（calc_T）を計算
            if (current_state.proxy_score > absolute_best_proxy && current_state.best_K > 0) {
                absolute_best_proxy = current_state.proxy_score;
                
                int c_K = current_state.best_K;
                vector<int> safe_perm(c_K);
                for (int i = 0; i < c_K; ++i) safe_perm[i] = c_K - 1 - i;
                vector<vector<int>> perms = {safe_perm};
                for (int trial = 0; trial < 3; ++trial) {
                    vector<int> p = safe_perm;
                    shuffle(p.begin(), p.end(), rng);
                    bool valid = true;
                    for (int i = 0; i < c_K; ++i) if (current_state.selected_branches[i].length < p[i]) valid = false;
                    if (valid) perms.push_back(p);
                }
                
                for (auto& perm : perms) {
                    vector<vector<int>> cur_door_h(N, vector<int>(N, -1)), cur_door_v(N, vector<int>(N, -1));
                    vector<vector<int>> cur_switch(N, vector<int>(N, -1));
                    
                    auto place_door = [&](int u_id, int v_id, int type) {
                        int ur = u_id / N, uc = u_id % N, vr = v_id / N, vc = v_id % N;
                        if (ur == vr) cur_door_v[ur][min(uc, vc)] = type;
                        else cur_door_h[min(ur, vr)][uc] = type;
                    };
                    
                    for (auto& e : current_state.dangerous_back_edges) place_door(e.first, e.second, 19);
                    
                    for (int i = 0; i < c_K; ++i) {
                        int sw_id = perm[i];
                        int curr_node = current_state.selected_branches[i].leaf_id;
                        vector<int> path;
                        while (curr_node != current_state.spine[current_state.selected_branches[i].spine_idx]) {
                            path.push_back(curr_node);
                            curr_node = current_state.parent[curr_node];
                        }
                        reverse(path.begin(), path.end());
                        cur_switch[current_state.selected_branches[i].leaf_id / N][current_state.selected_branches[i].leaf_id % N] = sw_id;
                        
                        for (int d = 0; d < sw_id; ++d) {
                            int req_S = sw_id - 1 - d;
                            int type = (req_S == sw_id - 1) ? (2 * req_S + 1) : (2 * req_S);
                            int u_id = (d == 0) ? current_state.spine[current_state.selected_branches[i].spine_idx] : path[d - 1];
                            place_door(u_id, path[d], type);
                        }
                    }
                    
                    for (int d = 0; d < c_K; ++d) {
                        int req_S = c_K - 1 - d;
                        int type = (req_S == c_K - 1) ? (2 * req_S + 1) : (2 * req_S);
                        int u_idx = current_state.S - c_K + d;
                        place_door(current_state.spine[u_idx], current_state.spine[u_idx + 1], type);
                    }
                    
                    int score = calc_T(cur_door_h, cur_door_v, cur_switch);
                    if (score > best_score) {
                        best_score = score;
                        best_door_h = cur_door_h; best_door_v = cur_door_v; best_switch_map = cur_switch;
                    }
                }
            }
        } else {
            // 遷移を棄却 (元に戻す)
            non_tree_edges[add_idx] = {u, v};
            tree_adj[u].erase(find(tree_adj[u].begin(), tree_adj[u].end(), v));
            tree_adj[v].erase(find(tree_adj[v].begin(), tree_adj[v].end(), u));
            tree_adj[ru].push_back(rv);
            tree_adj[rv].push_back(ru);
        }
    }
    
    // 結果出力
    vector<tuple<int, int, int, int>> doors;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (i < N - 1 && best_door_h[i][j] != -1) doors.push_back({0, i, j, best_door_h[i][j]});
            if (j < N - 1 && best_door_v[i][j] != -1) doors.push_back({1, i, j, best_door_v[i][j]});
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