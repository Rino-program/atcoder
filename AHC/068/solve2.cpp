#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <chrono>

using namespace std;

const int N = 20;
int initial_board_arr[N][N];
vector<vector<int>> adj_all(400);
int dist_all[400][400];
int wall_v[N][N];
int wall_h[N][N];
int sum_v[21][21];
int sum_h[21][21];

struct Move {
    char dir;
    int r, c, h, w;
};
vector<Move> valid_moves;

// 乱数生成器
uint32_t xor128() {
    static uint32_t x = 123456789, y = 362436069, z = 521288629, w = 88675123;
    uint32_t t = x ^ (x << 11);
    x = y; y = z; z = w;
    return w = (w ^ (w >> 19)) ^ (t ^ (t >> 8));
}

// 時間計測
double get_time() {
    using namespace std::chrono;
    return duration_cast<duration<double>>(high_resolution_clock::now().time_since_epoch()).count();
}

// 距離行列と壁・操作の前計算
void init() {
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            sum_v[i+1][j+1] = sum_v[i+1][j] + sum_v[i][j+1] - sum_v[i][j] + wall_v[i][j];
            sum_h[i+1][j+1] = sum_h[i+1][j] + sum_h[i][j+1] - sum_h[i][j] + wall_h[i][j];
        }
    }
    auto get_wall_v = [&](int r1, int r2, int c1, int c2) {
        if (r1 >= r2 || c1 >= c2) return 0;
        return sum_v[r2][c2] - sum_v[r1][c2] - sum_v[r2][c1] + sum_v[r1][c1];
    };
    auto get_wall_h = [&](int r1, int r2, int c1, int c2) {
        if (r1 >= r2 || c1 >= c2) return 0;
        return sum_h[r2][c2] - sum_h[r1][c2] - sum_h[r2][c1] + sum_h[r1][c1];
    };

    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            for (int h = 1; r + h <= N; ++h) {
                for (int w = 1; c + w <= N; ++w) {
                    if (h == 1 && w == 1) continue;
                    if (get_wall_v(r, r + h, c, c + w - 1) > 0) continue;
                    if (get_wall_h(r, r + h - 1, c, c + w) > 0) continue;
                    
                    if (h % 2 == 0) valid_moves.push_back({'V', r, c, h, w});
                    if (w % 2 == 0) valid_moves.push_back({'H', r, c, h, w});
                }
            }
        }
    }

    for (int i = 0; i < 400; ++i) {
        for (int j = 0; j < 400; ++j) dist_all[i][j] = 1e9;
        dist_all[i][i] = 0;
        queue<int> q;
        q.push(i);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : adj_all[u]) {
                if (dist_all[i][v] == 1e9) {
                    dist_all[i][v] = dist_all[i][u] + 1;
                    q.push(v);
                }
            }
        }
    }
}

// 操作適用時のスコア差分計算
int calc_diff(const Move& m, const vector<vector<int>>& board) {
    int diff = 0;
    auto eval = [&](int r, int c, int v) {
        int cur_p = r * 20 + c;
        int d = dist_all[cur_p][v];
        return d + (cur_p == v ? 0 : 2); // 完全一致ボーナス
    };
    if (m.dir == 'V') {
        int half = m.h / 2;
        for (int x = 0; x < half; ++x) {
            for (int y = 0; y < m.w; ++y) {
                int r1 = m.r + x, c1 = m.c + y;
                int r2 = m.r + half + x, c2 = m.c + y;
                int v1 = board[r1][c1], v2 = board[r2][c2];
                diff -= eval(r1, c1, v1); diff -= eval(r2, c2, v2);
                diff += eval(r1, c1, v2); diff += eval(r2, c2, v1);
            }
        }
    } else {
        int half = m.w / 2;
        for (int x = 0; x < m.h; ++x) {
            for (int y = 0; y < half; ++y) {
                int r1 = m.r + x, c1 = m.c + y;
                int r2 = m.r + x, c2 = m.c + half + y;
                int v1 = board[r1][c1], v2 = board[r2][c2];
                diff -= eval(r1, c1, v1); diff -= eval(r2, c2, v2);
                diff += eval(r1, c1, v2); diff += eval(r2, c2, v1);
            }
        }
    }
    return diff;
}

