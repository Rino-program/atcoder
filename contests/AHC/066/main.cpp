#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <random>
#include <chrono>
#include <unordered_set>

using namespace std;

const int dr[] = {0, 1, 0, -1};
const int dc[] = {1, 0, -1, 0};

struct State { int r, c, d; };
struct Point { int r, c; };

int N, M, T_limit;
vector<string> V_walls;
vector<string> H_walls;
vector<Point> locations;
vector<vector<int>> location_id;

pair<int, int> memo_dist[100][4][100];
string memo_path[100][4][100];

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

void bfs_all_targets(int from_id, int start_d) {
    Point sp = locations[from_id];
    vector<vector<vector<int>>> dist(N, vector<vector<int>>(N, vector<int>(4, 1e9)));
    vector<vector<vector<pair<State, char>>>> prv(N, vector<vector<pair<State, char>>>(N, vector<pair<State, char>>(4)));
    
    queue<State> q;
    dist[sp.r][sp.c][start_d] = 0;
    q.push({sp.r, sp.c, start_d});
    
    while (!q.empty()) {
        State curr = q.front();
        q.pop();
        
        if (can_move(curr.r, curr.c, curr.d)) {
            int nr = curr.r + dr[curr.d];
            int nc = curr.c + dc[curr.d];
            if (dist[nr][nc][curr.d] > dist[curr.r][curr.c][curr.d] + 1) {
                dist[nr][nc][curr.d] = dist[curr.r][curr.c][curr.d] + 1;
                prv[nr][nc][curr.d] = {curr, 'F'};
                q.push({nr, nc, curr.d});
            }
        }
        int nd_r = (curr.d + 1) % 4;
        if (dist[curr.r][curr.c][nd_r] > dist[curr.r][curr.c][curr.d] + 1) {
            dist[curr.r][curr.c][nd_r] = dist[curr.r][curr.c][curr.d] + 1;
            prv[curr.r][curr.c][nd_r] = {curr, 'R'};
            q.push({curr.r, curr.c, nd_r});
        }
        int nd_l = (curr.d + 3) % 4;
        if (dist[curr.r][curr.c][nd_l] > dist[curr.r][curr.c][curr.d] + 1) {
            dist[curr.r][curr.c][nd_l] = dist[curr.r][curr.c][curr.d] + 1;
            prv[curr.r][curr.c][nd_l] = {curr, 'L'};
            q.push({curr.r, curr.c, nd_l});
        }
    }
    
    for (int to_id = 0; to_id < (int)locations.size(); ++to_id) {
        Point tp = locations[to_id];
        int min_cost = 1e9;
        int best_d = -1;
        for (int d = 0; d < 4; ++d) {
            if (dist[tp.r][tp.c][d] < min_cost) {
                min_cost = dist[tp.r][tp.c][d];
                best_d = d;
            }
        }
        memo_dist[from_id][start_d][to_id] = {min_cost, best_d};
        if (min_cost < 1e9) {
            string ops = "";
            int cr = tp.r, cc = tp.c, cd = best_d;
            while (cr != sp.r || cc != sp.c || cd != start_d) {
                auto p = prv[cr][cc][cd];
                ops += p.second;
                cr = p.first.r; cc = p.first.c; cd = p.first.d;
            }
            reverse(ops.begin(), ops.end());
            memo_path[from_id][start_d][to_id] = ops;
        }
    }
}

struct RobotState {
    int loc_id;
    int dir;
    int r;
    int c;
};

struct TargetChoice {
    int kind;   // 0: カゴへ直行, 1: ボールを拾う/スワップする
    int ball;
    int loc_id;
    long long score;
};

int basket_loc(int ball_idx) {
    return 1 + M + ball_idx;
}

bool is_valid_interrupt_location(int loc_id, const vector<int>& occupant_at_loc) {
    return loc_id >= 0 && loc_id < (int)occupant_at_loc.size() && occupant_at_loc[loc_id] != -1;
}

