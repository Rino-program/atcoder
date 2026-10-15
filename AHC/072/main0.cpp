#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <deque>
#include <set>
#include <map>
#include <tuple>
#include <algorithm>
#include <random>

using namespace std;

// =========================================================================
// [TUNING PARAMETERS: 自動調整用パラメータ定義]
// =========================================================================
struct HyperParams {
    int max_ops = 99990;
    int phase2_max_merge_dist = 4;      // 寄り道を許容する最大床距離
    int combo_h_min = 5;               // 分割・踏み台コンボを検討する最小の高さ
    int combo_cost_min = 3;            // 分割・踏み台コンボを検討する最小直行手数
    int combo_cooldown_steps = 15;     // コンボ発動後の同マス利用禁止手数
    int height8_pending_steps = 10;    // 高さ8直行不能時の保留手数
    int recent_history_len = 6;        // 局所/大域でのピンポン防止履歴長
};

HyperParams PARAMS;

// =========================================================================
// [CONSTANTS & TYPES]
// =========================================================================
const int INF = 1e9;

struct Dir {
    char name;
    int dr;
    int dc;
};

const vector<Dir> DIRECTIONS = {
    {'U', -1, 0},
    {'R', 0, 1},
    {'D', 1, 0},
    {'L', 0, -1}
};

struct MoveCommand {
    int r, c, k;
    char d;
    int l;
};

// =========================================================================
// [MAIN SOLVER CLASS]
// =========================================================================
class Solver {
public:
    int N = 0;
    int K = 12;
    vector<string> grid;
    vector<vector<bool>> is_wall;
    vector<vector<int>> is_nest;
    map<int, pair<int, int>> nest_pos;
    vector<vector<vector<int>>> stacks;

    vector<vector<int>> top_color;
    vector<set<pair<int, int>>> slimes_by_color;

    // キャッシュ
    map<pair<int, int>, vector<vector<int>>> dist_map_cache;
    map<tuple<int, int, int>, vector<vector<int>>> jump_dist_cache;
    vector<vector<vector<int>>> nest_dist; // nest_dist[c][r][c_pos]

    vector<MoveCommand> ans;
    deque<pair<pair<int, int>, pair<int, int>>> global_recent_moves;

    mt19937 rng{42}; // 決定論的な乱数