// 盤面上のカードスワップ操作
void apply_move(const Move& m, vector<vector<int>>& board, vector<int>& card_pos) {
    if (m.dir == 'V') {
        int half = m.h / 2;
        for (int x = 0; x < half; ++x) {
            for (int y = 0; y < m.w; ++y) {
                int r1 = m.r + x, c1 = m.c + y;
                int r2 = m.r + half + x, c2 = m.c + y;
                int v1 = board[r1][c1], v2 = board[r2][c2];
                swap(board[r1][c1], board[r2][c2]);
                card_pos[v1] = r2 * 20 + c2; card_pos[v2] = r1 * 20 + c1;
            }
        }
    } else {
        int half = m.w / 2;
        for (int x = 0; x < m.h; ++x) {
            for (int y = 0; y < half; ++y) {
                int r1 = m.r + x, c1 = m.c + y;
                int r2 = m.r + x, c2 = m.c + half + y;
                int v1 = board[r1][c1], v2 = board[r2][c2];
                swap(board[r1][c1], board[r2][c2]);
                card_pos[v1] = r2 * 20 + c2; card_pos[v2] = r1 * 20 + c1;
            }
        }
    }
}

// 局所的なBFS最短パス
vector<int> bfs_path(int start, int goal, const vector<vector<int>>& adj_U) {
    if (start == goal) return {start};
    vector<int> dist(400, -1);
    vector<int> prev(400, -1);
    queue<int> q;
    q.push(start);
    dist[start] = 0;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        if (u == goal) break;
        for (int nxt : adj_U[u]) {
            if (dist[nxt] == -1) {
                dist[nxt] = dist[u] + 1;
                prev[nxt] = u;
                q.push(nxt);
            }
        }
    }
    if (dist[goal] == -1) return {}; 
    vector<int> path;
    int curr = goal;
    while (curr != -1) {
        path.push_back(curr);
        curr = prev[curr];
    }
    reverse(path.begin(), path.end());
    return path;
}

// 関節点 (Articulation Point) 探索
int timer_ap = 0;
vector<int> ord_ap, low_ap;
vector<bool> is_art;
void dfs_art(int u, int p, const vector<vector<int>>& adj_U) {
    ord_ap[u] = low_ap[u] = timer_ap++;
    int child_cnt = 0;
    bool art = false;
    for (int v : adj_U[u]) {
        if (v == p) continue;
        if (ord_ap[v] != -1) {
            low_ap[u] = min(low_ap[u], ord_ap[v]);
        } else {
            child_cnt++;
            dfs_art(v, u, adj_U);
            low_ap[u] = min(low_ap[u], low_ap[v]);
            if (p != -1 && low_ap[v] >= ord_ap[u]) art = true;
        }
    }
    if (p == -1 && child_cnt > 1) art = true;
    if (art) is_art[u] = true;
}