// 🌟 利益・不利益の計算と、寄り道制限を組み込んだターゲット選択
TargetChoice choose_next_target(
    const RobotState& st,
    int held_ball,
    const vector<int>& ball_pos,
    const vector<char>& delivered,
    const vector<int>& occupant_at_loc,
    int last_dropped_ball
) {
    const long long INF = (1LL << 60);
    TargetChoice best{0, -1, -1, INF};

    auto get_min_dist = [](int u, int v) {
        if (u == v) return 0;
        int mn = 1e9;
        for (int d = 0; d < 4; ++d) mn = min(mn, memo_dist[u][d][v].first);
        return mn;
    };

    // ----------------------------------------------------
    // 【空手の場合】メインのボールBを探しつつ、進路上のCも評価
    // ----------------------------------------------------
    if (held_ball == -1) {
        for (int i = 0; i < M; ++i) {
            if (delivered[i] || ball_pos[i] == -1) continue;
            int src = ball_pos[i]; // メインターゲット（ボールB）
            int dst = basket_loc(i);
            
            auto p1 = memo_dist[st.loc_id][st.dir][src];
            auto p2 = memo_dist[src][p1.second][dst];
            
            // ボールBに直行して届ける純粋なコスト
            long long direct_cost = (long long)p1.first + p2.first + 2;
            
            if (direct_cost < best.score) {
                best = {1, i, src, direct_cost};
            }

            // ついでにボールC（j）を運べるかチェック
            for (int j = 0; j < M; ++j) {
                if (i == j || delivered[j] || ball_pos[j] == -1) continue;
                if (j == last_dropped_ball) continue; 
                
                int y_src = ball_pos[j]; // ついでターゲット（ボールC）
                auto p_curr_y = memo_dist[st.loc_id][st.dir][y_src];
                auto p_y_x = memo_dist[y_src][p_curr_y.second][src];
                auto p_x_bx = memo_dist[src][p_y_x.second][dst];
                
                // 🌟 修正ポイント1: 「寄り道歩数」を計算
                // Cを経由することで、Bに直行するより何歩余分にかかるか？
                int detour = p_curr_y.first + p_y_x.first - p1.first;
                
                // 寄り道が3歩以上になるなら、それは「ついで」ではなく「取りに行っている」ので無視
                if (detour > 2) continue;
                
                // CをBの場所まで運ぶことで、C自身がカゴに近づく歩数
                int benefit = get_min_dist(y_src, basket_loc(j)) - get_min_dist(src, basket_loc(j));
                
                // 🌟 修正ポイント2: Cがカゴから遠ざかる（または変わらない）なら運ばない
                if (benefit <= 0) continue;

                long long sequence_cost = (long long)p_curr_y.first + p_y_x.first + p_x_bx.first + 3;
                long long eval_score = sequence_cost - benefit; 
                
                if (eval_score < best.score) {
                    best = {1, j, y_src, eval_score};
                }
            }
        }
        return best;
    }

    // ----------------------------------------------------
    // 【ボールを持っている場合】そのままカゴに入れるか、スワップするか
    // ----------------------------------------------------
    int dst = basket_loc(held_ball);
    best = {0, held_ball, dst, (long long)memo_dist[st.loc_id][st.dir][dst].first + 1};

    for (int i = 0; i < M; ++i) {
        if (i == held_ball || delivered[i] || ball_pos[i] == -1) continue;
        if (i == last_dropped_ball) continue; 
        
        int x_src = ball_pos[i];
        auto p_curr_x = memo_dist[st.loc_id][st.dir][x_src];
        auto p_x_bx = memo_dist[x_src][p_curr_x.second][basket_loc(i)];
        
        // 今持っているボール（C）を、次のボール（B）の場所でスワップした場合の利益
        int benefit = get_min_dist(st.loc_id, basket_loc(held_ball)) - get_min_dist(x_src, basket_loc(held_ball));
        
        // 🌟 修正ポイント3: 今持っているボールがカゴから遠ざかるような無駄なスワップは絶対にしない
        if (benefit <= 0) continue;

        long long sequence_cost = (long long)p_curr_x.first + p_x_bx.first + 2; 
        long long eval_score = sequence_cost - benefit;
        
        if (eval_score < best.score) {
            best = {1, i, x_src, eval_score};
        }
    }

    return best;
}

bool move_towards(
    const TargetChoice& target,
    RobotState& st,
    string& ops,
    const vector<int>& occupant_at_loc,
    bool stop_on_intermediate_ball
) {
    const string& path = memo_path[st.loc_id][st.dir][target.loc_id];
    int r = st.r;
    int c = st.c;
    int d = st.dir;

    for (char ch : path) {
        if ((int)ops.size() >= T_limit) return false;
        ops += ch;
        if (ch == 'F') {
            r += dr[d];
            c += dc[d];
        } else if (ch == 'R') {
            d = (d + 1) % 4;
        } else if (ch == 'L') {
            d = (d + 3) % 4;
        }

        int nid = location_id[r][c];
        if (stop_on_intermediate_ball && nid != -1 && nid != target.loc_id && is_valid_interrupt_location(nid, occupant_at_loc)) {
            st = {nid, d, r, c};
            return false;
        }
    }

    st = {target.loc_id, d, locations[target.loc_id].r, locations[target.loc_id].c};
    return true;
}

