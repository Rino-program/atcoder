#pragma GCC optimize("O3,unroll-loops")
#pragma GCC target("avx2,bmi,bmi2,lzcnt,popcnt")

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <chrono>
#include <cmath>

using namespace std;

// === 定数およびグローバル変数 ===
constexpr int N = 20;
constexpr int N2 = 400;
int initial_board_arr[N][N];
vector<int> adj_all[N2];
int dist_all[N2][N2]; // dist_all[カードの最終位置][現在位置]
int wall_v[N][N];
int wall_h[N][N];
int sum_v[21][21];
int sum_h[21][21];

// キャッシュ効率を極限まで高めた操作構造体
struct MoveInfo {
    char dir;
    int r, c, h, w;
    int offset;
    int num_swaps;
};
vector<MoveInfo> valid_moves;
vector<int> swap_p1;
vector<int> swap_p2;

struct OutputMove {
    char dir;
    int r, c, h, w;
};

// === 乱数・時間計測 ===
inline uint32_t xor128() {
    static uint32_t x = 123456789, y = 362436069, z = 521288629, w = 88675123;
    uint32_t t = x ^ (x << 11);
    x = y; y = z; z = w;
    return w = (w ^ (w >> 19)) ^ (t ^ (t >> 8));
}

inline double get_time() {
    using namespace std::chrono;
    return duration_cast<duration<double>>(high_resolution_clock::now().time_since_epoch()).count();
}

// === 初期化処理 ===
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

    swap_p1.reserve(5000000);
    swap_p2.reserve(5000000);

    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            for (int h = 1; r + h <= N; ++h) {
                for (int w = 1; c + w <= N; ++w) {
                    if (h == 1 && w == 1) continue;
                    if (get_wall_v(r, r + h, c, c + w - 1) > 0) continue;
                    if (get_wall_h(r, r + h - 1, c, c + w) > 0) continue;
                    
                    if (h % 2 == 0) {
                        MoveInfo m;
                        m.dir = 'V'; m.r = r; m.c = c; m.h = h; m.w = w;
                        m.offset = swap_p1.size();
                        m.num_swaps = 0;
                        int half = h / 2;
                        for (int x = 0; x < half; ++x) {
                            for (int y = 0; y < w; ++y) {
                                swap_p1.push_back((r + x) * N + (c + y));
                                swap_p2.push_back((r + half + x) * N + (c + y));
                                m.num_swaps++;
                            }
                        }
                        valid_moves.push_back(m);
                    }
                    if (w % 2 == 0) {
                        MoveInfo m;
                        m.dir = 'H'; m.r = r; m.c = c; m.h = h; m.w = w;
                        m.offset = swap_p1.size();
                        m.num_swaps = 0;
                        int half = w / 2;
                        for (int x = 0; x < h; ++x) {
                            for (int y = 0; y < half; ++y) {
                                swap_p1.push_back((r + x) * N + (c + y));
                                swap_p2.push_back((r + x) * N + (c + half + y));
                                m.num_swaps++;
                            }
                        }
                        valid_moves.push_back(m);
                    }
                }
            }
        }
    }

    for (int v = 0; v < N2; ++v) {
        for (int p = 0; p < N2; ++p) dist_all[v][p] = 1e9;
        dist_all[v][v] = 0;
        queue<int> q;
        q.push(v);
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int nxt : adj_all[u]) {
                if (dist_all[v][nxt] == 1e9) {
                    dist_all[v][nxt] = dist_all[v][u] + 1;
                    q.push(nxt);
                }
            }
        }
    }
}

