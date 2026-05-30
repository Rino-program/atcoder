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
    int kind;   // 0: deliver held ball, 1: pick/swap a ball
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

TargetChoice choose_next_target(
    const RobotState& st,
    int held_ball,
    const vector<int>& ball_pos,
    const vector<char>& delivered,
    const vector<int>& occupant_at_loc
) {
    const long long INF = (1LL << 60);
    TargetChoice best{0, -1, -1, INF};

    if (held_ball == -1) {
        for (int i = 0; i < M; ++i) {
            if (delivered[i] || ball_pos[i] == -1) continue;
            int src = ball_pos[i];
            int dst = basket_loc(i);
            auto p1 = memo_dist[st.loc_id][st.dir][src];
            auto p2 = memo_dist[src][p1.second][dst];
            long long score = (long long)p1.first + 1 + p2.first + 1;
            if (score < best.score) {
                best = {1, i, src, score};
            }
        }
        return best;
    }

    int dst = basket_loc(held_ball);
    best = {0, held_ball, dst, (long long)memo_dist[st.loc_id][st.dir][dst].first + 1};

    for (int i = 0; i < M; ++i) {
        if (i == held_ball || delivered[i] || ball_pos[i] == -1) continue;
        int src = ball_pos[i];
        auto p1 = memo_dist[st.loc_id][st.dir][src];
        auto p2 = memo_dist[src][p1.second][basket_loc(i)];
        if (p1.first > 3 || p2.first > 3) continue;
        long long score = (long long)p1.first + 1 + p2.first + 1;
        if (score + 2 < best.score) {
            best = {1, i, src, score};
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

int evaluate_order(const vector<int>& order) {
    int total_cost = 0;
    int cur_id = 0; 
    int cur_d = 0;  
    for (int ball_idx : order) {
        int ball_id = 1 + ball_idx;
        int basket_id = 1 + M + ball_idx;
        auto p1 = memo_dist[cur_id][cur_d][ball_id];
        total_cost += p1.first + 1;
        cur_id = ball_id; cur_d = p1.second;
        
        auto p2 = memo_dist[cur_id][cur_d][basket_id];
        total_cost += p2.first + 1;
        cur_id = basket_id; cur_d = p2.second;
    }
    return total_cost;
}

// 🌟 ステップ3: マクロ圧縮関数
string compress(const string& s) {
    if (s.length() <= 3) return s;

    int best_profit = 0;
    string best_T = "";
    vector<int> best_positions;

    int n = s.length();
    // 探索するマクロの長さ (長すぎても効果が薄いため上限50)
    int max_len = min(n / 2, 50);
    unordered_set<string> evaluated;

    for (int len = 4; len <= max_len; ++len) {
        evaluated.clear();
        for (int i = 0; i <= n - len; ++i) {
            string T = s.substr(i, len);
            
            // 定数倍高速化: 同じ文字列の重複探索を防ぐ
            if (evaluated.count(T)) continue;
            evaluated.insert(T);

            vector<int> pos;
            int curr = i;
            // 互いに重ならない出現位置を探す
            while (curr <= n - len) {
                if (s.compare(curr, len, T) == 0) {
                    pos.push_back(curr);
                    curr += len;
                } else {
                    curr++;
                }
            }

            // 利益 = (元の文字数) - (圧縮後の文字数)
            // 圧縮後 = (初回 M + len + M) + (2回目以降 P(1文字) * (出現回数-1))
            int profit = (int)pos.size() * len - (len + 2 + (int)pos.size() - 1);
            if (profit > best_profit) {
                best_profit = profit;
                best_T = T;
                best_positions = pos;
            }
        }
    }

    // 圧縮しても文字数が減らないならそのまま返す
    if (best_profit <= 0) return s;

    // 前後の安全な領域を切り出す
    string prefix = s.substr(0, best_positions[0]);
    int last_idx = best_positions.back() + best_T.length();
    string suffix = s.substr(last_idx);

    // 前半を再帰的に圧縮
    string result = compress(prefix);
    
    // 中心部分（マクロ定義と使用）
    result += "M" + best_T + "M"; // 初回をマクロ登録
    int curr = best_positions[0] + best_T.length();
    for (size_t i = 1; i < best_positions.size(); ++i) {
        // マクロとマクロの間の「隙間の文字列」はそのまま追加
        result += s.substr(curr, best_positions[i] - curr);
        result += "P"; // マクロ呼び出し
        curr = best_positions[i] + best_T.length();
    }
    
    // 後半を再帰的に圧縮
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
    
    // 全点間最短経路の事前計算
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

    string raw_ops = "";
    while (delivered_cnt < M && (int)raw_ops.size() < T_limit) {
        TargetChoice target = choose_next_target(st, held_ball, ball_pos, delivered, occupant_at_loc);
        if (target.loc_id < 0) break;

        bool reached_target = move_towards(target, st, raw_ops, occupant_at_loc, true);
        if (!reached_target) {
            continue;
        }

        if ((int)raw_ops.size() >= T_limit) break;
        raw_ops += 'S';

        if (target.kind == 0) {
            delivered[held_ball] = true;
            ball_pos[held_ball] = target.loc_id;
            occupant_at_loc[target.loc_id] = -1;
            held_ball = -1;
            ++delivered_cnt;
        } else {
            int next_ball = target.ball;
            if (held_ball == -1) {
                held_ball = next_ball;
                ball_pos[next_ball] = -1;
                occupant_at_loc[target.loc_id] = -1;
            } else {
                int prev_ball = held_ball;
                ball_pos[prev_ball] = target.loc_id;
                occupant_at_loc[target.loc_id] = prev_ball;
                held_ball = next_ball;
                ball_pos[next_ball] = -1;
            }
        }
    }
    
    // マクロによる圧縮は、出力長が T_limit を超えない場合のみ採用する
    string compressed_ops = compress(raw_ops);
    if (compressed_ops.size() > (size_t)T_limit || compressed_ops.size() >= raw_ops.size()) {
        compressed_ops = raw_ops;
    }
    
    // 出力
    for (char c : compressed_ops) {
        cout << c << "\n";
    }
    
    return 0;
}