string compress(const string& s) {
    if (s.length() <= 3) return s;

    int best_profit = 0;
    string best_T = "";
    vector<int> best_positions;

    int n = s.length();
    int max_len = min(n / 2, 50);
    unordered_set<string> evaluated;

    for (int len = 4; len <= max_len; ++len) {
        evaluated.clear();
        for (int i = 0; i <= n - len; ++i) {
            string T = s.substr(i, len);
            
            if (evaluated.count(T)) continue;
            evaluated.insert(T);

            vector<int> pos;
            int curr = i;
            while (curr <= n - len) {
                if (s.compare(curr, len, T) == 0) {
                    pos.push_back(curr);
                    curr += len;
                } else {
                    curr++;
                }
            }

            int profit = (int)pos.size() * len - (len + 2 + (int)pos.size() - 1);
            if (profit > best_profit) {
                best_profit = profit;
                best_T = T;
                best_positions = pos;
            }
        }
    }

    if (best_profit <= 0) return s;

    string prefix = s.substr(0, best_positions[0]);
    int last_idx = best_positions.back() + best_T.length();
    string suffix = s.substr(last_idx);

    string result = compress(prefix);
    
    result += "M" + best_T + "M"; 
    int curr = best_positions[0] + best_T.length();
    for (size_t i = 1; i < best_positions.size(); ++i) {
        result += s.substr(curr, best_positions[i] - curr);
        result += "P"; 
        curr = best_positions[i] + best_T.length();
    }
    
    result += compress(suffix);
    
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N >> M >> T_limit)) return 0;
    V_walls.resize(N);
    for (int i = 0; i < N; ++i) cin >> V_walls[i];
    H_walls.resize(N - 1);
    for (int i = 0; i < N - 1; ++i) cin >> H_walls[i];
    
    locations.push_back({0, 0});
    vector<Point> balls(M), baskets(M);
    for (int i = 0; i < M; ++i) {
        cin >> balls[i].r >> balls[i].c >> baskets[i].r >> baskets[i].c;
        locations.push_back(balls[i]);
    }
    for (int i = 0; i < M; ++i) {
        locations.push_back(baskets[i]);
    }

    location_id.assign(N, vector<int>(N, -1));
    for (int id = 0; id < (int)locations.size(); ++id) {
        location_id[locations[id].r][locations[id].c] = id;
    }
    
    for (int id = 0; id < (int)locations.size(); ++id) {
        for (int d = 0; d < 4; ++d) {
            bfs_all_targets(id, d);
        }
    }

    vector<int> ball_pos(M);
    vector<char> delivered(M, false);
    vector<int> occupant_at_loc(locations.size(), -1);
    for (int i = 0; i < M; ++i) {
        int loc = 1 + i;
        ball_pos[i] = loc;
        occupant_at_loc[loc] = i;
    }

    RobotState st{0, 0, 0, 0};
    int held_ball = -1;
    int delivered_cnt = 0;
    int last_dropped_ball = -1; // 🌟 ここで直前のボールを追跡

    string raw_ops = "";
    while (delivered_cnt < M && (int)raw_ops.size() < T_limit) {
        TargetChoice target = choose_next_target(st, held_ball, ball_pos, delivered, occupant_at_loc, last_dropped_ball);
        if (target.loc_id < 0) break;

        bool reached_target = move_towards(target, st, raw_ops, occupant_at_loc, true);
        if (!reached_target) {
            continue;
        }

        if ((int)raw_ops.size() >= T_limit) break;
        raw_ops += 'S';

        // 🌟 スワップ結果に応じて last_dropped_ball を更新
        if (target.kind == 0) {
            delivered[held_ball] = true;
            ball_pos[held_ball] = target.loc_id;
            occupant_at_loc[target.loc_id] = -1;
            last_dropped_ball = held_ball; // 置いたボールを記録
            held_ball = -1;
            ++delivered_cnt;
        } else {
            int next_ball = target.ball;
            if (held_ball == -1) {
                held_ball = next_ball;
                ball_pos[next_ball] = -1;
                occupant_at_loc[target.loc_id] = -1;
                last_dropped_ball = -1; // 拾っただけなので置いたボールはなし
            } else {
                int prev_ball = held_ball;
                ball_pos[prev_ball] = target.loc_id;
                occupant_at_loc[target.loc_id] = prev_ball;
                held_ball = next_ball;
                ball_pos[next_ball] = -1;
                last_dropped_ball = prev_ball; // スワップして床に置かれたボールを記録
            }
        }
    }
    
    string compressed_ops = compress(raw_ops);
    if (compressed_ops.size() > (size_t)T_limit || compressed_ops.size() >= raw_ops.size()) {
        compressed_ops = raw_ops;
    }
    
    for (char c : compressed_ops) {
        cout << c << "\n";
    }
    
    return 0;
}