// === 高速な操作適用 & 距離差分計算 ===
inline int apply_move_and_diff(const MoveInfo& m, vector<int>& board, vector<int>& card_pos) {
    int diff = 0;
    const int end_idx = m.offset + m.num_swaps;
    const int* p1_ptr = &swap_p1[m.offset];
    const int* p2_ptr = &swap_p2[m.offset];
    
    for (int i = m.offset; i < end_idx; ++i) {
        int pos1 = *p1_ptr++;
        int pos2 = *p2_ptr++;
        int v1 = board[pos1];
        int v2 = board[pos2];
        
        const int* dist_v1 = dist_all[v1];
        const int* dist_v2 = dist_all[v2];
        
        diff -= dist_v1[pos1];
        diff -= dist_v2[pos2];
        diff += dist_v1[pos2];
        diff += dist_v2[pos1];
        
        board[pos1] = v2;
        board[pos2] = v1;
        card_pos[v1] = pos2;
        card_pos[v2] = pos1;
    }
    return diff;
}

// === フェーズ2用ユーティリティ ===
vector<int> bfs_path(int start, int goal, const vector<int> adj_U[]) {
    if (start == goal) return {start};
    vector<int> dist(N2, -1);
    vector<int> prev(N2, -1);
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

int timer_ap = 0;
vector<int> ord_ap, low_ap;
vector<bool> is_art;

void dfs_art(int u, int p, const vector<int> adj_U[]) {
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

// === メイン処理 ===
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
                int u = i * N + j;
                int v = i * N + j + 1;
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
                int u = i * N + j;
                int v = (i + 1) * N + j;
                adj_all[u].push_back(v);
                adj_all[v].push_back(u);
            }
        }
    }
    
    init();
    
    vector<int> current_board(N2);
    vector<int> current_pos(N2);
    int current_dist_sum = 0;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            int v = initial_board_arr[i][j];
            int p = i * N + j;
            current_board[p] = v;
            current_pos[v] = p;
            current_dist_sum += dist_all[v][p];
        }
    }
    
    vector<int> current_moves;
    current_moves.reserve(100000);
    double best_score = 1e9;
    vector<int> best_moves;
    vector<int> best_board(N2);
    vector<int> best_pos(N2);
    
    // TLEを防ぐため制限時間をやや厳し目に設定
    const double time_limit = 1.95; 
    int iter = 0;
    const double temp0 = 6.0;
    const double temp1 = 0.05;
    
    const int num_valid_moves = valid_moves.size();

    if (num_valid_moves == 0) {
        best_moves = current_moves;
        best_board = current_board;
        best_pos = current_pos;
    } else {
        while (true) {
            if ((iter & 1023) == 0) {
                double now = get_time();
                if (now - start_time > time_limit) break;
            }
            
            double now = get_time();
            double progress = (now - start_time) / time_limit;
            if (progress > 1.0) progress = 1.0;
            double temp = temp0 * pow(temp1 / temp0, progress);
            
            // 動的ペナルティ係数。終盤はより厳しく評価
            double current_C = 1.5 - 0.7 * progress;
            
            bool do_pop = (!current_moves.empty()) && ((xor128() % 2) == 0); 
            
            if (do_pop) {
                int m_idx = current_moves.back();
                const MoveInfo& m = valid_moves[m_idx];
                int diff = apply_move_and_diff(m, current_board, current_pos); // Undo
                double delta = -1.0 + current_C * diff;
                
                if (delta <= 0.0 || (double)(xor128() % 10000) / 10000.0 < exp(-delta / temp)) {
                    current_moves.pop_back();
                    current_dist_sum += diff;
                } else {
                    apply_move_and_diff(m, current_board, current_pos); // Redo
                }
            } else {
                int best_diff = 1e9;
                int best_idx = -1;
                // 進行度に応じて試行回数を増やし、終盤の無駄を省く
                int cand_size = 4 + (int)(3.0 * progress); 
                
                for (int c = 0; c < cand_size; ++c) {
                    int m_idx = xor128() % num_valid_moves;
                    const MoveInfo& m = valid_moves[m_idx];
                    int diff = apply_move_and_diff(m, current_board, current_pos);
                    if (diff < best_diff) {
                        best_diff = diff;
                        best_idx = m_idx;
                    }
                    apply_move_and_diff(m, current_board, current_pos); // 次候補へ（Undo）
                }
                
                const MoveInfo& m = valid_moves[best_idx];
                apply_move_and_diff(m, current_board, current_pos);
                double delta = 1.0 + current_C * best_diff;
                
                if (delta <= 0.0 || (double)(xor128() % 10000) / 10000.0 < exp(-delta / temp)) {
                    current_moves.push_back(best_idx);
                    current_dist_sum += best_diff;
                } else {
                    apply_move_and_diff(m, current_board, current_pos); // Undo
                }
            }
            
            double true_eval = current_moves.size() + 1.1 * current_dist_sum;
            if (true_eval < best_score) {
                best_score = true_eval;
                best_moves = current_moves;
                // コピーコストを下げるため、配列アクセスを使用
                std::copy(current_board.begin(), current_board.end(), best_board.begin());
                std::copy(current_pos.begin(), current_pos.end(), best_pos.begin());
            }
            iter++;
        }
    }
    
    // 【フェーズ2】
    vector<OutputMove> final_moves_out;
    final_moves_out.reserve(100000);
    for (int m_idx : best_moves) {
        const MoveInfo& mi = valid_moves[m_idx];
        final_moves_out.push_back({mi.dir, mi.r, mi.c, mi.h, mi.w});
    }
    vector<int> board = best_board;
    vector<int> pos = best_pos;
    
    vector<bool> is_fixed(N2, false);
    int un_fixed_cnt = N2; 
    
    while (un_fixed_cnt > 1) {
        vector<int> adj_U[N2];
        for (int i = 0; i < N2; ++i) {
            if (is_fixed[i]) continue;
            for (int nxt : adj_all[i]) {
                if (!is_fixed[nxt]) adj_U[i].push_back(nxt);
            }
        }
        
        timer_ap = 0;
        ord_ap.assign(N2, -1);
        low_ap.assign(N2, -1);
        is_art.assign(N2, false);
        int root = -1;
        for (int i = 0; i < N2; ++i) {
            if (!is_fixed[i]) { root = i; break; }
        }
        if (root != -1) dfs_art(root, -1, adj_U);
        
        vector<pair<int, int>> candidates; 
        for (int i = 0; i < N2; ++i) {
            if (!is_fixed[i] && !is_art[i]) {
                candidates.push_back({dist_all[i][pos[i]], i});
            }
        }
        sort(candidates.begin(), candidates.end());
        
        int best_v = -1;
        int best_d = 1e9;
        vector<int> best_path;
        int K = min((int)candidates.size(), 10);
        for (int i = 0; i < K; ++i) {
            int v = candidates[i].second;
            int p_v = pos[v];
            vector<int> path = bfs_path(p_v, v, adj_U);
            if (!path.empty() && path.size() < best_d) {
                best_d = path.size();
                best_v = v;
                best_path = std::move(path);
            }
        }
        
        if (best_v == -1 && !candidates.empty()) {
            best_v = candidates[0].second;
            best_path = {pos[best_v]}; 
        } else if (best_v == -1) {
            break;
        }
        
        for (size_t i = 0; i < best_path.size() - 1; ++i) {
            int u = best_path[i], w = best_path[i+1];
            int r1 = u / N, c1 = u % N;
            int r2 = w / N, c2 = w % N;
            OutputMove m;
            if (r1 == r2) { 
                m.dir = 'H'; m.r = r1; m.c = min(c1, c2); m.h = 1; m.w = 2;
            } else { 
                m.dir = 'V'; m.r = min(r1, r2); m.c = c1; m.h = 2; m.w = 1;
            }
            final_moves_out.push_back(m);
            
            int v1 = board[u], v2 = board[w];
            swap(board[u], board[w]);
            pos[v1] = w; pos[v2] = u;
        }
        
        is_fixed[best_v] = true;
        un_fixed_cnt--;
    }
    
    // 【出力】
    for (const OutputMove& m : final_moves_out) {
        cout << m.dir << " " << m.r << " " << m.c << " " << m.h << " " << m.w << "\n";
    }
    
    return 0;
}