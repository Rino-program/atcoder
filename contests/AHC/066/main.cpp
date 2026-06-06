#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <chrono>
#include <random>
#include <cstring>
#include <string_view>

using namespace std;

// 終了時の遅延が完全に消滅したため、1.95まで攻められます
const double TIME_LIMIT = 1.95; 

const int dr[] = {0, 1, 0, -1};
const int dc[] = {1, 0, -1, 0};

int N, M, T_limit;
vector<string> V_walls;
vector<string> H_walls;

int dist_memo[400][4][400];
int end_dir_memo[400][4][400];
char prv_move[400][4][400][4]; 

int d_cost[20][20][4];
int d_turns[20][20][4];
int d_bonus[20][20][4];
bool is_poi[20][20];

bool can_move(int r, int c, int d) {
    int nr = r + dr[d];
    int nc = c + dc[d];
    if (nr < 0 || nr >= N || nc < 0 || nc >= N) return false;
    if (d == 0)      return V_walls[r][c] == '0';
    else if (d == 1) return H_walls[r][c] == '0';
    else if (d == 2) return V_walls[r][c-1] == '0';
    else if (d == 3) return H_walls[r-1][c] == '0';
    return false;
}

void precompute_paths() {
    struct State {
        int cost, turns, bonus, r, c, d;
        bool operator>(const State& o) const {
            if (cost != o.cost) return cost > o.cost;
            if (turns != o.turns) return turns > o.turns;
            return bonus < o.bonus;
        }
    };

    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            for (int d = 0; d < 4; ++d) {
                int start_id = r * N + c;
                for(int i=0; i<N; ++i) {
                    for(int j=0; j<N; ++j) {
                        d_cost[i][j][0] = d_cost[i][j][1] = d_cost[i][j][2] = d_cost[i][j][3] = 1e9;
                        d_turns[i][j][0] = d_turns[i][j][1] = d_turns[i][j][2] = d_turns[i][j][3] = 1e9;
                        d_bonus[i][j][0] = d_bonus[i][j][1] = d_bonus[i][j][2] = d_bonus[i][j][3] = -1;
                    }
                }

                priority_queue<State, vector<State>, greater<State>> pq;
                d_cost[r][c][d] = 0;
                d_turns[r][c][d] = 0;
                d_bonus[r][c][d] = is_poi[r][c] ? 1 : 0;
                pq.push({0, 0, d_bonus[r][c][d], r, c, d});

                while (!pq.empty()) {
                    auto curr = pq.top();
                    pq.pop();

                    if (curr.cost > d_cost[curr.r][curr.c][curr.d] || 
                       (curr.cost == d_cost[curr.r][curr.c][curr.d] && curr.turns > d_turns[curr.r][curr.c][curr.d]) ||
                       (curr.cost == d_cost[curr.r][curr.c][curr.d] && curr.turns == d_turns[curr.r][curr.c][curr.d] && curr.bonus < d_bonus[curr.r][curr.c][curr.d])) {
                        continue;
                    }

                    if (can_move(curr.r, curr.c, curr.d)) {
                        int nr = curr.r + dr[curr.d];
                        int nc = curr.c + dc[curr.d];
                        int next_bonus = curr.bonus + (is_poi[nr][nc] ? 1 : 0);
                        if (curr.cost + 1 < d_cost[nr][nc][curr.d] || 
                           (curr.cost + 1 == d_cost[nr][nc][curr.d] && curr.turns < d_turns[nr][nc][curr.d]) ||
                           (curr.cost + 1 == d_cost[nr][nc][curr.d] && curr.turns == d_turns[nr][nc][curr.d] && next_bonus > d_bonus[nr][nc][curr.d])) {
                            d_cost[nr][nc][curr.d] = curr.cost + 1;
                            d_turns[nr][nc][curr.d] = curr.turns;
                            d_bonus[nr][nc][curr.d] = next_bonus;
                            prv_move[start_id][d][nr * N + nc][curr.d] = 'F';
                            pq.push({curr.cost + 1, curr.turns, next_bonus, nr, nc, curr.d});
                        }
                    }

                    int nd_r = (curr.d + 1) % 4;
                    if (curr.cost + 1 < d_cost[curr.r][curr.c][nd_r] || 
                       (curr.cost + 1 == d_cost[curr.r][curr.c][nd_r] && curr.turns + 1 < d_turns[curr.r][curr.c][nd_r]) ||
                       (curr.cost + 1 == d_cost[curr.r][curr.c][nd_r] && curr.turns + 1 == d_turns[curr.r][curr.c][nd_r] && curr.bonus > d_bonus[curr.r][curr.c][nd_r])) {
                        d_cost[curr.r][curr.c][nd_r] = curr.cost + 1;
                        d_turns[curr.r][curr.c][nd_r] = curr.turns + 1;
                        d_bonus[curr.r][curr.c][nd_r] = curr.bonus;
                        prv_move[start_id][d][curr.r * N + curr.c][nd_r] = 'R';
                        pq.push({curr.cost + 1, curr.turns + 1, curr.bonus, curr.r, curr.c, nd_r});
                    }

                    int nd_l = (curr.d + 3) % 4;
                    if (curr.cost + 1 < d_cost[curr.r][curr.c][nd_l] || 
                       (curr.cost + 1 == d_cost[curr.r][curr.c][nd_l] && curr.turns + 1 < d_turns[curr.r][curr.c][nd_l]) ||
                       (curr.cost + 1 == d_cost[curr.r][curr.c][nd_l] && curr.turns + 1 == d_turns[curr.r][curr.c][nd_l] && curr.bonus > d_bonus[curr.r][curr.c][nd_l])) {
                        d_cost[curr.r][curr.c][nd_l] = curr.cost + 1;
                        d_turns[curr.r][curr.c][nd_l] = curr.turns + 1;
                        d_bonus[curr.r][curr.c][nd_l] = curr.bonus;
                        prv_move[start_id][d][curr.r * N + curr.c][nd_l] = 'L';
                        pq.push({curr.cost + 1, curr.turns + 1, curr.bonus, curr.r, curr.c, nd_l});
                    }
                }

                for (int tr = 0; tr < N; ++tr) {
                    for (int tc = 0; tc < N; ++tc) {
                        int end_id = tr * N + tc;
                        int min_c = 1e9, min_t = 1e9, max_b = -1, best_ed = 0;
                        for (int ed = 0; ed < 4; ++ed) {
                            if (d_cost[tr][tc][ed] < min_c || 
                               (d_cost[tr][tc][ed] == min_c && d_turns[tr][tc][ed] < min_t) ||
                               (d_cost[tr][tc][ed] == min_c && d_turns[tr][tc][ed] == min_t && d_bonus[tr][tc][ed] > max_b)) {
                                min_c = d_cost[tr][tc][ed];
                                min_t = d_turns[tr][tc][ed];
                                max_b = d_bonus[tr][tc][ed];
                                best_ed = ed;
                            }
                        }
                        dist_memo[start_id][d][end_id] = min_c;
                        end_dir_memo[start_id][d][end_id] = best_ed;
                    }
                }
            }
        }
    }
}