    void read_input() {
        if (!(cin >> N >> K)) return;
        grid.resize(N);
        for (int i = 0; i < N; ++i) {
            cin >> grid[i];
        }

        is_wall.assign(N, vector<bool>(N, false));
        is_nest.assign(N, vector<int>(N, -1));
        stacks.assign(N, vector<vector<int>>(N));

        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                char ch = grid[r][c];
                if (ch == '#') {
                    is_wall[r][c] = true;
                } else if (ch >= 'a' && ch <= 'l') {
                    int color = ch - 'a';
                    stacks[r][c].push_back(color);
                } else if (ch >= 'A' && ch <= 'L') {
                    int color = ch - 'A';
                    is_nest[r][c] = color;
                    nest_pos[color] = {r, c};
                }
            }
        }

        if (!nest_pos.empty()) {
            int max_c = -1;
            for (auto& p : nest_pos) max_c = max(max_c, p.first);
            K = max(K, max_c + 1);
        }
    }

    void init() {
        top_color.assign(N, vector<int>(N, -1));
        slimes_by_color.resize(K);

        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                if (!stacks[r][c].empty()) {
                    int tc = stacks[r][c].back();
                    top_color[r][c] = tc;
                    slimes_by_color[tc].insert({r, c});
                }
            }
        }

        nest_dist.assign(K, vector<vector<int>>(N, vector<int>(N, INF)));
        for (int c = 0; c < K; ++c) {
            if (nest_pos.count(c)) {
                nest_dist[c] = get_dist_map(nest_pos[c]);
            }
        }
    }

    void update_cell(int r, int c) {
        int old_c = top_color[r][c];
        int new_c = stacks[r][c].empty() ? -1 : stacks[r][c].back();
        if (old_c == new_c) return;

        if (old_c != -1) {
            slimes_by_color[old_c].erase({r, c});
        }
        if (new_c != -1) {
            slimes_by_color[new_c].insert({r, c});
        }
        top_color[r][c] = new_c;
    }

    const vector<vector<int>>& get_dist_map(pair<int, int> pos) {
        if (dist_map_cache.count(pos)) {
            return dist_map_cache[pos];
        }
        vector<vector<int>> d_map(N, vector<int>(N, INF));
        d_map[pos.first][pos.second] = 0;
        queue<pair<int, int>> q;
        q.push(pos);

        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();
            for (auto& d : DIRECTIONS) {
                int nr = r + d.dr;
                int nc = c + d.dc;
                if (nr >= 0 && nr < N && nc >= 0 && nc < N && !is_wall[nr][nc]) {
                    if (d_map[nr][nc] == INF) {
                        d_map[nr][nc] = d_map[r][c] + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
        dist_map_cache[pos] = move(d_map);
        return dist_map_cache[pos];
    }

    const vector<vector<int>>& get_jump_dist(pair<int, int> target_coord, int max_len) {
        auto key = make_tuple(target_coord.first, target_coord.second, max_len);
        if (jump_dist_cache.count(key)) {
            return jump_dist_cache[key];
        }
        vector<vector<int>> j_dist(N, vector<int>(N, INF));
        j_dist[target_coord.first][target_coord.second] = 0;
        queue<pair<int, int>> q;
        q.push(target_coord);

        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();
            int d_cur = j_dist[r][c];

            for (auto& d : DIRECTIONS) {
                for (int l = 1; l <= max_len; ++l) {
                    int nr = r + d.dr * l;
                    int nc = c + d.dc * l;
                    if (!(nr >= 0 && nr < N && nc >= 0 && nc < N)) break;
                    if (is_wall[nr][nc]) break;

                    if (j_dist[nr][nc] == INF) {
                        j_dist[nr][nc] = d_cur + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
        jump_dist_cache[key] = move(j_dist);
        return jump_dist_cache[key];
    }

    void record_move(int r, int c, int k, char d, int l, int tr, int tc) {
        ans.push_back({r, c, k, d, l});
        global_recent_moves.push_back({{r, c}, {tr, tc}});
        if ((int)global_recent_moves.size() > PARAMS.recent_history_len) {
            global_recent_moves.pop_front();
        }

        vector<int> moving(stacks[r][c].begin() + k, stacks[r][c].end());
        stacks[r][c].erase(stacks[r][c].begin() + k, stacks[r][c].end());
        reverse(moving.begin(), moving.end());
        stacks[tr][tc].insert(stacks[tr][tc].end(), moving.begin(), moving.end());

        if (is_nest[tr][tc] != -1) {
            int nc = is_nest[tr][tc];
            while (!stacks[tr][tc].empty() && stacks[tr][tc].back() == nc) {
                stacks[tr][tc].pop_back();
            }
        }
        if (is_nest[r][c] != -1) {
            int nc = is_nest[r][c];
            while (!stacks[r][c].empty() && stacks[r][c].back() == nc) {
                stacks[r][c].pop_back();
            }
        }

        update_cell(r, c);
        update_cell(tr, tc);
    }

    bool is_in_global_recent(int r1, int c1, int r2, int c2) {
        for (auto& edge : global_recent_moves) {
            if ((edge.first == make_pair(r1, c1) && edge.second == make_pair(r2, c2)) ||
                (edge.first == make_pair(r2, c2) && edge.second == make_pair(r1, c1))) {
                return true;
            }
        }
        return false;
    }

    void solve() {
        set<pair<int, int>> stuck_slimes;
        set<pair<int, int>> skipped_slimes;
        map<pair<int, int>, int> height8_pending;
        map<pair<int, int>, int> combo_cooldown;

        while ((int)ans.size() < PARAMS.max_ops) {
            int cur_ans_len = ans.size();

            for (auto it = height8_pending.begin(); it != height8_pending.end(); ) {
                if (cur_ans_len >= it->second) it = height8_pending.erase(it);
                else ++it;
            }
            for (auto it = combo_cooldown.begin(); it != combo_cooldown.end(); ) {
                if (cur_ans_len >= it->second) it = combo_cooldown.erase(it);
                else ++it;
            }

            pair<int, int> best_slime = {-1, -1};
            pair<int, int> best_pri = {-1, -1};
            bool is_height_8 = false;

            // 1. 高さ8のスライムを探索
            for (int c_idx = 0; c_idx < K; ++c_idx) {
                for (auto& pos : slimes_by_color[c_idx]) {
                    int r = pos.first, c = pos.second;
                    if ((int)stacks[r][c].size() == 8) {
                        if (!stuck_slimes.count(pos) && !height8_pending.count(pos) && !skipped_slimes.count(pos)) {
                            int d = nest_dist[c_idx][r][c];
                            if (d < INF && d > best_pri.first) {
                                best_pri = {d, 8};
                                best_slime = pos;
                                is_height_8 = true;
                            }
                        }
                    }
                }
            }

            // 2. 通常スライム探索
            if (best_slime.first == -1) {
                best_pri = {-1, -1};
                for (int c_idx = 0; c_idx < K; ++c_idx) {
                    for (auto& pos : slimes_by_color[c_idx]) {
                        int r = pos.first, c = pos.second;
                        if (!stuck_slimes.count(pos) && !skipped_slimes.count(pos) && !height8_pending.count(pos)) {
                            int d = nest_dist[c_idx][r][c];
                            if (d < INF) {
                                int h_val = stacks[r][c].size();
                                pair<int, int> pri = {d, h_val};
                                if (pri > best_pri) {
                                    best_pri = pri;
                                    best_slime = pos;
                                    is_height_8 = false;
                                }
                            }
                        }
                    }
                }
            }

            if (best_slime.first == -1) {
                if (!height8_pending.empty()) {
                    height8_pending.clear();
                    continue;
                }
                if (!skipped_slimes.empty()) {
                    skipped_slimes.clear();
                    continue;
                }
            }

            // =================================================================
            // [SECTION 5: 詰まり復帰処理]
            // =================================================================
            if (best_slime.first == -1) {
                struct FallbackCandidate {
                    int h, d, r, c;
                    bool operator<(const FallbackCandidate& o) const {
                        if (h != o.h) return h > o.h;
                        return d > o.d;
                    }
                };
                vector<FallbackCandidate> all_slimes;
                for (int c_idx = 0; c_idx < K; ++c_idx) {
                    for (auto& pos : slimes_by_color[c_idx]) {
                        all_slimes.push_back({(int)stacks[pos.first][pos.second].size(), nest_dist[c_idx][pos.first][pos.second], pos.first, pos.second});
                    }
                }
                if (all_slimes.empty()) break;
                sort(all_slimes.begin(), all_slimes.end());

                tuple<int, int, int, char, int, int, int> fallback_move = {-1, -1, -1, ' ', -1, -1, -1};
                tuple<int, int, int> best_fb_score = {-INF, -INF, -INF};

                // 優先度1: 前進探索
                for (auto& sl : all_slimes) {
                    int hr = sl.r, hc = sl.c;
                    int clr = stacks[hr][hc].back();
                    int cur_h = stacks[hr][hc].size();
                    int sc = 0;
                    for (int i = cur_h - 1; i >= 0 && stacks[hr][hc][i] == clr; --i) sc++;
                    int c_dist = nest_dist[clr][hr][hc];

                    for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                        int k_val = cur_h - move_cnt;
                        int max_l_val = k_val + 1;

                        for (auto& d : DIRECTIONS) {
                            for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                int tr = hr + d.dr * l_val;
                                int tc = hc + d.dc * l_val;
                                if (!(tr >= 0 && tr < N && tc >= 0 && tc < N)) break;
                                if (is_wall[tr][tc]) break;
                                if ((int)stacks[tr][tc].size() + move_cnt > 8) continue;
                                if (is_in_global_recent(hr, hc, tr, tc)) continue;

                                int cand_d = nest_dist[clr][tr][tc];
                                if (cand_d < c_dist) {
                                    int delta = c_dist - cand_d;
                                    tuple<int, int, int> score = {delta, -cand_d, -l_val};
                                    if (score > best_fb_score) {
                                        best_fb_score = score;
                                        fallback_move = {hr, hc, k_val, d.name, l_val, tr, tc};
                                    }
                                }
                            }
                        }
                    }
                    if (get<0>(fallback_move) != -1) break;
                }

                // 優先度2: 空きマスへの退避
                if (get<0>(fallback_move) == -1) {
                    for (auto& sl : all_slimes) {
                        int hr = sl.r, hc = sl.c;
                        int clr = stacks[hr][hc].back();
                        int cur_h = stacks[hr][hc].size();
                        int sc = 0;
                        for (int i = cur_h - 1; i >= 0 && stacks[hr][hc][i] == clr; --i) sc++;

                        for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                            int k_val = cur_h - move_cnt;
                            int max_l_val = k_val + 1;

                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = hr + d.dr * l_val;
                                    int tc = hc + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N && tc >= 0 && tc < N)) break;
                                    if (is_wall[tr][tc]) break;
                                    if (stacks[tr][tc].empty()) {
                                        if (is_in_global_recent(hr, hc, tr, tc)) continue;
                                        fallback_move = {hr, hc, k_val, d.name, l_val, tr, tc};
                                        break;
                                    }
                                }
                                if (get<0>(fallback_move) != -1) break;
                            }
                            if (get<0>(fallback_move) != -1) break;
                        }
                        if (get<0>(fallback_move) != -1) break;
                    }
                }

                // 優先度3: 履歴外の合法手全探索
                if (get<0>(fallback_move) == -1) {
                    vector<pair<int, int>> all_slime_coords;
                    for (int c_idx = 0; c_idx < K; ++c_idx) {
                        for (auto& pos : slimes_by_color[c_idx]) all_slime_coords.push_back(pos);
                    }
                    shuffle(all_slime_coords.begin(), all_slime_coords.end(), rng);

                    for (auto& pos : all_slime_coords) {
                        int sr = pos.first, sc_pos = pos.second;
                        int clr = stacks[sr][sc_pos].back();
                        int h = stacks[sr][sc_pos].size();
                        int sc_cnt = 0;
                        for (int i = h - 1; i >= 0 && stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                        for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                            int k_val = h - move_cnt;
                            int max_l_val = k_val + 1;

                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = sr + d.dr * l_val;
                                    int tc = sc_pos + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N && tc >= 0 && tc < N) || is_wall[tr][tc]) break;
                                    if ((int)stacks[tr][tc].size() + move_cnt <= 8) {
                                        if (!is_in_global_recent(sr, sc_pos, tr, tc)) {
                                            fallback_move = {sr, sc_pos, k_val, d.name, l_val, tr, tc};
                                            break;
                                        }
                                    }
                                }
                                if (get<0>(fallback_move) != -1) break;
                            }
                            if (get<0>(fallback_move) != -1) break;
                        }
                        if (get<0>(fallback_move) != -1) break;
                    }
                }

                // 優先度4: 履歴制限解除（セーフティネット）
                if (get<0>(fallback_move) == -1) {
                    global_recent_moves.clear();
                    tuple<int, int, int, int, char, int, int, int> best_safety = {INF, -1, -1, -1, ' ', -1, -1, -1};

                    vector<pair<int, int>> all_slime_coords;
                    for (int c_idx = 0; c_idx < K; ++c_idx) {
                        for (auto& pos : slimes_by_color[c_idx]) all_slime_coords.push_back(pos);
                    }

                    for (auto& pos : all_slime_coords) {
                        int sr = pos.first, sc_pos = pos.second;
                        int clr = stacks[sr][sc_pos].back();
                        int h = stacks[sr][sc_pos].size();
                        int sc_cnt = 0;
                        for (int i = h - 1; i >= 0 && stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                        for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                            int k_val = h - move_cnt;
                            int max_l_val = k_val + 1;

                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = sr + d.dr * l_val;
                                    int tc = sc_pos + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N && tc >= 0 && tc < N) || is_wall[tr][tc]) break;
                                    if ((int)stacks[tr][tc].size() + move_cnt <= 8) {
                                        int d_cand = nest_dist[clr][tr][tc];
                                        if (d_cand < get<0>(best_safety)) {
                                            best_safety = {d_cand, sr, sc_pos, k_val, d.name, l_val, tr, tc};
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if (get<1>(best_safety) != -1) {
                        fallback_move = {get<1>(best_safety), get<2>(best_safety), get<3>(best_safety),
                                         get<4>(best_safety), get<5>(best_safety), get<6>(best_safety), get<7>(best_safety)};
                    }
                }

                if (get<0>(fallback_move) == -1) break;

                auto [f_hr, f_hc, f_k, f_d_str, f_l, f_tr, f_tc] = fallback_move;
                record_move(f_hr, f_hc, f_k, f_d_str, f_l, f_tr, f_tc);

                stuck_slimes.clear();
                skipped_slimes.clear();
                height8_pending.clear();
                continue;
            }

            // =================================================================
            // [SECTION 6-1: 汎用分割・踏み台ブースト合流探索]
            // =================================================================
            int cur_r = best_slime.first, cur_c = best_slime.second;
            int color = stacks[cur_r][cur_c].back();
            auto [goal_nest_r, goal_nest_c] = nest_pos[color];
            int step_limit = N * N;
            bool moved_any = false;
            bool is_merging = false;

            deque<pair<int, int>> recent_visited;
            recent_visited.push_back({cur_r, cur_c});
            int start_nest_dist = nest_dist[color][cur_r][cur_c];

            int h_cur = stacks[cur_r][cur_c].size();
            int same_count = 0;
            for (int i = h_cur - 1; i >= 0 && stacks[cur_r][cur_c][i] == color; --i) same_count++;
            int base_k = h_cur - same_count;
            int base_max_l = base_k + 1;

            int cost_direct = get_jump_dist({goal_nest_r, goal_nest_c}, base_max_l)[cur_r][cur_c];
            bool in_cooldown = (cur_ans_len < (combo_cooldown.count({cur_r, cur_c}) ? combo_cooldown[{cur_r, cur_c}] : 0));

            bool combo_found = false;
            tuple<int, int, int, char, int, int, int> act1;
            tuple<int, int, int, char, int, int, int> act2;
            tuple<int, int, int, char, int, int, int> act3;
            int min_combo_cost = cost_direct;

            if (h_cur >= PARAMS.combo_h_min && cost_direct >= PARAMS.combo_cost_min && !in_cooldown) {
                for (int split_k = 1; split_k < h_cur; ++split_k) {
                    int m_fly = h_cur - split_k;
                    int max_l_split = split_k + 1;

                    for (auto& d : DIRECTIONS) {
                        for (int l_val = 1; l_val <= max_l_split; ++l_val) {
                            int tr = cur_r + d.dr * l_val;
                            int tc = cur_c + d.dc * l_val;
                            if (!(tr >= 0 && tr < N && tc >= 0 && tc < N)) break;
                            if (is_wall[tr][tc]) break;
                            if ((int)stacks[tr][tc].size() + m_fly > 8) continue;

                            int new_h_tr = stacks[tr][tc].size() + m_fly;
                            int top_sc = m_fly;
                            if (!stacks[tr][tc].empty()) {
                                for (int i = (int)stacks[tr][tc].size() - 1; i >= 0 && stacks[tr][tc][i] == color; --i) {
                                    top_sc++;
                                }
                            }
                            int top_max_l = max(1, new_h_tr - top_sc + 1);
                            int cost_top_goal = get_jump_dist({goal_nest_r, goal_nest_c}, top_max_l)[tr][tc];
                            if (cost_top_goal >= INF) continue;

                            for (int sr = max(0, cur_r - 2); sr <= min(N - 1, cur_r + 2); ++sr) {
                                for (int sc_pos = max(0, cur_c - 2); sc_pos <= min(N - 1, cur_c + 2); ++sc_pos) {
                                    if ((sr == cur_r && sc_pos == cur_c) || (sr == tr && sc_pos == tc) || is_wall[sr][sc_pos]) continue;
                                    int h_step = stacks[sr][sc_pos].size();
                                    if (h_step >= 1 && h_step < 8) {
                                        int cap = 8 - h_step;
                                        int send_cnt = min(split_k, cap);
                                        int rem_k = split_k - send_cnt;
                                        int step_max_l = rem_k + 1;

                                        int dr_s = sr - cur_r;
                                        int dc_s = sc_pos - cur_c;
                                        char step1_dir = ' ';
                                        int step1_len = 0;

                                        if (dr_s == 0 && abs(dc_s) >= 1 && abs(dc_s) <= step_max_l) {
                                            step1_dir = (dc_s > 0) ? 'R' : 'L';
                                            int sgn = (dc_s > 0) ? 1 : -1;
                                            bool ok = true;
                                            for (int st = 1; st <= abs(dc_s); ++st) {
                                                if (is_wall[cur_r][cur_c + sgn * st]) { ok = false; break; }
                                            }
                                            if (ok) step1_len = abs(dc_s);
                                        } else if (dc_s == 0 && abs(dr_s) >= 1 && abs(dr_s) <= step_max_l) {
                                            step1_dir = (dr_s > 0) ? 'D' : 'U';
                                            int sgn = (dr_s > 0) ? 1 : -1;
                                            bool ok = true;
                                            for (int st = 1; st <= abs(dr_s); ++st) {
                                                if (is_wall[cur_r + sgn * st][cur_c]) { ok = false; break; }
                                            }
                                            if (ok) step1_len = abs(dr_s);
                                        }

                                        if (step1_len > 0) {
                                            int b_k = h_step;
                                            int b_max_l = b_k + 1;
                                            int dr_t = tr - sr;
                                            int dc_t = tc - sc_pos;
                                            char step2_dir = ' ';
                                            int step2_len = 0;

                                            if (dr_t == 0 && abs(dc_t) >= 1 && abs(dc_t) <= b_max_l) {
                                                step2_dir = (dc_t > 0) ? 'R' : 'L';
                                                int sgn2 = (dc_t > 0) ? 1 : -1;
                                                bool ok = true;
                                                for (int st = 1; st <= abs(dc_t); ++st) {
                                                    if (is_wall[sr][sc_pos + sgn2 * st]) { ok = false; break; }
                                                }
                                                if (ok) step2_len = abs(dc_t);
                                            } else if (dc_t == 0 && abs(dr_t) >= 1 && abs(dr_t) <= b_max_l) {
                                                step2_dir = (dr_t > 0) ? 'D' : 'U';
                                                int sgn2 = (dr_t > 0) ? 1 : -1;
                                                bool ok = true;
                                                for (int st = 1; st <= abs(dr_t); ++st) {
                                                    if (is_wall[sr + sgn2 * st][sc_pos]) { ok = false; break; }
                                                }
                                                if (ok) step2_len = abs(dr_t);
                                            }

                                            if (step2_len > 0 && (new_h_tr + send_cnt <= 8)) {
                                                int merged_h = new_h_tr + send_cnt;
                                                int merged_sc = top_sc + send_cnt;
                                                int merged_max_l = max(1, merged_h - merged_sc + 1);
                                                int ops_after = get_jump_dist({goal_nest_r, goal_nest_c}, merged_max_l)[tr][tc];

                                                if (ops_after < INF) {
                                                    int total_combo = 3 + ops_after;
                                                    if (total_combo < min_combo_cost) {
                                                        min_combo_cost = total_combo;
                                                        combo_found = true;
                                                        act1 = {cur_r, cur_c, split_k, d.name, l_val, tr, tc};
                                                        act2 = {cur_r, cur_c, rem_k, step1_dir, step1_len, sr, sc_pos};
                                                        act3 = {sr, sc_pos, b_k, step2_dir, step2_len, tr, tc};
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (combo_found) {
                combo_cooldown[{cur_r, cur_c}] = ans.size() + PARAMS.combo_cooldown_steps;
                combo_cooldown[{get<5>(act1), get<6>(act1)}] = ans.size() + PARAMS.combo_cooldown_steps;

                record_move(get<0>(act1), get<1>(act1), get<2>(act1), get<3>(act1), get<4>(act1), get<5>(act1), get<6>(act1));
                record_move(get<0>(act2), get<1>(act2), get<2>(act2), get<3>(act2), get<4>(act2), get<5>(act2), get<6>(act2));
                record_move(get<0>(act3), get<1>(act3), get<2>(act3), get<3>(act3), get<4>(act3), get<5>(act3), get<6>(act3));

                stuck_slimes.clear();
                skipped_slimes.clear();
                moved_any = true;

                int t3_r = get<5>(act3), t3_c = get<6>(act3);
                if (make_pair(t3_r, t3_c) != make_pair(goal_nest_r, goal_nest_c) && !stacks[t3_r][t3_c].empty()) {
                    cur_r = t3_r; cur_c = t3_c;
                    recent_visited.push_back({cur_r, cur_c});
                    is_height_8 = ((int)stacks[t3_r][t3_c].size() == 8);
                } else {
                    continue;
                }
            }

            // =================================================================
            // [SECTION 6-2: 単一スライムの移動先選定と運搬ループ]
            // =================================================================
            while ((int)ans.size() < PARAMS.max_ops && step_limit > 0) {
                step_limit--;
                if (cur_r == goal_nest_r && cur_c == goal_nest_c) break;
                int h = stacks[cur_r][cur_c].size();
                if (h == 0) break;

                int same_cnt = 0;
                for (int i = h - 1; i >= 0 && stacks[cur_r][cur_c][i] == color; --i) same_cnt++;
                int m = same_cnt;
                int k = h - m;
                int max_l = k + 1;

                tuple<int, int, int, char, int, int, int, int> best_move = {-1, -1, -1, ' ', -1, -1, -1, -1};
                bool is_staged_merge = false;
                pair<int, int> stage_target_pos = {-1, -1};
                pair<int, int> stage_best_adj = {-1, -1};

                auto find_best_move_for = [&](pair<int, int> target_coord) -> tuple<int, int, int, char, int, int, int, int> {
                    auto& j_dist = get_jump_dist(target_coord, max_l);
                    auto& t_d_map = get_dist_map(target_coord);
                    int cur_ops = j_dist[cur_r][cur_c];
                    if (cur_ops >= INF) return {-1, -1, -1, ' ', -1, -1, -1, -1};

                    tuple<int, int, int, int> b_pri = {-INF, -INF, -INF, -INF};
                    tuple<int, int, int, char, int, int, int, int> b_m = {-1, -1, -1, ' ', -1, -1, -1, -1};

                    for (auto& d : DIRECTIONS) {
                        for (int l = 1; l <= max_l; ++l) {
                            int tr = cur_r + d.dr * l;
                            int tc = cur_c + d.dc * l;
                            if (!(tr >= 0 && tr < N && tc >= 0 && tc < N)) break;
                            if (is_wall[tr][tc]) break;
                            if ((int)stacks[tr][tc].size() + m > 8) continue;

                            bool is_to_goal = (tr == goal_nest_r && tc == goal_nest_c);
                            if (!is_to_goal) {
                                bool vis = false;
                                for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                                if (vis) continue;
                                if (is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                            }

                            int cand_ops = j_dist[tr][tc];
                            if (cand_ops >= cur_ops) continue;

                            int bonus = (tr == target_coord.first && tc == target_coord.second) ? 100000 : 0;
                            int cand_real_d = t_d_map[tr][tc];

                            tuple<int, int, int, int> pri = {bonus, -cand_ops, -cand_real_d, -l};
                            if (pri > b_pri) {
                                b_pri = pri;
                                b_m = {cur_r, cur_c, k, d.name, l, tr, tc, m};
                            }
                            if (tr == target_coord.first && tc == target_coord.second) break;
                        }
                    }
                    return b_m;
                };

                // =============================================================
                // [SECTION 6-3: 最適合流相手の比較選定]
                // =============================================================
                if (!is_height_8) {
                    int ops_to_goal = get_jump_dist({goal_nest_r, goal_nest_c}, max_l)[cur_r][cur_c];
                    auto& cur_d_map = get_dist_map({cur_r, cur_c});
                    int best_overall_benefit = 0;

                    if (ops_to_goal > 1) {
                        for (auto& n_pos : slimes_by_color[color]) {
                            int nr = n_pos.first, nc = n_pos.second;
                            if (nr == cur_r && nc == cur_c) continue;
                            if (nr == goal_nest_r && nc == goal_nest_c) continue;

                            bool vis = false;
                            for (auto& v : recent_visited) if (v.first == nr && v.second == nc) vis = true;
                            if (vis) continue;
                            if (is_in_global_recent(cur_r, cur_c, nr, nc)) continue;

                            int h_target = stacks[nr][nc].size();
                            if (h_target >= 8) continue;
                            if (cur_d_map[nr][nc] > PARAMS.phase2_max_merge_dist) continue;

                            int partner_max_l = max(1, h_target);
                            int partner_saved_ops = get_jump_dist({goal_nest_r, goal_nest_c}, partner_max_l)[nr][nc];
                            if (partner_saved_ops >= INF) partner_saved_ops = 2;

                            // パターン1: 直接合流
                            if (h_target + m <= 8) {
                                int cost_detour = get_jump_dist({nr, nc}, max_l)[cur_r][cur_c];
                                if (cost_detour >= INF) continue;

                                int new_h = h_target + m;
                                int new_max_l = max(max_l, new_h);
                                int ops_from_merge = get_jump_dist({goal_nest_r, goal_nest_c}, new_max_l)[nr][nc];
                                if (ops_from_merge >= INF) continue;

                                int jump_gain = new_max_l - max_l;
                                bool is_worthwhile = (
                                    (jump_gain >= cost_detour) ||
                                    (cost_detour + ops_from_merge <= ops_to_goal) ||
                                    (cost_detour + ops_from_merge < ops_to_goal + partner_saved_ops)
                                );
                                if (is_worthwhile) {
                                    int net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + ops_from_merge) + jump_gain;
                                    if (net_benefit > best_overall_benefit) {
                                        auto test_m = find_best_move_for({nr, nc});
                                        if (get<0>(test_m) != -1) {
                                            best_overall_benefit = net_benefit;
                                            best_move = test_m;
                                            is_staged_merge = false;
                                        }
                                    }
                                }
                            }
                            // パターン2: 分割積載
                            else {
                                pair<int, int> best_adj = {-1, -1};
                                int min_adj_cost = INF;

                                for (auto& ad : DIRECTIONS) {
                                    int ar = nr + ad.dr, ac = nc + ad.dc;
                                    if (ar >= 0 && ar < N && ac >= 0 && ac < N && !is_wall[ar][ac]) {
                                        if ((int)stacks[ar][ac].size() + m <= 8) {
                                            int c_adj = get_jump_dist({ar, ac}, max_l)[cur_r][cur_c];
                                            if (c_adj < min_adj_cost) {
                                                min_adj_cost = c_adj;
                                                best_adj = {ar, ac};
                                            }
                                        }
                                    }
                                }

                                if (best_adj.first != -1 && min_adj_cost < INF) {
                                    int cost_detour = min_adj_cost + 1;
                                    int ops_target_8 = get_jump_dist({goal_nest_r, goal_nest_c}, 8)[nr][nc];
                                    int rem = m - (8 - h_target);
                                    int ops_rem = get_jump_dist({goal_nest_r, goal_nest_c}, max(1, rem))[best_adj.first][best_adj.second];

                                    if (ops_target_8 < INF && ops_rem < INF) {
                                        int total_after = ops_target_8 + ops_rem;
                                        int net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + total_after) + (8 - max_l);
                                        if (net_benefit > best_overall_benefit) {
                                            auto test_m = find_best_move_for(best_adj);
                                            if (get<0>(test_m) != -1) {
                                                best_overall_benefit = net_benefit;
                                                best_move = test_m;
                                                is_staged_merge = true;
                                                stage_target_pos = {nr, nc};
                                                stage_best_adj = best_adj;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // =============================================================
                // [SECTION 6-4: 高さ8直行 or 通常巣直行]
                // =============================================================
                if (is_height_8) {
                    int c_dist = nest_dist[color][cur_r][cur_c];
                    if (c_dist < INF) {
                        tuple<int, int, int> b_pri = {-INF, -INF, -INF};
                        for (auto& d : DIRECTIONS) {
                            for (int l = 1; l <= max_l; ++l) {
                                int tr = cur_r + d.dr * l;
                                int tc = cur_c + d.dc * l;
                                if (!(tr >= 0 && tr < N && tc >= 0 && tc < N)) break;
                                if (is_wall[tr][tc]) break;
                                if ((int)stacks[tr][tc].size() + m > 8) continue;

                                bool is_to_goal = (tr == goal_nest_r && tc == goal_nest_c);
                                if (!is_to_goal) {
                                    bool vis = false;
                                    for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                                    if (vis) continue;
                                    if (is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                                }

                                int cand_d = nest_dist[color][tr][tc];
                                if (cand_d >= c_dist) continue;

                                int delta_d = c_dist - cand_d;
                                tuple<int, int, int> pri = {delta_d, -cand_d, -l};
                                if (pri > b_pri) {
                                    b_pri = pri;
                                    best_move = {cur_r, cur_c, k, d.name, l, tr, tc, m};
                                }
                                if (is_to_goal) break;
                            }
                        }
                    }
                    if (get<0>(best_move) == -1) {
                        height8_pending[{cur_r, cur_c}] = ans.size() + PARAMS.height8_pending_steps;
                        break;
                    }
                } else {
                    if (get<0>(best_move) == -1) {
                        best_move = find_best_move_for({goal_nest_r, goal_nest_c});
                    }
                    if (get<0>(best_move) == -1) break;
                }

                // =============================================================
                // [SECTION 6-5: ジャンプ実行と更新]
                // =============================================================
                auto [bm_r, bm_c, k_val, d_str, l_val, tr, tc, m_val] = best_move;
                is_merging = (make_pair(tr, tc) != make_pair(goal_nest_r, goal_nest_c)) &&
                             (!stacks[tr][tc].empty() && stacks[tr][tc].back() == color);

                record_move(cur_r, cur_c, k_val, d_str, l_val, tr, tc);
                moved_any = true;
                recent_visited.push_back({cur_r, cur_c});
                if ((int)recent_visited.size() > PARAMS.recent_history_len) {
                    recent_visited.pop_front();
                }

                // =============================================================
                // [SECTION 6-6: 分割積載実行]
                // =============================================================
                if (is_staged_merge && make_pair(tr, tc) == stage_best_adj) {
                    int tnr = stage_target_pos.first, tnc = stage_target_pos.second;
                    int h_tgt = stacks[tnr][tnc].size();
                    if (h_tgt < 8 && !stacks[tr][tc].empty()) {
                        int max_send = min(8 - h_tgt, (int)stacks[tr][tc].size());
                        int k_send = stacks[tr][tc].size() - max_send;
                        char s_d_str = ' ';

                        for (auto& cd : DIRECTIONS) {
                            if (tr + cd.dr == tnr && tc + cd.dc == tnc) {
                                s_d_str = cd.name;
                                break;
                            }
                        }
                        if (s_d_str != ' ') {
                            record_move(tr, tc, k_send, s_d_str, 1, tnr, tnc);
                            is_merging = true;
                        }
                    }
                }

                if (tr == goal_nest_r && tc == goal_nest_c) {
                    cur_r = tr; cur_c = tc;
                    break;
                }

                cur_r = tr; cur_c = tc;
                if (is_merging) break;
            }

            if (moved_any) {
                if (is_merging) {
                    stuck_slimes.clear();
                    skipped_slimes.clear();
                } else {
                    int end_nest_dist = stacks[cur_r][cur_c].empty() ? 0 : nest_dist[color][cur_r][cur_c];
                    if (end_nest_dist >= start_nest_dist) {
                        skipped_slimes.insert({cur_r, cur_c});
                    } else {
                        stuck_slimes.clear();
                        skipped_slimes.clear();
                    }
                }
            } else {
                stuck_slimes.insert({cur_r, cur_c});
            }
        }
    }

    void print_answer() {
        for (auto& cmd : ans) {
            cout << cmd.r << " " << cmd.c << " " << cmd.k << " " << cmd.d << " " << cmd.l << "\n";
        }
    }
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    Solver solver;
    solver.read_input();
    solver.init();
    solver.solve();
    solver.print_answer();

    return 0;
}