// マルチスタート1回分のシミュレーション
vector<Move> playout(int max_climb_steps, int cand_size) {
    vector<vector<int>> cur_board(N, vector<int>(N));
    vector<int> cur_pos(400);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            cur_board[i][j] = initial_board_arr[i][j];
            cur_pos[initial_board_arr[i][j]] = i * 20 + j;
        }
    }
    
    vector<Move> history;
    int no_improve = 0;
    
    // 【フェーズ1】最良優先の山登り法
    if (!valid_moves.empty()) {
        for (int step = 0; step < max_climb_steps; ++step) {
            int best_diff = 1e9;
            Move best_m;
            for (int c = 0; c < cand_size; ++c) {
                int m_idx = xor128() % valid_moves.size();
                const Move& m = valid_moves[m_idx];
                int diff = calc_diff(m, cur_board);
                if (diff < best_diff) {
                    best_diff = diff;
                    best_m = m;
                }
            }
            if (best_diff < 0) {
                apply_move(best_m, cur_board, cur_pos);
                history.push_back(best_m);
                no_improve = 0;
            } else {
                no_improve++;
                if (no_improve > 20) break;
            }
        }
    }
    
    // 【フェーズ2】関節点を利用した確実なソート
    vector<bool> is_fixed(400, false);
    int un_fixed_cnt = 400;
    
    while (un_fixed_cnt > 1) {
        vector<vector<int>> adj_U(400);
        for (int i = 0; i < 400; ++i) {
            if (is_fixed[i]) continue;
            for (int nxt : adj_all[i]) {
                if (!is_fixed[nxt]) adj_U[i].push_back(nxt);
            }
        }
        
        timer_ap = 0;
        ord_ap.assign(400, -1);
        low_ap.assign(400, -1);
        is_art.assign(400, false);
        int root = -1;
        for (int i = 0; i < 400; ++i) {
            if (!is_fixed[i]) { root = i; break; }
        }
        if (root != -1) dfs_art(root, -1, adj_U);
        
        vector<pair<int, int>> candidates; 
        for (int i = 0; i < 400; ++i) {
            if (!is_fixed[i] && !is_art[i]) {
                candidates.push_back({dist_all[cur_pos[i]][i], i});
            }
        }
        sort(candidates.begin(), candidates.end());
        
        int best_v = -1;
        int best_d = 1e9;
        vector<int> best_path;
        int K = min((int)candidates.size(), 10);
        for (int i = 0; i < K; ++i) {
            int v = candidates[i].second;
            int p_v = cur_pos[v];
            vector<int> path = bfs_path(p_v, v, adj_U);
            if (!path.empty() && path.size() < best_d) {
                best_d = path.size();
                best_v = v;
                best_path = path;
            }
        }
        
        if (best_v == -1 && !candidates.empty()) {
            best_v = candidates[0].second;
            best_path = {cur_pos[best_v]}; 
        }
        
        for (int i = 0; i < (int)best_path.size() - 1; ++i) {
            int u = best_path[i], w = best_path[i+1];
            int r1 = u / 20, c1 = u % 20;
            int r2 = w / 20, c2 = w % 20;
            Move m;
            if (r1 == r2) { 
                m.dir = 'H'; m.r = r1; m.c = min(c1, c2); m.h = 1; m.w = 2;
            } else { 
                m.dir = 'V'; m.r = min(r1, r2); m.c = c1; m.h = 2; m.w = 1;
            }
            history.push_back(m);
            
            int v1 = cur_board[r1][c1], v2 = cur_board[r2][c2];
            swap(cur_board[r1][c1], cur_board[r2][c2]);
            cur_pos[v1] = r2 * 20 + c2; cur_pos[v2] = r1 * 20 + c1;
        }
        
        is_fixed[best_v] = true;
        un_fixed_cnt--;
    }
    
    return history;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    double start_time = get_time();
    int dummy_N;
    if (!(cin >> dummy_N)) return 0;
    
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            cin >> initial_board_arr[i][j];
        }
    }
    
    for (int i = 0; i < N; ++i) {
        string s; cin >> s;
        for (int j = 0; j < N - 1; ++j) {
            wall_v[i][j] = (s[j] == '1' ? 1 : 0);
            if (s[j] == '0') {
                int u = i * 20 + j;
                int v = i * 20 + j + 1;
                adj_all[u].push_back(v);
                adj_all[v].push_back(u);
            }
        }
    }
    for (int i = 0; i < N - 1; ++i) {
        string s; cin >> s;
        for (int j = 0; j < N; ++j) {
            wall_h[i][j] = (s[j] == '1' ? 1 : 0);
            if (s[j] == '0') {
                int u = i * 20 + j;
                int v = (i + 1) * 20 + j;
                adj_all[u].push_back(v);
                adj_all[v].push_back(u);
            }
        }
    }
    
    init();
    
    vector<Move> best_history;
    int best_T = 1e9;
    int playout_cnt = 0;
    
    // 実行時間制限2.0sに対して1.90秒までマルチスタートする
    double limit_time = 1.90; 
    
    while (true) {
        double now = get_time();
        if (now - start_time > limit_time) break;
        
        int max_climb = 1000 + (xor128() % 2000);
        int cand_size = 10 + (xor128() % 40);
        
        if (playout_cnt == 0) {
            max_climb = 0; // 最低1回は山登りなしのベースラインも確保する
        }
        
        vector<Move> hist = playout(max_climb, cand_size);
        if ((int)hist.size() < best_T) {
            best_T = hist.size();
            best_history = hist;
        }
        playout_cnt++;
    }
    
    for (const Move& m : best_history) {
        cout << m.dir << " " << m.r << " " << m.c << " " << m.h << " " << m.w << "\n";
    }
    
    return 0;
}