string get_path(int s_id, int s_d, int e_id, int& out_d) {
    string path = "";
    int curr_id = e_id;
    int curr_d = end_dir_memo[s_id][s_d][e_id];
    out_d = curr_d;

    while (curr_id != s_id || curr_d != s_d) {
        char move = prv_move[s_id][s_d][curr_id][curr_d];
        path += move;
        if (move == 'F') {
            int r = curr_id / N, c = curr_id % N;
            r -= dr[curr_d]; c -= dc[curr_d];
            curr_id = r * N + c;
        } else if (move == 'R') {
            curr_d = (curr_d + 3) % 4;
        } else if (move == 'L') {
            curr_d = (curr_d + 1) % 4;
        } else break;
    }
    reverse(path.begin(), path.end());
    return path;
}

// 【重要】文字列のメモリ確保を完全に排除した超高速経路探索
// ゴールからスタートへ逆順に辿るだけで距離を計測します
int find_best_drop(int start_l, int start_d, int goal_l, int target_basket) {
    int best_drop = goal_l;
    int min_dist = 1e9;
    for (int d = 0; d < 4; ++d) min_dist = min(min_dist, dist_memo[goal_l][d][target_basket]);
    
    int curr_l = goal_l;
    int curr_d = end_dir_memo[start_l][start_d][goal_l];
    
    while (curr_l != start_l || curr_d != start_d) {
        char move = prv_move[start_l][start_d][curr_l][curr_d];
        if (move == 'F') {
            int r = curr_l / N, c = curr_l % N;
            r -= dr[curr_d]; c -= dc[curr_d];
            curr_l = r * N + c;
        } else if (move == 'R') {
            curr_d = (curr_d + 3) % 4;
        } else if (move == 'L') {
            curr_d = (curr_d + 1) % 4;
        } else break;
        
        int dist = 1e9;
        for (int d = 0; d < 4; ++d) dist = min(dist, dist_memo[curr_l][d][target_basket]);
        
        if (dist < min_dist) {
            min_dist = dist;
            best_drop = curr_l;
        }
    }
    return best_drop;
}

