#ifndef _WIN32
#pragma GCC optimize("O3,unroll-loops")
#pragma GCC target("avx2,bmi,bmi2,lzcnt,popcnt")
#endif

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <deque>
#include <set>
#include <tuple>
#include <algorithm>
#include <random>
#include <cstring>
#include <cstdlib>

using namespace std;

// =========================================================================
// [HYPER PARAMETERS: Optuna自動調整用]
// =========================================================================
struct HyperParams {
    int max_ops = 99990;
    int combo_h_min = 4;
    int combo_cost_min = 2;
    int combo_cooldown_steps = 30;
    int height8_pending_steps = 15;
    int recent_history_len = 50;

    // タイブレーク評価
    int bonus_catapult_align = 15;
    int bonus_pass_through_same = 8;
    int bonus_pass_through_diff = 15;

    // 終盤の単純な1マス移動を減らし、同色合流を優先する評価
    int bonus_merge_same = 220;
    int bonus_merge_height = 12;
    int penalty_repeated_short_move = 6;

    int seed = 42;
};

HyperParams PARAMS;
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

int N_GLOBAL = 0;
int K_GLOBAL = 12;
bool IS_WALL[20][20];
int IS_NEST[20][20];
pair<int, int> NEST_POS[12];
bool HAS_NEST[12];

int DIST_MAP_CACHE[20][20][20][20];
bool DIST_MAP_CALCULATED[20][20];

int JUMP_DIST_CACHE[20][20][9][20][20];
bool JUMP_DIST_CALCULATED[20][20][9];

int NEST_DIST[12][20][20];