long long simulate_and_evaluate(const vector<int>& order, const vector<int>& orig_balls, const vector<int>& orig_baskets, string* out_ops = nullptr) {
    long long total_cost = 0;
    int curr_l = 0, curr_d = 0;
    
    struct BState { int loc; bool delivered; };
    vector<BState> b_state(M);
    for(int i = 0; i < M; ++i) b_state[i] = {orig_balls[i], false};
    
    for(int i = 0; i < M; ++i) {
        int B = order[i];
        if (b_state[B].delivered) continue;
        
        int B_loc = b_state[B].loc;
        int B_basket = orig_baskets[B];
        int best_C = -1;
        int best_type = 0;
        int max_gain = 3;
        int current_best_drop = -1;
        
        for(int j = i + 1; j < M; ++j) {
            int C = order[j];
            if (b_state[C].delivered) continue;
            
            int C_loc = b_state[C].loc;
            int C_basket = orig_baskets[C];
            
            if (C_loc == B_loc) continue;
            
            int direct_B = dist_memo[curr_l][curr_d][B_loc];
            
            int cost_via_C1 = dist_memo[curr_l][curr_d][C_loc] + 1;
            int dir_after_C1 = end_dir_memo[curr_l][curr_d][C_loc];
            cost_via_C1 += dist_memo[C_loc][dir_after_C1][B_loc];
            int extra_cost1 = cost_via_C1 - direct_B;
            
            int old_C_dist = 1e9;
            for(int d = 0; d < 4; ++d) old_C_dist = min(old_C_dist, dist_memo[C_loc][d][C_basket]);
            
            int optimal_drop_loc = find_best_drop(C_loc, dir_after_C1, B_loc, C_basket);
            
            int new_C_dist = 1e9;
            for(int d = 0; d < 4; ++d) new_C_dist = min(new_C_dist, dist_memo[optimal_drop_loc][d][C_basket]);
            
            int drop_cost_inc = (optimal_drop_loc != B_loc) ? 1 : 0;
            int gain1 = (old_C_dist - new_C_dist) - (extra_cost1 + drop_cost_inc);
            
            if (gain1 > max_gain) {
                max_gain = gain1;
                best_C = C;
                best_type = 1;
                current_best_drop = optimal_drop_loc;
            }
            
            int cost_via_C2 = dist_memo[curr_l][curr_d][C_loc] + 1;
            int dir_after_C2 = end_dir_memo[curr_l][curr_d][C_loc];
            cost_via_C2 += dist_memo[C_loc][dir_after_C2][C_basket] + 1;
            int dir_after_basket = end_dir_memo[C_loc][dir_after_C2][C_basket];
            cost_via_C2 += dist_memo[C_basket][dir_after_basket][B_loc];
            int extra_cost2 = cost_via_C2 - direct_B;
            
            int gain2 = (old_C_dist + 2 + 12) - extra_cost2;
            if (gain2 > max_gain) {
                max_gain = gain2;
                best_C = C;
                best_type = 2;
                current_best_drop = -1; 
            }
        }
        
        if (best_C != -1) {
            int C = best_C;
            int C_loc = b_state[C].loc;
            int C_basket = orig_baskets[C];
            int next_d;
            
            if (best_type == 1) {
                if (out_ops) *out_ops += get_path(curr_l, curr_d, C_loc, next_d) + "S";
                total_cost += dist_memo[curr_l][curr_d][C_loc] + 1;
                curr_d = end_dir_memo[curr_l][curr_d][C_loc];
                curr_l = C_loc;
                
                if (current_best_drop != B_loc) {
                    if (out_ops) *out_ops += get_path(curr_l, curr_d, current_best_drop, next_d) + "S";
                    total_cost += dist_memo[curr_l][curr_d][current_best_drop] + 1;
                    curr_d = end_dir_memo[curr_l][curr_d][current_best_drop];
                    curr_l = current_best_drop;
                    b_state[C].loc = current_best_drop;
                    
                    if (out_ops) *out_ops += get_path(curr_l, curr_d, B_loc, next_d) + "S";
                    total_cost += dist_memo[curr_l][curr_d][B_loc] + 1;
                    curr_d = end_dir_memo[curr_l][curr_d][B_loc];
                    curr_l = B_loc;
                } else {
                    if (out_ops) *out_ops += get_path(curr_l, curr_d, B_loc, next_d) + "S";
                    total_cost += dist_memo[curr_l][curr_d][B_loc] + 1;
                    curr_d = end_dir_memo[curr_l][curr_d][B_loc];
                    curr_l = B_loc;
                    
                    if (B_loc == C_basket) b_state[C].delivered = true;
                    else b_state[C].loc = B_loc;
                }
                
            } else {
                if (out_ops) *out_ops += get_path(curr_l, curr_d, C_loc, next_d) + "S";
                total_cost += dist_memo[curr_l][curr_d][C_loc] + 1;
                curr_d = end_dir_memo[curr_l][curr_d][C_loc];
                curr_l = C_loc;
                
                if (out_ops) *out_ops += get_path(curr_l, curr_d, C_basket, next_d) + "S";
                total_cost += dist_memo[curr_l][curr_d][C_basket] + 1;
                curr_d = end_dir_memo[curr_l][curr_d][C_basket];
                curr_l = C_basket;
                
                b_state[C].delivered = true;
                
                if (out_ops) *out_ops += get_path(curr_l, curr_d, B_loc, next_d) + "S";
                total_cost += dist_memo[curr_l][curr_d][B_loc] + 1;
                curr_d = end_dir_memo[curr_l][curr_d][B_loc];
                curr_l = B_loc;
            }
        } else {
            int next_d;
            if (out_ops) *out_ops += get_path(curr_l, curr_d, B_loc, next_d) + "S";
            total_cost += dist_memo[curr_l][curr_d][B_loc] + 1;
            curr_d = end_dir_memo[curr_l][curr_d][B_loc];
            curr_l = B_loc;
        }

        int next_d;
        if (out_ops) *out_ops += get_path(curr_l, curr_d, B_basket, next_d) + "S";
        total_cost += dist_memo[curr_l][curr_d][B_basket] + 1;
        curr_d = end_dir_memo[curr_l][curr_d][B_basket];
        curr_l = B_basket;
        
        b_state[B].delivered = true;
        
        if (out_ops && out_ops->length() >= (size_t)T_limit) break;
    }
    
    return total_cost;
}

// 【重要】unordered_mapを排除し、ベクターのソートのみでマクロを探す超軽量処理
string compress_fast(const string& s) {
    int n = s.length();
    if (n <= 5) return s;
    
    int best_profit = 0;
    string best_sub = "";
    string_view sv(s);
    
    for (int len = 4; len <= min(n / 2, 50); ++len) {
        vector<string_view> subs;
        subs.reserve(n - len + 1);
        for (int i = 0; i <= n - len; ++i) {
            subs.push_back(sv.substr(i, len));
        }
        sort(subs.begin(), subs.end());
        
        for (size_t i = 0; i < subs.size(); ) {
            size_t j = i + 1;
            while (j < subs.size() && subs[j] == subs[i]) j++;
            if (j - i >= 2) {
                int occurrences = 0;
                string_view candidate = subs[i];
                for (int k = 0; k <= n - len; ) {
                    if (sv.substr(k, len) == candidate) {
                        occurrences++;
                        k += len;
                    } else {
                        k++;
                    }
                }
                int profit = occurrences * len - (len + 2 + occurrences);
                if (profit > best_profit) {
                    best_profit = profit;
                    best_sub = string(candidate);
                }
            }
            i = j;
        }
    }
    
    if (best_profit <= 0) return s;
    
    string res = "";
    bool first = false;
    for (int i = 0; i < n; ) {
        if (i <= n - (int)best_sub.length() && s.substr(i, best_sub.length()) == best_sub) {
            if (!first) {
                res += "M" + best_sub + "M";
                first = true;
            } else {
                res += "P";
            }
            i += best_sub.length();
        } else {
            res += s[i];
            i++;
        }
    }
    return res;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    auto start_time = chrono::high_resolution_clock::now();

    if (!(cin >> N >> M >> T_limit)) return 0;
    
    V_walls.resize(N);
    for (int i = 0; i < N; ++i) cin >> V_walls[i];
    H_walls.resize(N - 1);
    for (int i = 0; i < N - 1; ++i) cin >> H_walls[i];
    
    vector<int> balls(M), baskets(M);
    memset(is_poi, 0, sizeof(is_poi));
    
    for (int i = 0; i < M; ++i) {
        int br, bc, kr, kc;
        cin >> br >> bc >> kr >> kc;
        balls[i] = br * N + bc;
        baskets[i] = kr * N + kc;
        
        is_poi[br][bc] = true;
        is_poi[kr][kc] = true;
    }

    precompute_paths();

    vector<int> current_order(M);
    for (int i = 0; i < M; ++i) current_order[i] = i;
    
    int curr_l = 0, curr_d = 0;
    vector<bool> used(M, false);
    for (int i = 0; i < M; ++i) {
        int best_idx = -1;
        int min_cost = 1e9;
        for (int j = 0; j < M; ++j) {
            if (!used[j]) {
                int cost = dist_memo[curr_l][curr_d][balls[j]];
                if (cost < min_cost) {
                    min_cost = cost;
                    best_idx = j;
                }
            }
        }
        current_order[i] = best_idx;
        used[best_idx] = true;
        curr_d = end_dir_memo[curr_l][curr_d][balls[best_idx]];
        curr_l = balls[best_idx];
        curr_d = end_dir_memo[curr_l][curr_d][baskets[best_idx]];
        curr_l = baskets[best_idx];
    }

    long long current_score = simulate_and_evaluate(current_order, balls, baskets);
    vector<int> best_order = current_order;
    long long best_score = current_score;

    mt19937 rnd(42);
    double temp_start = 50.0;
    double temp_end = 0.1;
    int iter = 0;

    while (true) {
        if ((iter & 63) == 0) {
            auto current_time = chrono::high_resolution_clock::now();
            double elapsed = chrono::duration<double>(current_time - start_time).count();
            if (elapsed > TIME_LIMIT) break;
            
            double progress = elapsed / TIME_LIMIT;
            double temp = temp_start * pow(temp_end / temp_start, progress);

            vector<int> next_order = current_order;
            int type = rnd() % 2;
            if (type == 0) {
                int i = rnd() % M;
                int j = rnd() % M;
                swap(next_order[i], next_order[j]);
            } else {
                int i = rnd() % M;
                int j = rnd() % M;
                if (i > j) swap(i, j);
                reverse(next_order.begin() + i, next_order.begin() + j + 1);
            }

            long long next_score = simulate_and_evaluate(next_order, balls, baskets);
            double diff = next_score - current_score;

            if (diff < 0 || uniform_real_distribution<double>(0.0, 1.0)(rnd) < exp(-diff / temp)) {
                current_order = next_order;
                current_score = next_score;
                if (current_score < best_score) {
                    best_score = current_score;
                    best_order = current_order;
                }
            }
        }
        iter++;
    }

    string raw_ops = "";
    simulate_and_evaluate(best_order, balls, baskets, &raw_ops);

    string final_ops = compress_fast(raw_ops);
    
    if (final_ops.length() > (size_t)T_limit) {
        final_ops = final_ops.substr(0, T_limit);
    }

    cout << final_ops << "\n";

    return 0;
}