int get_dist(int sr, int sc, int tr, int tc) {
    if (!DIST_MAP_CALCULATED[sr][sc]) {
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                DIST_MAP_CACHE[sr][sc][r][c] = INF;
            }
        }
        DIST_MAP_CACHE[sr][sc][sr][sc] = 0;
        queue<pair<int, int>> q;
        q.push({sr, sc});
        while (!q.empty()) {
            auto [r, c] = q.front(); q.pop();
            int cur_d = DIST_MAP_CACHE[sr][sc][r][c];
            for (auto& d : DIRECTIONS) {
                int nr = r + d.dr, nc = c + d.dc;
                if (nr >= 0 && nr < N_GLOBAL && nc >= 0 && nc < N_GLOBAL && !IS_WALL[nr][nc]) {
                    if (DIST_MAP_CACHE[sr][sc][nr][nc] == INF) {
                        DIST_MAP_CACHE[sr][sc][nr][nc] = cur_d + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
        DIST_MAP_CALCULATED[sr][sc] = true;
    }
    return DIST_MAP_CACHE[sr][sc][tr][tc];
}

int get_jump(int tr, int tc, int max_len, int r, int c) {
    if (max_len > 8) max_len = 8;
    if (max_len < 1) max_len = 1;

    if (!JUMP_DIST_CALCULATED[tr][tc][max_len]) {
        for (int row = 0; row < N_GLOBAL; ++row) {
            for (int col = 0; col < N_GLOBAL; ++col) {
                JUMP_DIST_CACHE[tr][tc][max_len][row][col] = INF;
            }
        }
        JUMP_DIST_CACHE[tr][tc][max_len][tr][tc] = 0;
        queue<pair<int, int>> q;
        q.push({tr, tc});
        while (!q.empty()) {
            auto [cr, cc] = q.front(); q.pop();
            int cur_d = JUMP_DIST_CACHE[tr][tc][max_len][cr][cc];
            for (auto& d : DIRECTIONS) {
                for (int l = 1; l <= max_len; ++l) {
                    int nr = cr + d.dr * l;
                    int nc = cc + d.dc * l;
                    if (!(nr >= 0 && nr < N_GLOBAL && nc >= 0 && nc < N_GLOBAL)) break;
                    if (IS_WALL[nr][nc]) break;
                    if (JUMP_DIST_CACHE[tr][tc][max_len][nr][nc] == INF) {
                        JUMP_DIST_CACHE[tr][tc][max_len][nr][nc] = cur_d + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
        JUMP_DIST_CALCULATED[tr][tc][max_len] = true;
    }
    return JUMP_DIST_CACHE[tr][tc][max_len][r][c];
}

class Solver {
public:
    vector<vector<vector<int>>> stacks;
    vector<vector<int>> top_color;
    vector<set<pair<int, int>>> slimes_by_color;
    vector<MoveCommand> ans;
    deque<pair<pair<int, int>, pair<int, int>>> global_recent_moves;
    mt19937 rng;
    int recent_history_limit = 50;

    void read_input() {
        if (!(cin >> N_GLOBAL >> K_GLOBAL)) return;
        vector<string> grid(N_GLOBAL);
        for (int i = 0; i < N_GLOBAL; ++i) cin >> grid[i];

        stacks.assign(N_GLOBAL, vector<vector<int>>(N_GLOBAL));
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                char ch = grid[r][c];
                if (ch == '#') {
                    IS_WALL[r][c] = true;
                } else if (ch >= 'a' && ch <= 'l') {
                    stacks[r][c].push_back(ch - 'a');
                } else if (ch >= 'A' && ch <= 'L') {
                    int clr = ch - 'A';
                    IS_NEST[r][c] = clr;
                    NEST_POS[clr] = {r, c};
                    HAS_NEST[clr] = true;
                }
            }
        }
        for (int c = 0; c < 12; ++c) {
            if (HAS_NEST[c]) K_GLOBAL = max(K_GLOBAL, c + 1);
        }
    }

    void init() {
        rng.seed(PARAMS.seed);
        top_color.assign(N_GLOBAL, vector<int>(N_GLOBAL, -1));
        slimes_by_color.resize(K_GLOBAL);

        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                if (!stacks[r][c].empty()) {
                    int tc = stacks[r][c].back();
                    top_color[r][c] = tc;
                    slimes_by_color[tc].insert({r, c});
                }
            }
        }

        for (int c = 0; c < K_GLOBAL; ++c) {
            if (HAS_NEST[c]) {
                for (int r = 0; r < N_GLOBAL; ++r) {
                    for (int col = 0; col < N_GLOBAL; ++col) {
                        NEST_DIST[c][r][col] = get_dist(NEST_POS[c].first, NEST_POS[c].second, r, col);
                    }
                }
            } else {
                for (int r = 0; r < N_GLOBAL; ++r) {
                    for (int col = 0; col < N_GLOBAL; ++col) {
                        NEST_DIST[c][r][col] = INF;
                    }
                }
            }
        }
    }

    void update_cell(int r, int c) {
        int old_c = top_color[r][c];
        int new_c = stacks[r][c].empty() ? -1 : stacks[r][c].back();
        if (old_c == new_c) return;

        if (old_c != -1) slimes_by_color[old_c].erase({r, c});
        if (new_c != -1) slimes_by_color[new_c].insert({r, c});
        top_color[r][c] = new_c;
    }

    void record_move(int r, int c, int k, char d, int l, int tr, int tc) {
        int cur_h = stacks[r][c].size();
        if (k < 0 || k >= cur_h || l < 1 || l > k + 1) return;
        if ((int)stacks[tr][tc].size() + (cur_h - k) > 8) return;

        ans.push_back({r, c, k, d, l});
        global_recent_moves.push_back({{r, c}, {tr, tc}});
        if ((int)global_recent_moves.size() > recent_history_limit) {
            global_recent_moves.pop_front();
        }

        vector<int> moving(stacks[r][c].begin() + k, stacks[r][c].end());
        stacks[r][c].erase(stacks[r][c].begin() + k, stacks[r][c].end());
        reverse(moving.begin(), moving.end());
        stacks[tr][tc].insert(stacks[tr][tc].end(), moving.begin(), moving.end());

        if (IS_NEST[tr][tc] != -1) {
            int nc = IS_NEST[tr][tc];
            while (!stacks[tr][tc].empty() && stacks[tr][tc].back() == nc) stacks[tr][tc].pop_back();
        }
        if (IS_NEST[r][c] != -1) {
            int nc = IS_NEST[r][c];
            while (!stacks[r][c].empty() && stacks[r][c].back() == nc) stacks[r][c].pop_back();
        }

        update_cell(r, c);
        update_cell(tr, tc);
    }

    bool is_in_global_recent(int r1, int c1, int r2, int c2) const {
        for (auto& edge : global_recent_moves) {
            if ((edge.first == make_pair(r1, c1) && edge.second == make_pair(r2, c2)) ||
                (edge.first == make_pair(r2, c2) && edge.second == make_pair(r1, c1))) {
                return true;
            }
        }
        return false;
    }

    bool exec_single_catapult(int r, int c) {
        if (stacks[r][c].empty()) return false;
        int h = stacks[r][c].size();
        int color = stacks[r][c].back();
        auto [gr, gc] = NEST_POS[color];

        int dr = gr - r, dc = gc - c;
        if (dr != 0 && dc != 0) return false;
        if (dr == 0 && dc == 0) return false;

        char d_char = ' ';
        int dist = 0;
        if (dr == 0) {
            d_char = (dc > 0) ? 'R' : 'L';
            dist = abs(dc);
            int step = (dc > 0) ? 1 : -1;
            for (int i = 1; i <= dist; ++i) if (IS_WALL[r][c + step * i]) return false;
        } else {
            d_char = (dr > 0) ? 'D' : 'U';
            dist = abs(dr);
            int step = (dr > 0) ? 1 : -1;
            for (int i = 1; i <= dist; ++i) if (IS_WALL[r + step * i][c]) return false;
        }

        int m_same = 0;
        for (int i = h - 1; i >= 0 && stacks[r][c][i] == color; --i) m_same++;

        int min_k = max(dist - 1, h - m_same);
        int max_k = h - 1;
        if (min_k > max_k) return false;

        int chosen_k = min_k;
        int m_fly = h - chosen_k;
        if ((int)stacks[gr][gc].size() + m_fly > 8) return false;

        record_move(r, c, chosen_k, d_char, dist, gr, gc);
        return true;
    }

    bool run_catapults_chain() {
        bool any_fired = false;
        bool fired_in_round = true;
        while (fired_in_round) {
            if ((int)ans.size() >= PARAMS.max_ops) break;
            fired_in_round = false;
            for (int r = 0; r < N_GLOBAL; ++r) {
                for (int c = 0; c < N_GLOBAL; ++c) {
                    while (exec_single_catapult(r, c)) {
                        fired_in_round = true;
                        any_fired = true;
                        if ((int)ans.size() >= PARAMS.max_ops) return any_fired;
                    }
                }
            }
        }
        return any_fired;
    }

    int total_remaining_slimes() const {
        int cnt = 0;
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) cnt += stacks[r][c].size();
        }
        return cnt;
    }

    bool should_skip_expensive_search() const {
        return total_remaining_slimes() > 72;
    }

    void solve() {
        set<pair<int, int>> stuck_slimes;
        set<pair<int, int>> skipped_slimes;
        vector<vector<int>> height8_pending(N_GLOBAL, vector<int>(N_GLOBAL, 0));
        vector<vector<int>> combo_cooldown(N_GLOBAL, vector<int>(N_GLOBAL, 0));
        recent_history_limit = PARAMS.recent_history_len;
        int last_remaining = total_remaining_slimes();
        int stagnant_rounds = 0;

        while ((int)ans.size() < PARAMS.max_ops) {
            int current_remaining = total_remaining_slimes();
            if (current_remaining < last_remaining) {
                stagnant_rounds = 0;
                recent_history_limit = PARAMS.recent_history_len;
            } else {
                ++stagnant_rounds;
                if (stagnant_rounds >= 100) recent_history_limit = max(PARAMS.recent_history_len, 100);
            }
            last_remaining = current_remaining;
            while ((int)global_recent_moves.size() > recent_history_limit) {
                global_recent_moves.pop_front();
            }

            if (run_catapults_chain()) {
                stuck_slimes.clear();
                skipped_slimes.clear();
                if (total_remaining_slimes() == 0) break;
            }

            int cur_ans_len = ans.size();
            pair<int, int> best_slime = {-1, -1};
            bool is_height_8 = false;

            // 1. 高さ8のスライムを最優先
            pair<int, int> best_pri = {-1, -1};
            for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                for (auto& pos : slimes_by_color[c_idx]) {
                    if ((int)stacks[pos.first][pos.second].size() == 8) {
                        if (!stuck_slimes.count(pos) && cur_ans_len >= height8_pending[pos.first][pos.second] && !skipped_slimes.count(pos)) {
                            int d = NEST_DIST[c_idx][pos.first][pos.second];
                            if (d < INF && d > best_pri.first) {
                                best_pri = {d, 8};
                                best_slime = pos;
                                is_height_8 = true;
                            }
                        }
                    }
                }
            }

            // 2. 通常のスライム探索
            if (best_slime.first == -1) {
                best_pri = {-1, -1};
                for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                    for (auto& pos : slimes_by_color[c_idx]) {
                        if (!stuck_slimes.count(pos) && !skipped_slimes.count(pos) && cur_ans_len >= height8_pending[pos.first][pos.second]) {
                            int d = NEST_DIST[c_idx][pos.first][pos.second];
                            if (d < INF) {
                                int h_val = stacks[pos.first][pos.second].size();
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

            // 保留中スライムの解除
            if (best_slime.first == -1) {
                if (!skipped_slimes.empty()) {
                    skipped_slimes.clear();
                    continue;
                }
                bool had_pending = false;
                for (int r = 0; r < N_GLOBAL; ++r) {
                    for (int c = 0; c < N_GLOBAL; ++c) {
                        if (height8_pending[r][c] > 0) {
                            height8_pending[r][c] = 0;
                            had_pending = true;
                        }
                    }
                }
                if (had_pending) continue;
            }

            // [完全版 4段階 FALLBACK ROUTING: 手詰まりを100%打破]
            if (best_slime.first == -1) {
                vector<tuple<int, int, int, int>> all_slimes;
                for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                    for (auto& pos : slimes_by_color[c_idx]) {
                        int d = NEST_DIST[c_idx][pos.first][pos.second];
                        all_slimes.push_back({(int)stacks[pos.first][pos.second].size(), d, pos.first, pos.second});
                    }
                }
                if (all_slimes.empty()) break;
                sort(all_slimes.begin(), all_slimes.end(), greater<tuple<int, int, int, int>>());

                tuple<int, int, int, char, int, int, int> fallback_move = {-1, -1, -1, ' ', -1, -1, -1};

                // 【段階1】前進探索
                tuple<int, int, int> best_fb_score = {-INF, -INF, -INF};
                for (auto& [_, _d, hr, hc] : all_slimes) {
                    int clr = stacks[hr][hc].back();
                    int cur_h = stacks[hr][hc].size();
                    int sc = 0;
                    for (int i = cur_h - 1; i >= 0 && stacks[hr][hc][i] == clr; --i) sc++;
                    int c_dist = NEST_DIST[clr][hr][hc];

                    for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                        int k_val = cur_h - move_cnt;
                        int max_l_val = k_val + 1;
                        for (auto& d : DIRECTIONS) {
                            for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                int tr = hr + d.dr * l_val, tc = hc + d.dc * l_val;
                                if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                                if (IS_WALL[tr][tc]) break;
                                if ((int)stacks[tr][tc].size() + move_cnt > 8) continue;
                                if (is_in_global_recent(hr, hc, tr, tc)) continue;

                                int cand_d = NEST_DIST[clr][tr][tc];
                                if (cand_d < c_dist) {
                                    int delta = c_dist - cand_d;
                                    tuple<int, int, int> score = {delta, -cand_d, l_val};
                                    if (score > best_fb_score) {
                                        best_fb_score = score;
                                        fallback_move = {hr, hc, k_val, d.name, l_val, tr, tc};
                                    }
                                }
                            }
                        }
                    }
                }

                // 【段階2】空きマスへの退避
                if (get<0>(fallback_move) == -1) {
                    tuple<int, int> best_evac_score = {-INF, -INF};
                    for (auto& [_, _d, hr, hc] : all_slimes) {
                        int clr = stacks[hr][hc].back();
                        int cur_h = stacks[hr][hc].size();
                        int sc = 0;
                        for (int i = cur_h - 1; i >= 0 && stacks[hr][hc][i] == clr; --i) sc++;

                        for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                            int k_val = cur_h - move_cnt;
                            int max_l_val = k_val + 1;
                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = hr + d.dr * l_val, tc = hc + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                                    if (IS_WALL[tr][tc]) break;
                                    if (stacks[tr][tc].empty()) {
                                        if (is_in_global_recent(hr, hc, tr, tc)) continue;
                                        int cand_d = NEST_DIST[clr][tr][tc];
                                        if (cand_d < INF) {
                                            tuple<int, int> score = {-cand_d, l_val};
                                            if (score > best_evac_score) {
                                                best_evac_score = score;
                                                fallback_move = {hr, hc, k_val, d.name, l_val, tr, tc};
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // 【段階3】履歴外の合法手全探索
                if (get<0>(fallback_move) == -1) {
                    vector<pair<int, int>> all_coords;
                    for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                        for (auto& pos : slimes_by_color[c_idx]) all_coords.push_back(pos);
                    }
                    shuffle(all_coords.begin(), all_coords.end(), rng);

                    for (auto& [sr, sc_pos] : all_coords) {
                        int clr = stacks[sr][sc_pos].back();
                        int h = stacks[sr][sc_pos].size();
                        int sc_cnt = 0;
                        for (int i = h - 1; i >= 0 && stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                        for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                            int k_val = h - move_cnt;
                            int max_l_val = k_val + 1;
                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = sr + d.dr * l_val, tc = sc_pos + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc]) break;
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

                // 【段階4】履歴制限解除
                if (get<0>(fallback_move) == -1) {
                    global_recent_moves.clear();
                    tuple<int, int> best_safety_score = {-INF, -INF};

                    for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                        for (auto& [sr, sc_pos] : slimes_by_color[c_idx]) {
                            int clr = stacks[sr][sc_pos].back();
                            int h = stacks[sr][sc_pos].size();
                            int sc_cnt = 0;
                            for (int i = h - 1; i >= 0 && stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                            for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                                int k_val = h - move_cnt;
                                int max_l_val = k_val + 1;
                                for (auto& d : DIRECTIONS) {
                                    for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                        int tr = sr + d.dr * l_val, tc = sc_pos + d.dc * l_val;
                                        if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc]) break;
                                        if ((int)stacks[tr][tc].size() + move_cnt <= 8) {
                                            int d_cand = NEST_DIST[clr][tr][tc];
                                            tuple<int, int> score = {-d_cand, l_val};
                                            if (score > best_safety_score) {
                                                best_safety_score = score;
                                                fallback_move = {sr, sc_pos, k_val, d.name, l_val, tr, tc};
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                if (get<0>(fallback_move) == -1) break;

                auto [f_hr, f_hc, f_k, f_d, f_l, f_tr, f_tc] = fallback_move;
                record_move(f_hr, f_hc, f_k, f_d, f_l, f_tr, f_tc);

                // 動かしたマスのみを解除してゾンビ再発を防止
                stuck_slimes.erase({f_hr, f_hc});
                stuck_slimes.erase({f_tr, f_tc});
                skipped_slimes.clear();
                continue;
            }

            // 移動計画
            int cur_r = best_slime.first, cur_c = best_slime.second;
            int color = stacks[cur_r][cur_c].back();
            auto [goal_nest_r, goal_nest_c] = NEST_POS[color];
            int step_limit = N_GLOBAL * N_GLOBAL;
            bool moved_any = false;
            bool is_merging = false;

            deque<pair<int, int>> recent_visited;
            recent_visited.push_back({cur_r, cur_c});
            int start_nest_dist = NEST_DIST[color][cur_r][cur_c];

            int h_cur = stacks[cur_r][cur_c].size();
            int same_count = 0;
            for (int i = h_cur - 1; i >= 0 && stacks[cur_r][cur_c][i] == color; --i) same_count++;
            int base_k = h_cur - same_count;
            int base_max_l = base_k + 1;

            int cost_direct = get_jump(goal_nest_r, goal_nest_c, base_max_l, cur_r, cur_c);
            bool in_cooldown = (cur_ans_len < combo_cooldown[cur_r][cur_c]);

            // 3手コンボ判定
            bool combo_found = false;
            tuple<int, int, int, char, int, int, int> act1, act2, act3;
            int min_combo_cost = cost_direct;

            if (h_cur >= PARAMS.combo_h_min && same_count == h_cur && cost_direct >= PARAMS.combo_cost_min && !in_cooldown) {
                for (int split_k = 1; split_k < h_cur; ++split_k) {
                    int m_fly = h_cur - split_k;
                    int max_l_split = split_k + 1;
                    for (auto& d : DIRECTIONS) {
                        for (int l_val = 1; l_val <= max_l_split; ++l_val) {
                            int tr = cur_r + d.dr * l_val, tc = cur_c + d.dc * l_val;
                            if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc] || IS_NEST[tr][tc] != -1) break;
                            if ((int)stacks[tr][tc].size() + m_fly > 8) continue;

                            int new_h_tr = stacks[tr][tc].size() + m_fly;
                            int top_sc = m_fly;
                            if (!stacks[tr][tc].empty()) {
                                for (int i = (int)stacks[tr][tc].size() - 1; i >= 0 && stacks[tr][tc][i] == color; --i) top_sc++;
                            }
                            int top_max_l = max(1, new_h_tr - top_sc + 1);
                            int cost_top_goal = get_jump(goal_nest_r, goal_nest_c, top_max_l, tr, tc);
                            if (cost_top_goal >= INF) continue;

                            for (int sr = max(0, cur_r - 2); sr <= min(N_GLOBAL - 1, cur_r + 2); ++sr) {
                                for (int sc_pos = max(0, cur_c - 2); sc_pos <= min(N_GLOBAL - 1, cur_c + 2); ++sc_pos) {
                                    if ((sr == cur_r && sc_pos == cur_c) || (sr == tr && sc_pos == tc) || IS_WALL[sr][sc_pos] || IS_NEST[sr][sc_pos] != -1) continue;
                                    int h_step = stacks[sr][sc_pos].size();
                                    if (h_step >= 1 && h_step < 8) {
                                        int send_cnt = min(split_k, 8 - h_step);
                                        int rem_k = split_k - send_cnt;
                                        int step_max_l = rem_k + 1;
                                        int dr_s = sr - cur_r, dc_s = sc_pos - cur_c;
                                        char step1_dir = ' '; int step1_len = 0;

                                        if (dr_s == 0 && abs(dc_s) >= 1 && abs(dc_s) <= step_max_l) {
                                            step1_dir = (dc_s > 0) ? 'R' : 'L';
                                            int sgn = (dc_s > 0) ? 1 : -1;
                                            bool ok = true;
                                            for (int st = 1; st <= abs(dc_s); ++st) if (IS_WALL[cur_r][cur_c + sgn * st]) { ok = false; break; }
                                            if (ok) step1_len = abs(dc_s);
                                        } else if (dc_s == 0 && abs(dr_s) >= 1 && abs(dr_s) <= step_max_l) {
                                            step1_dir = (dr_s > 0) ? 'D' : 'U';
                                            int sgn = (dr_s > 0) ? 1 : -1;
                                            bool ok = true;
                                            for (int st = 1; st <= abs(dr_s); ++st) if (IS_WALL[cur_r + sgn * st][cur_c]) { ok = false; break; }
                                            if (ok) step1_len = abs(dr_s);
                                        }

                                        if (step1_len > 0) {
                                            int b_max_l = h_step + 1;
                                            int dr_t = tr - sr, dc_t = tc - sc_pos;
                                            char step2_dir = ' '; int step2_len = 0;
                                            if (dr_t == 0 && abs(dc_t) >= 1 && abs(dc_t) <= b_max_l) {
                                                step2_dir = (dc_t > 0) ? 'R' : 'L';
                                                int sgn2 = (dc_t > 0) ? 1 : -1;
                                                bool ok = true;
                                                for (int st = 1; st <= abs(dc_t); ++st) if (IS_WALL[sr][sc_pos + sgn2 * st]) { ok = false; break; }
                                                if (ok) step2_len = abs(dc_t);
                                            } else if (dc_t == 0 && abs(dr_t) >= 1 && abs(dr_t) <= b_max_l) {
                                                step2_dir = (dr_t > 0) ? 'D' : 'U';
                                                int sgn2 = (dr_t > 0) ? 1 : -1;
                                                bool ok = true;
                                                for (int st = 1; st <= abs(dr_t); ++st) if (IS_WALL[sr + sgn2 * st][sc_pos]) { ok = false; break; }
                                                if (ok) step2_len = abs(dr_t);
                                            }

                                            if (step2_len > 0 && (new_h_tr + send_cnt <= 8)) {
                                                int merged_max_l = max(1, (new_h_tr + send_cnt) - (top_sc + send_cnt) + 1);
                                                int ops_after = get_jump(goal_nest_r, goal_nest_c, merged_max_l, tr, tc);
                                                if (ops_after < INF && 3 + ops_after < min_combo_cost) {
                                                    min_combo_cost = 3 + ops_after;
                                                    combo_found = true;
                                                    act1 = {cur_r, cur_c, split_k, d.name, l_val, tr, tc};
                                                    act2 = {cur_r, cur_c, rem_k, step1_dir, step1_len, sr, sc_pos};
                                                    act3 = {sr, sc_pos, h_step, step2_dir, step2_len, tr, tc};
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
                combo_cooldown[cur_r][cur_c] = ans.size() + PARAMS.combo_cooldown_steps;
                combo_cooldown[get<5>(act1)][get<6>(act1)] = ans.size() + PARAMS.combo_cooldown_steps;
                record_move(get<0>(act1), get<1>(act1), get<2>(act1), get<3>(act1), get<4>(act1), get<5>(act1), get<6>(act1));
                record_move(get<0>(act2), get<1>(act2), get<2>(act2), get<3>(act2), get<4>(act2), get<5>(act2), get<6>(act2));
                record_move(get<0>(act3), get<1>(act3), get<2>(act3), get<3>(act3), get<4>(act3), get<5>(act3), get<6>(act3));
                run_catapults_chain();
                stuck_slimes.clear();
                skipped_slimes.clear();
                continue;
            }

            // 移動ループ
            while ((int)ans.size() < PARAMS.max_ops && step_limit > 0) {
                step_limit--;
                if (cur_r == goal_nest_r && cur_c == goal_nest_c) break;
                int h = stacks[cur_r][cur_c].size();
                if (h == 0) break;

                int same_cnt = 0;
                for (int i = h - 1; i >= 0 && stacks[cur_r][cur_c][i] == color; --i) same_cnt++;
                if (same_cnt == 0) break;

                int m = same_cnt;
                int k = h - m;
                int max_l = k + 1;

                tuple<int, int, int, char, int, int, int, int> best_move = {-1, -1, -1, ' ', -1, -1, -1, -1};

                // 最良手の探索（将来手数の評価）
                auto find_best_move_for = [&](int target_r, int target_c) -> tuple<int, int, int, char, int, int, int, int> {
                    int cur_ops = get_jump(target_r, target_c, max_l, cur_r, cur_c);
                    if (cur_ops >= INF) return {-1, -1, -1, ' ', -1, -1, -1, -1};

                    tuple<int, int, int, int> b_pri = {-INF, -INF, -INF, -INF};
                    tuple<int, int, int, char, int, int, int, int> b_m = {-1, -1, -1, ' ', -1, -1, -1, -1};

                    for (auto& d : DIRECTIONS) {
                        for (int l = 1; l <= max_l; ++l) {
                            int tr = cur_r + d.dr * l, tc = cur_c + d.dc * l;
                            if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                            if (IS_WALL[tr][tc]) break;
                            if ((int)stacks[tr][tc].size() + m > 8) continue;

                            bool is_to_goal = (tr == target_r && tc == target_c);
                            if (!is_to_goal) {
                                bool vis = false;
                                for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                                if (vis || is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                            }

                            int cand_future_ops = INF;
                            int tie_breaker_bonus = 0;
                            bool merges_same_color = (!stacks[tr][tc].empty() && stacks[tr][tc].back() == color);
                            int merged_height = (int)stacks[tr][tc].size() + m;

                            if (is_to_goal) {
                                cand_future_ops = 0;
                            } else {
                                int h_after = merged_height;

                                int dr_nest = goal_nest_r - tr, dc_nest = goal_nest_c - tc;
                                bool can_catapult_next = false;
                                bool is_on_fire_line = false;

                                if ((dr_nest == 0 || dc_nest == 0) && (dr_nest != 0 || dc_nest != 0)) {
                                    int line_dist = abs(dr_nest + dc_nest);
                                    bool line_clear = true;
                                    int sdr = (dr_nest == 0) ? 0 : (dr_nest > 0 ? 1 : -1);
                                    int sdc = (dc_nest == 0) ? 0 : (dc_nest > 0 ? 1 : -1);
                                    for (int step = 1; step <= line_dist; ++step) {
                                        if (IS_WALL[tr + sdr * step][tc + sdc * step]) { line_clear = false; break; }
                                    }
                                    if (line_clear) {
                                        is_on_fire_line = true;
                                        if (line_dist <= h_after) can_catapult_next = true;
                                    }
                                }

                                if (can_catapult_next) {
                                    cand_future_ops = 1;
                                } else {
                                    // 一時的な塔の高さで過大評価せず、スライム群本来の max_l で将来手数を算出する
                                    cand_future_ops = get_jump(target_r, target_c, max_l, tr, tc);
                                }

                                if (is_on_fire_line) tie_breaker_bonus += PARAMS.bonus_catapult_align;
                                if (!stacks[tr][tc].empty()) {
                                    if (merges_same_color) tie_breaker_bonus += PARAMS.bonus_pass_through_same;
                                    else tie_breaker_bonus += PARAMS.bonus_pass_through_diff;
                                }
                            }

                            // 合流後の「実際に運べる距離」を計算する。
                            // 同色スタックへの着地なら、移動した m 個も同色列に加わるため、
                            // 合流後の先頭同色数を含めた max_l を使う。
                            int future_max_l = max_l;
                            if (merges_same_color) {
                                int dst_h = (int)stacks[tr][tc].size();
                                int dst_same = 0;
                                for (int i = dst_h - 1; i >= 0 && stacks[tr][tc][i] == color; --i) ++dst_same;
                                int merged_same = dst_same + m;
                                future_max_l = max(1, merged_height - merged_same + 1);
                                int improved_ops = get_jump(target_r, target_c, future_max_l, tr, tc);
                                if (improved_ops < cand_future_ops) cand_future_ops = improved_ops;
                                tie_breaker_bonus += PARAMS.bonus_merge_same;
                                tie_breaker_bonus += min(8, merged_height) * PARAMS.bonus_merge_height;
                            }

                            // 直前から同じ1マス移動を繰り返す候補には弱いペナルティを入れる。
                            // 完全禁止ではないので一本道などの必要な移動は残す。
                            int short_move_penalty = 0;
                            if (l == 1 && !recent_visited.empty() && recent_visited.back() == make_pair(cur_r, cur_c)) {
                                short_move_penalty = PARAMS.penalty_repeated_short_move;
                            }

                            // 従来は「将来手数が必ず1以上減る」ことを要求していたが、
                            // 合流は一時的に距離を増やしても後続で得をするため、
                            // 合流候補だけは最大1手の先行投資を許す。
                            int effective_gain = (cur_ops - cand_future_ops) * 100 + tie_breaker_bonus - short_move_penalty;
                            if (!merges_same_color && cand_future_ops >= cur_ops) continue;
                            if (merges_same_color && effective_gain <= 0) continue;

                            int goal_priority = is_to_goal ? 100000 : 0;
                            int cand_real_d = get_dist(target_r, target_c, tr, tc);

                            tuple<int, int, int, int> pri = {goal_priority + effective_gain, tie_breaker_bonus, -cand_real_d, l};
                            if (pri > b_pri) {
                                b_pri = pri;
                                b_m = {cur_r, cur_c, k, d.name, l, tr, tc, m};
                            }
                            if (is_to_goal) break;
                        }
                    }
                    return b_m;
                };

                if (is_height_8) {
                    int c_dist = NEST_DIST[color][cur_r][cur_c];
                    if (c_dist < INF) {
                        tuple<int, int, int> b_pri = {-INF, -INF, -INF};
                        for (auto& d : DIRECTIONS) {
                            for (int l = 1; l <= max_l; ++l) {
                                int tr = cur_r + d.dr * l, tc = cur_c + d.dc * l;
                                if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc]) break;
                                if ((int)stacks[tr][tc].size() + m > 8) continue;

                                bool is_to_goal = (tr == goal_nest_r && tc == goal_nest_c);
                                if (!is_to_goal) {
                                    bool vis = false;
                                    for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                                    if (vis || is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                                }

                                int cand_d = NEST_DIST[color][tr][tc];
                                if (cand_d >= c_dist) continue;

                                tuple<int, int, int> pri = {c_dist - cand_d, -cand_d, l};
                                if (pri > b_pri) {
                                    b_pri = pri;
                                    best_move = {cur_r, cur_c, k, d.name, l, tr, tc, m};
                                }
                                if (is_to_goal) break;
                            }
                        }
                    }
                    if (get<0>(best_move) == -1) {
                        height8_pending[cur_r][cur_c] = ans.size() + PARAMS.height8_pending_steps;
                        break;
                    }
                } else {
                    best_move = find_best_move_for(goal_nest_r, goal_nest_c);
                    if (get<0>(best_move) == -1) break;
                }

                auto [bm_r, bm_c, k_val, d_str, l_val, tr, tc, m_val] = best_move;

                // 同色スライムの上に重なったときのみ合流と判定（異色の上に乗っただけでは中断しない）
                is_merging = (make_pair(tr, tc) != make_pair(goal_nest_r, goal_nest_c)) &&
                             (!stacks[tr][tc].empty() && stacks[tr][tc].back() == color);

                record_move(cur_r, cur_c, k_val, d_str, l_val, tr, tc);
                moved_any = true;
                recent_visited.push_back({cur_r, cur_c});
                if ((int)recent_visited.size() > PARAMS.recent_history_len) recent_visited.pop_front();

                run_catapults_chain();

                if (tr == goal_nest_r && tc == goal_nest_c) {
                    cur_r = tr; cur_c = tc;
                    break;
                }
                cur_r = tr; cur_c = tc;
                if (is_merging) break;
            }

            if (moved_any) {
                if (is_merging) {
                    stuck_slimes.clear(); skipped_slimes.clear();
                } else {
                    int end_nest_dist = (!stacks[cur_r][cur_c].empty()) ? NEST_DIST[color][cur_r][cur_c] : 0;
                    if (end_nest_dist >= start_nest_dist) skipped_slimes.insert({cur_r, cur_c});
                    else { stuck_slimes.clear(); skipped_slimes.clear(); }
                }
            } else {
                stuck_slimes.insert({cur_r, cur_c});
            }
        }
    }

    void print_answer() const {
        for (auto& cmd : ans) {
            cout << cmd.r << " " << cmd.c << " " << cmd.k << " " << cmd.d << " " << cmd.l << "\n";
        }
    }
};

int main(int argc, char* argv[]) {
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--seed" && i + 1 < argc) PARAMS.seed = stoi(argv[++i]);
        else if (arg == "--combo_h_min" && i + 1 < argc) PARAMS.combo_h_min = stoi(argv[++i]);
        else if (arg == "--combo_cost_min" && i + 1 < argc) PARAMS.combo_cost_min = stoi(argv[++i]);
        else if (arg == "--combo_cooldown_steps" && i + 1 < argc) PARAMS.combo_cooldown_steps = stoi(argv[++i]);
        else if (arg == "--height8_pending_steps" && i + 1 < argc) PARAMS.height8_pending_steps = stoi(argv[++i]);
        else if (arg == "--recent_history_len" && i + 1 < argc) PARAMS.recent_history_len = stoi(argv[++i]);
        else if (arg == "--bonus_catapult_align" && i + 1 < argc) PARAMS.bonus_catapult_align = stoi(argv[++i]);
        else if (arg == "--bonus_pass_through_same" && i + 1 < argc) PARAMS.bonus_pass_through_same = stoi(argv[++i]);
        else if (arg == "--bonus_pass_through_diff" && i + 1 < argc) PARAMS.bonus_pass_through_diff = stoi(argv[++i]);
        else if (arg == "--bonus_merge_same" && i + 1 < argc) PARAMS.bonus_merge_same = stoi(argv[++i]);
        else if (arg == "--bonus_merge_height" && i + 1 < argc) PARAMS.bonus_merge_height = stoi(argv[++i]);
        else if (arg == "--penalty_repeated_short_move" && i + 1 < argc) PARAMS.penalty_repeated_short_move = stoi(argv[++i]);
    }

    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    memset(IS_WALL, 0, sizeof(IS_WALL));
    memset(HAS_NEST, 0, sizeof(HAS_NEST));
    memset(DIST_MAP_CALCULATED, 0, sizeof(DIST_MAP_CALCULATED));
    memset(JUMP_DIST_CALCULATED, 0, sizeof(JUMP_DIST_CALCULATED));

    for (int r = 0; r < 20; ++r) {
        for (int c = 0; c < 20; ++c) IS_NEST[r][c] = -1;
    }

    Solver solver;
    solver.read_input();
    solver.init();
    solver.solve();
    solver.print_answer();

    cout.flush();
    _Exit(0);
}