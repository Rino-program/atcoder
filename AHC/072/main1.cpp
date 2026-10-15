#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <deque>
#include <set>
#include <tuple>
#include <algorithm>
#include <chrono>
#include <random>
#include <cstring>

using namespace std;

// =========================================================================
// [HYPER PARAMETERS]
// =========================================================================
struct HyperParams {
    int max_ops = 99990;
    int phase2_max_merge_dist = 5;
    int combo_h_min = 7;
    int combo_cost_min = 3;
    int combo_cooldown_steps = 24;
    int height8_pending_steps = 15;
    int recent_history_len = 20;       // 履歴長を拡張して循環を確実に防止
    double time_limit = 600;          // 1.90秒で安全終了して出力保証
    int rand_p_h8_second = 46;
    int rand_p_norm_second = 19;
    int rand_p_norm_third = 8;
    int combo_search_radius = 2;
    int partner_saved_ops_default = 3;
    int weight_jump_gain = 0;
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

// =========================================================================
// [GLOBAL ENVIRONMENT & ULTRA-FAST FLAT CACHE]
// =========================================================================
int N_GLOBAL = 0;
int K_GLOBAL = 12;
vector<string> GRID_GLOBAL;
bool IS_WALL[20][20];
int IS_NEST[20][20];
pair<int, int> NEST_POS[12];
bool HAS_NEST[12];

// 静的フラットキャッシュ (合計 約6MB: メモリ制限 1024MB 内に完全余裕)
int DIST_MAP_CACHE[20][20][20][20];
bool DIST_MAP_CALCULATED[20][20];

int JUMP_DIST_CACHE[20][20][9][20][20];
bool JUMP_DIST_CALCULATED[20][20][9];

int NEST_DIST[12][20][20];

const int* get_dist_map_ptr(int sr, int sc) {
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
            auto [r, c] = q.front();
            q.pop();
            int cur_d = DIST_MAP_CACHE[sr][sc][r][c];
            for (auto& d : DIRECTIONS) {
                int nr = r + d.dr;
                int nc = c + d.dc;
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
    return &DIST_MAP_CACHE[sr][sc][0][0];
}

int get_dist(int sr, int sc, int tr, int tc) {
    get_dist_map_ptr(sr, sc);
    return DIST_MAP_CACHE[sr][sc][tr][tc];
}

const int* get_jump_dist_ptr(int tr, int tc, int max_len) {
    if (max_len > 8) max_len = 8;
    if (max_len < 1) max_len = 1;

    if (!JUMP_DIST_CALCULATED[tr][tc][max_len]) {
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                JUMP_DIST_CACHE[tr][tc][max_len][r][c] = INF;
            }
        }
        JUMP_DIST_CACHE[tr][tc][max_len][tr][tc] = 0;
        queue<pair<int, int>> q;
        q.push({tr, tc});

        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();
            int d_cur = JUMP_DIST_CACHE[tr][tc][max_len][r][c];

            for (auto& d : DIRECTIONS) {
                for (int l = 1; l <= max_len; ++l) {
                    int nr = r + d.dr * l;
                    int nc = c + d.dc * l;
                    if (!(nr >= 0 && nr < N_GLOBAL && nc >= 0 && nc < N_GLOBAL)) break;
                    if (IS_WALL[nr][nc]) break;

                    if (JUMP_DIST_CACHE[tr][tc][max_len][nr][nc] == INF) {
                        JUMP_DIST_CACHE[tr][tc][max_len][nr][nc] = d_cur + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
        JUMP_DIST_CALCULATED[tr][tc][max_len] = true;
    }
    return &JUMP_DIST_CACHE[tr][tc][max_len][0][0];
}

int get_jump(int tr, int tc, int max_len, int r, int c) {
    get_jump_dist_ptr(tr, tc, max_len);
    return JUMP_DIST_CACHE[tr][tc][max_len][r][c];
}

// =========================================================================
// [STATE NODE]
// =========================================================================
struct State {
    vector<vector<vector<int>>> stacks;
    vector<vector<int>> top_color;
    vector<set<pair<int, int>>> slimes_by_color;
    vector<MoveCommand> ans;
    deque<pair<pair<int, int>, pair<int, int>>> global_recent_moves;

    int total_remaining_slimes() const {
        int cnt = 0;
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                cnt += stacks[r][c].size();
            }
        }
        return cnt;
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

        if (IS_NEST[tr][tc] != -1) {
            int nc = IS_NEST[tr][tc];
            while (!stacks[tr][tc].empty() && stacks[tr][tc].back() == nc) {
                stacks[tr][tc].pop_back();
            }
        }
        if (IS_NEST[r][c] != -1) {
            int nc = IS_NEST[r][c];
            while (!stacks[r][c].empty() && stacks[r][c].back() == nc) {
                stacks[r][c].pop_back();
            }
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
};

// =========================================================================
// [SIMULATION CORE WITH ROBUST FALLBACK]
// =========================================================================
bool simulate_full(State& st, mt19937& rng, bool randomized, const chrono::steady_clock::time_point& start_time) {
    set<pair<int, int>> stuck_slimes;
    set<pair<int, int>> skipped_slimes;
    vector<vector<int>> height8_pending(N_GLOBAL, vector<int>(N_GLOBAL, 0));
    vector<vector<int>> combo_cooldown(N_GLOBAL, vector<int>(N_GLOBAL, 0));

    auto is_time_up = [&]() {
        auto now = chrono::steady_clock::now();
        return chrono::duration<double>(now - start_time).count() >= PARAMS.time_limit;
    };

    while ((int)st.ans.size() < PARAMS.max_ops) {
        if (is_time_up()) break;

        int cur_ans_len = st.ans.size();

        pair<int, int> best_slime = {-1, -1};
        bool is_height_8 = false;

        // 1. 高さ8のスライムを最優先探索
        vector<pair<pair<int, int>, pair<int, int>>> h8_cands;
        for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
            for (auto& pos : st.slimes_by_color[c_idx]) {
                if ((int)st.stacks[pos.first][pos.second].size() == 8) {
                    if (!stuck_slimes.count(pos) && cur_ans_len >= height8_pending[pos.first][pos.second] && !skipped_slimes.count(pos)) {
                        int d = NEST_DIST[c_idx][pos.first][pos.second];
                        if (d < INF) {
                            h8_cands.push_back({{d, 8}, pos});
                        }
                    }
                }
            }
        }
        if (!h8_cands.empty()) {
            sort(h8_cands.begin(), h8_cands.end(), greater<pair<pair<int, int>, pair<int, int>>>());
            int pick = 0;
            if (randomized && h8_cands.size() >= 2 && ((int)(rng() % 100) < PARAMS.rand_p_h8_second)) pick = 1;
            best_slime = h8_cands[pick].second;
            is_height_8 = true;
        }

        // 2. 通常のスライム探索
        if (best_slime.first == -1) {
            vector<pair<pair<int, int>, pair<int, int>>> normal_cands;
            for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                for (auto& pos : st.slimes_by_color[c_idx]) {
                    if (!stuck_slimes.count(pos) && !skipped_slimes.count(pos) && cur_ans_len >= height8_pending[pos.first][pos.second]) {
                        int d = NEST_DIST[c_idx][pos.first][pos.second];
                        if (d < INF) {
                            int h_val = st.stacks[pos.first][pos.second].size();
                            normal_cands.push_back({{d, h_val}, pos});
                        }
                    }
                }
            }
            if (!normal_cands.empty()) {
                sort(normal_cands.begin(), normal_cands.end(), greater<pair<pair<int, int>, pair<int, int>>>());
                int pick = 0;
                if (randomized && normal_cands.size() >= 2 && ((int)(rng() % 100) < PARAMS.rand_p_norm_second)) pick = 1;
                if (randomized && normal_cands.size() >= 3 && ((int)(rng() % 100) < PARAMS.rand_p_norm_third)) pick = 2;
                best_slime = normal_cands[pick].second;
                is_height_8 = false;
            }
        }

        // スライムが見つからない場合、保留・スキップを解除
        if (best_slime.first == -1) {
            if (!skipped_slimes.empty()) {
                skipped_slimes.clear();
                continue;
            }
        }

        // =================================================================
        // [SECTION 5: 詰まり復帰処理 (FALLBACK ROUTING)]
        // =================================================================
        if (best_slime.first == -1) {
            vector<tuple<int, int, int, int>> all_slimes;
            for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                for (auto& pos : st.slimes_by_color[c_idx]) {
                    int d = NEST_DIST[c_idx][pos.first][pos.second];
                    all_slimes.push_back({(int)st.stacks[pos.first][pos.second].size(), d, pos.first, pos.second});
                }
            }

            if (all_slimes.empty()) break; // 全員帰巣完了！

            sort(all_slimes.begin(), all_slimes.end(), greater<tuple<int, int, int, int>>());

            tuple<int, int, int, char, int, int, int> fallback_move = {-1, -1, -1, ' ', -1, -1, -1};
            tuple<int, int, int> best_fb_score = {-INF, -INF, -INF};

            // 優先度1: 前進できる手があるか全スライムから探索
            for (auto& [_, _d, hr, hc] : all_slimes) {
                int clr = st.stacks[hr][hc].back();
                int cur_h = st.stacks[hr][hc].size();
                int sc = 0;
                for (int i = cur_h - 1; i >= 0 && st.stacks[hr][hc][i] == clr; --i) sc++;
                int c_dist = NEST_DIST[clr][hr][hc];

                for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                    int k_val = cur_h - move_cnt;
                    int max_l_val = k_val + 1;

                    for (auto& d : DIRECTIONS) {
                        for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                            int tr = hr + d.dr * l_val;
                            int tc = hc + d.dc * l_val;
                            if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                            if (IS_WALL[tr][tc]) break;
                            if ((int)st.stacks[tr][tc].size() + move_cnt > 8) continue;
                            if (st.is_in_global_recent(hr, hc, tr, tc)) continue;

                            int cand_d = NEST_DIST[clr][tr][tc];
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

            // 優先度2: 前進できない場合、空きマスへの退避（道あけ）
            if (get<0>(fallback_move) == -1) {
                for (auto& [_, _d, hr, hc] : all_slimes) {
                    int clr = st.stacks[hr][hc].back();
                    int cur_h = st.stacks[hr][hc].size();
                    int sc = 0;
                    for (int i = cur_h - 1; i >= 0 && st.stacks[hr][hc][i] == clr; --i) sc++;

                    for (int move_cnt = sc; move_cnt >= 1; --move_cnt) {
                        int k_val = cur_h - move_cnt;
                        int max_l_val = k_val + 1;

                        for (auto& d : DIRECTIONS) {
                            for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                int tr = hr + d.dr * l_val;
                                int tc = hc + d.dc * l_val;
                                if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                                if (IS_WALL[tr][tc]) break;
                                if (st.stacks[tr][tc].empty()) {
                                    if (st.is_in_global_recent(hr, hc, tr, tc)) continue;
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

            // 優先度3: 履歴に引っかからない合法的1手
            if (get<0>(fallback_move) == -1) {
                vector<pair<int, int>> all_coords;
                for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                    for (auto& pos : st.slimes_by_color[c_idx]) all_coords.push_back(pos);
                }
                shuffle(all_coords.begin(), all_coords.end(), rng);

                for (auto& [sr, sc_pos] : all_coords) {
                    int clr = st.stacks[sr][sc_pos].back();
                    int h = st.stacks[sr][sc_pos].size();
                    int sc_cnt = 0;
                    for (int i = h - 1; i >= 0 && st.stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                    for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                        int k_val = h - move_cnt;
                        int max_l_val = k_val + 1;

                        for (auto& d : DIRECTIONS) {
                            for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                int tr = sr + d.dr * l_val;
                                int tc = sc_pos + d.dc * l_val;
                                if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc]) break;
                                if ((int)st.stacks[tr][tc].size() + move_cnt <= 8) {
                                    if (!st.is_in_global_recent(sr, sc_pos, tr, tc)) {
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

            // 優先度4 (最後のセーフティネット)
            if (get<0>(fallback_move) == -1) {
                st.global_recent_moves.clear();
                vector<tuple<int, int, int, int, char, int, int, int>> cand_safety;

                for (int c_idx = 0; c_idx < K_GLOBAL; ++c_idx) {
                    for (auto& [sr, sc_pos] : st.slimes_by_color[c_idx]) {
                        int clr = st.stacks[sr][sc_pos].back();
                        int h = st.stacks[sr][sc_pos].size();
                        int sc_cnt = 0;
                        for (int i = h - 1; i >= 0 && st.stacks[sr][sc_pos][i] == clr; --i) sc_cnt++;

                        for (int move_cnt = sc_cnt; move_cnt >= 1; --move_cnt) {
                            int k_val = h - move_cnt;
                            int max_l_val = k_val + 1;

                            for (auto& d : DIRECTIONS) {
                                for (int l_val = 1; l_val <= max_l_val; ++l_val) {
                                    int tr = sr + d.dr * l_val;
                                    int tc = sc_pos + d.dc * l_val;
                                    if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL) || IS_WALL[tr][tc]) break;
                                    if ((int)st.stacks[tr][tc].size() + move_cnt <= 8) {
                                        int d_cand = NEST_DIST[clr][tr][tc];
                                        cand_safety.push_back({d_cand, sr, sc_pos, k_val, d.name, l_val, tr, tc});
                                    }
                                }
                            }
                        }
                    }
                }
                if (!cand_safety.empty()) {
                    sort(cand_safety.begin(), cand_safety.end());
                    auto [_, b_sr, b_sc, b_k, b_d, b_l, b_tr, b_tc] = cand_safety[0];
                    fallback_move = {b_sr, b_sc, b_k, b_d, b_l, b_tr, b_tc};
                }
            }

            if (get<0>(fallback_move) == -1) break; // 盤面に合法手なし

            auto [f_hr, f_hc, f_k, f_d, f_l, f_tr, f_tc] = fallback_move;
            st.record_move(f_hr, f_hc, f_k, f_d, f_l, f_tr, f_tc);

            // ピンポン防止: 退避先のスライムは即座にスタック解除せず、徐々に解放
            stuck_slimes.erase({f_hr, f_hc});
            stuck_slimes.erase({f_tr, f_tc});
            skipped_slimes.clear();
            continue;
        }

        // =================================================================
        // [SECTION 6: 通常運搬マクロ]
        // =================================================================
        int cur_r = best_slime.first, cur_c = best_slime.second;
        int color = st.stacks[cur_r][cur_c].back();
        auto [goal_nest_r, goal_nest_c] = NEST_POS[color];
        int step_limit = N_GLOBAL * N_GLOBAL;
        bool moved_any = false;
        bool is_merging = false;

        deque<pair<int, int>> recent_visited;
        recent_visited.push_back({cur_r, cur_c});
        int start_nest_dist = NEST_DIST[color][cur_r][cur_c];

        int h_cur = st.stacks[cur_r][cur_c].size();
        int same_count = 0;
        for (int i = h_cur - 1; i >= 0 && st.stacks[cur_r][cur_c][i] == color; --i) same_count++;
        int base_k = h_cur - same_count;
        int base_max_l = base_k + 1;

        int cost_direct = get_jump(goal_nest_r, goal_nest_c, base_max_l, cur_r, cur_c);
        bool in_cooldown = (cur_ans_len < combo_cooldown[cur_r][cur_c]);

        bool combo_found = false;
        tuple<int, int, int, char, int, int, int> act1 = {-1, -1, -1, ' ', -1, -1, -1};
        tuple<int, int, int, char, int, int, int> act2 = {-1, -1, -1, ' ', -1, -1, -1};
        tuple<int, int, int, char, int, int, int> act3 = {-1, -1, -1, ' ', -1, -1, -1};
        int min_combo_cost = cost_direct;

        // 分割・踏み台コンボ
        if (h_cur >= PARAMS.combo_h_min && cost_direct >= PARAMS.combo_cost_min && !in_cooldown) {
            for (int split_k = 1; split_k < h_cur; ++split_k) {
                int m_fly = h_cur - split_k;
                int max_l_split = split_k + 1;

                for (auto& d : DIRECTIONS) {
                    for (int l_val = 1; l_val <= max_l_split; ++l_val) {
                        int tr = cur_r + d.dr * l_val;
                        int tc = cur_c + d.dc * l_val;
                        if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                        if (IS_WALL[tr][tc]) break;
                        if ((int)st.stacks[tr][tc].size() + m_fly > 8) continue;

                        int new_h_tr = st.stacks[tr][tc].size() + m_fly;
                        int top_sc = m_fly;
                        if (!st.stacks[tr][tc].empty()) {
                            for (int i = (int)st.stacks[tr][tc].size() - 1; i >= 0 && st.stacks[tr][tc][i] == color; --i) top_sc++;
                        }
                        int top_max_l = max(1, new_h_tr - top_sc + 1);
                        int cost_top_goal = get_jump(goal_nest_r, goal_nest_c, top_max_l, tr, tc);
                        if (cost_top_goal >= INF) continue;

                        int rad = PARAMS.combo_search_radius;
                        for (int sr = max(0, cur_r - rad); sr <= min(N_GLOBAL - 1, cur_r + rad); ++sr) {
                            for (int sc_pos = max(0, cur_c - rad); sc_pos <= min(N_GLOBAL - 1, cur_c + rad); ++sc_pos) {
                                if ((sr == cur_r && sc_pos == cur_c) || (sr == tr && sc_pos == tc) || IS_WALL[sr][sc_pos]) continue;
                                int h_step = st.stacks[sr][sc_pos].size();
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
                                        for (int st_step = 1; st_step <= abs(dc_s); ++st_step) {
                                            if (IS_WALL[cur_r][cur_c + sgn * st_step]) { ok = false; break; }
                                        }
                                        if (ok) step1_len = abs(dc_s);
                                    } else if (dc_s == 0 && abs(dr_s) >= 1 && abs(dr_s) <= step_max_l) {
                                        step1_dir = (dr_s > 0) ? 'D' : 'U';
                                        int sgn = (dr_s > 0) ? 1 : -1;
                                        bool ok = true;
                                        for (int st_step = 1; st_step <= abs(dr_s); ++st_step) {
                                            if (IS_WALL[cur_r + sgn * st_step][cur_c]) { ok = false; break; }
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
                                            for (int st_step = 1; st_step <= abs(dc_t); ++st_step) {
                                                if (IS_WALL[sr][sc_pos + sgn2 * st_step]) { ok = false; break; }
                                            }
                                            if (ok) step2_len = abs(dc_t);
                                        } else if (dc_t == 0 && abs(dr_t) >= 1 && abs(dr_t) <= b_max_l) {
                                            step2_dir = (dr_t > 0) ? 'D' : 'U';
                                            int sgn2 = (dr_t > 0) ? 1 : -1;
                                            bool ok = true;
                                            for (int st_step = 1; st_step <= abs(dr_t); ++st_step) {
                                                if (IS_WALL[sr + sgn2 * st_step][sc_pos]) { ok = false; break; }
                                            }
                                            if (ok) step2_len = abs(dr_t);
                                        }

                                        if (step2_len > 0 && (new_h_tr + send_cnt <= 8)) {
                                            int merged_h = new_h_tr + send_cnt;
                                            int merged_sc = top_sc + send_cnt;
                                            int merged_max_l = max(1, merged_h - merged_sc + 1);
                                            int ops_after = get_jump(goal_nest_r, goal_nest_c, merged_max_l, tr, tc);

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
            combo_cooldown[cur_r][cur_c] = st.ans.size() + PARAMS.combo_cooldown_steps;
            combo_cooldown[get<5>(act1)][get<6>(act1)] = st.ans.size() + PARAMS.combo_cooldown_steps;

            st.record_move(get<0>(act1), get<1>(act1), get<2>(act1), get<3>(act1), get<4>(act1), get<5>(act1), get<6>(act1));
            st.record_move(get<0>(act2), get<1>(act2), get<2>(act2), get<3>(act2), get<4>(act2), get<5>(act2), get<6>(act2));
            st.record_move(get<0>(act3), get<1>(act3), get<2>(act3), get<3>(act3), get<4>(act3), get<5>(act3), get<6>(act3));

            stuck_slimes.clear();
            skipped_slimes.clear();
            moved_any = true;

            int t3_r = get<5>(act3), t3_c = get<6>(act3);
            if (make_pair(t3_r, t3_c) != make_pair(goal_nest_r, goal_nest_c) && !st.stacks[t3_r][t3_c].empty()) {
                cur_r = t3_r; cur_c = t3_c;
                recent_visited.push_back({cur_r, cur_c});
                is_height_8 = ((int)st.stacks[t3_r][t3_c].size() == 8);
            } else {
                continue;
            }
        }

        // 通常運搬ループ
        while ((int)st.ans.size() < PARAMS.max_ops && step_limit > 0) {
            step_limit--;
            if (cur_r == goal_nest_r && cur_c == goal_nest_c) break;
            int h = st.stacks[cur_r][cur_c].size();
            if (h == 0) break;

            int same_cnt = 0;
            for (int i = h - 1; i >= 0 && st.stacks[cur_r][cur_c][i] == color; --i) same_cnt++;
            int m = same_cnt;
            int k = h - m;
            int max_l = k + 1;

            tuple<int, int, int, char, int, int, int, int> best_move = {-1, -1, -1, ' ', -1, -1, -1, -1};
            bool is_staged_merge = false;
            pair<int, int> stage_target_pos = {-1, -1};
            pair<int, int> stage_best_adj = {-1, -1};

            auto find_best_move_for = [&](int target_r, int target_c) -> tuple<int, int, int, char, int, int, int, int> {
                int cur_ops = get_jump(target_r, target_c, max_l, cur_r, cur_c);
                if (cur_ops >= INF) return {-1, -1, -1, ' ', -1, -1, -1, -1};

                tuple<int, int, int, int> b_pri = {-INF, -INF, -INF, -INF};
                tuple<int, int, int, char, int, int, int, int> b_m = {-1, -1, -1, ' ', -1, -1, -1, -1};

                for (auto& d : DIRECTIONS) {
                    for (int l = 1; l <= max_l; ++l) {
                        int tr = cur_r + d.dr * l;
                        int tc = cur_c + d.dc * l;
                        if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                        if (IS_WALL[tr][tc]) break;
                        if ((int)st.stacks[tr][tc].size() + m > 8) continue;

                        bool is_to_goal = (tr == goal_nest_r && tc == goal_nest_c);
                        if (!is_to_goal) {
                            bool vis = false;
                            for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                            if (vis) continue;
                            if (st.is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                        }

                        int cand_ops = get_jump(target_r, target_c, max_l, tr, tc);
                        if (cand_ops >= cur_ops) continue;

                        int bonus = (tr == target_r && tc == target_c) ? 100000 : 0;
                        int cand_real_d = get_dist(target_r, target_c, tr, tc);

                        tuple<int, int, int, int> pri = {bonus, -cand_ops, -cand_real_d, -l};
                        if (pri > b_pri) {
                            b_pri = pri;
                            b_m = {cur_r, cur_c, k, d.name, l, tr, tc, m};
                        }
                        if (tr == target_r && tc == target_c) break;
                    }
                }
                return b_m;
            };

            if (!is_height_8) {
                int ops_to_goal = get_jump(goal_nest_r, goal_nest_c, max_l, cur_r, cur_c);
                int best_overall_benefit = 0;

                if (ops_to_goal > 1) {
                    for (auto& n_pos : st.slimes_by_color[color]) {
                        int nr = n_pos.first, nc = n_pos.second;
                        if (nr == cur_r && nc == cur_c) continue;
                        if (nr == goal_nest_r && nc == goal_nest_c) continue;

                        bool vis = false;
                        for (auto& v : recent_visited) if (v.first == nr && v.second == nc) vis = true;
                        if (vis) continue;
                        if (st.is_in_global_recent(cur_r, cur_c, nr, nc)) continue;

                        int h_target = st.stacks[nr][nc].size();
                        if (h_target >= 8) continue;

                        int d_val = get_dist(cur_r, cur_c, nr, nc);
                        if (d_val > PARAMS.phase2_max_merge_dist) continue;

                        int partner_max_l = max(1, h_target);
                        int partner_saved_ops = get_jump(goal_nest_r, goal_nest_c, partner_max_l, nr, nc);
                        if (partner_saved_ops >= INF) partner_saved_ops = PARAMS.partner_saved_ops_default;

                        if (h_target + m <= 8) {
                            int cost_detour = get_jump(nr, nc, max_l, cur_r, cur_c);
                            if (cost_detour >= INF) continue;

                            int new_h = h_target + m;
                            int new_max_l = max(max_l, new_h);
                            int ops_from_merge = get_jump(goal_nest_r, goal_nest_c, new_max_l, nr, nc);
                            if (ops_from_merge >= INF) continue;

                            int jump_gain = new_max_l - max_l;
                            bool is_worthwhile = (
                                (jump_gain >= cost_detour) ||
                                (cost_detour + ops_from_merge <= ops_to_goal) ||
                                (cost_detour + ops_from_merge < ops_to_goal + partner_saved_ops)
                            );
                            if (is_worthwhile) {
                                int net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + ops_from_merge) + jump_gain * PARAMS.weight_jump_gain;
                                if (net_benefit > best_overall_benefit) {
                                    auto test_m = find_best_move_for(nr, nc);
                                    if (get<0>(test_m) != -1) {
                                        best_overall_benefit = net_benefit;
                                        best_move = test_m;
                                        is_staged_merge = false;
                                    }
                                }
                            }
                        } else {
                            pair<int, int> best_adj = {-1, -1};
                            int min_adj_cost = INF;

                            for (auto& ad : DIRECTIONS) {
                                int ar = nr + ad.dr, ac = nc + ad.dc;
                                if (ar >= 0 && ar < N_GLOBAL && ac >= 0 && ac < N_GLOBAL && !IS_WALL[ar][ac]) {
                                    if ((int)st.stacks[ar][ac].size() + m <= 8) {
                                        int c_adj = get_jump(ar, ac, max_l, cur_r, cur_c);
                                        if (c_adj < min_adj_cost) {
                                            min_adj_cost = c_adj;
                                            best_adj = {ar, ac};
                                        }
                                    }
                                }
                            }

                            if (best_adj.first != -1 && min_adj_cost < INF) {
                                int cost_detour = min_adj_cost + 1;
                                int ops_target_8 = get_jump(goal_nest_r, goal_nest_c, 8, nr, nc);
                                int rem = m - (8 - h_target);
                                int ops_rem = get_jump(goal_nest_r, goal_nest_c, max(1, rem), best_adj.first, best_adj.second);

                                if (ops_target_8 < INF && ops_rem < INF) {
                                    int total_after = ops_target_8 + ops_rem;
                                    int net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + total_after) + (8 - max_l) * PARAMS.weight_jump_gain;
                                    if (net_benefit > best_overall_benefit) {
                                        auto test_m = find_best_move_for(best_adj.first, best_adj.second);
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

            if (is_height_8) {
                int c_dist = NEST_DIST[color][cur_r][cur_c];
                if (c_dist < INF) {
                    tuple<int, int, int> b_pri = {-INF, -INF, -INF};
                    for (auto& d : DIRECTIONS) {
                        for (int l = 1; l <= max_l; ++l) {
                            int tr = cur_r + d.dr * l;
                            int tc = cur_c + d.dc * l;
                            if (!(tr >= 0 && tr < N_GLOBAL && tc >= 0 && tc < N_GLOBAL)) break;
                            if (IS_WALL[tr][tc]) break;
                            if ((int)st.stacks[tr][tc].size() + m > 8) continue;

                            bool is_to_goal = (tr == goal_nest_r && tc == goal_nest_c);
                            if (!is_to_goal) {
                                bool vis = false;
                                for (auto& v : recent_visited) if (v.first == tr && v.second == tc) vis = true;
                                if (vis) continue;
                                if (st.is_in_global_recent(cur_r, cur_c, tr, tc)) continue;
                            }

                            int cand_d = NEST_DIST[color][tr][tc];
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
                    height8_pending[cur_r][cur_c] = st.ans.size() + PARAMS.height8_pending_steps;
                    break;
                }
            } else {
                if (get<0>(best_move) == -1) {
                    best_move = find_best_move_for(goal_nest_r, goal_nest_c);
                }
                if (get<0>(best_move) == -1) break;
            }

            auto [bm_r, bm_c, k_val, d_str, l_val, tr, tc, m_val] = best_move;
            is_merging = (make_pair(tr, tc) != make_pair(goal_nest_r, goal_nest_c)) &&
                         (!st.stacks[tr][tc].empty() && st.stacks[tr][tc].back() == color);

            st.record_move(cur_r, cur_c, k_val, d_str, l_val, tr, tc);
            moved_any = true;
            recent_visited.push_back({cur_r, cur_c});
            if ((int)recent_visited.size() > PARAMS.recent_history_len) {
                recent_visited.pop_front();
            }

            if (is_staged_merge && make_pair(tr, tc) == stage_best_adj) {
                int tnr = stage_target_pos.first, tnc = stage_target_pos.second;
                int h_tgt = st.stacks[tnr][tnc].size();
                if (h_tgt < 8 && !st.stacks[tr][tc].empty()) {
                    int max_send = min(8 - h_tgt, (int)st.stacks[tr][tc].size());
                    int k_send = st.stacks[tr][tc].size() - max_send;
                    char s_d_str = ' ';

                    for (auto& cd : DIRECTIONS) {
                        if (tr + cd.dr == tnr && tc + cd.dc == tnc) {
                            s_d_str = cd.name;
                            break;
                        }
                    }
                    if (s_d_str != ' ') {
                        st.record_move(tr, tc, k_send, s_d_str, 1, tnr, tnc);
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

        // 移動成否に応じた状態更新
        if (moved_any) {
            if (is_merging) {
                stuck_slimes.clear();
                skipped_slimes.clear();
            } else {
                int end_nest_dist = (!st.stacks[cur_r][cur_c].empty()) ? NEST_DIST[color][cur_r][cur_c] : 0;
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

    return st.total_remaining_slimes() == 0;
}

// =========================================================================
// [MAIN ENTRY]
// =========================================================================
int main(int argc, char* argv[]) {
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--phase2_max_merge_dist" && i + 1 < argc) PARAMS.phase2_max_merge_dist = stoi(argv[++i]);
        else if (arg == "--combo_h_min" && i + 1 < argc) PARAMS.combo_h_min = stoi(argv[++i]);
        else if (arg == "--combo_cost_min" && i + 1 < argc) PARAMS.combo_cost_min = stoi(argv[++i]);
        else if (arg == "--combo_cooldown_steps" && i + 1 < argc) PARAMS.combo_cooldown_steps = stoi(argv[++i]);
        else if (arg == "--height8_pending_steps" && i + 1 < argc) PARAMS.height8_pending_steps = stoi(argv[++i]);
        else if (arg == "--recent_history_len" && i + 1 < argc) PARAMS.recent_history_len = stoi(argv[++i]);
        else if (arg == "--time_limit" && i + 1 < argc) PARAMS.time_limit = stod(argv[++i]);
        else if (arg == "--rand_p_h8_second" && i + 1 < argc) PARAMS.rand_p_h8_second = stoi(argv[++i]);
        else if (arg == "--rand_p_norm_second" && i + 1 < argc) PARAMS.rand_p_norm_second = stoi(argv[++i]);
        else if (arg == "--rand_p_norm_third" && i + 1 < argc) PARAMS.rand_p_norm_third = stoi(argv[++i]);
        else if (arg == "--combo_search_radius" && i + 1 < argc) PARAMS.combo_search_radius = stoi(argv[++i]);
        else if (arg == "--partner_saved_ops_default" && i + 1 < argc) PARAMS.partner_saved_ops_default = stoi(argv[++i]);
        else if (arg == "--weight_jump_gain" && i + 1 < argc) PARAMS.weight_jump_gain = stoi(argv[++i]);
    }

    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    auto start_time = chrono::steady_clock::now();

    memset(IS_WALL, 0, sizeof(IS_WALL));
    memset(HAS_NEST, 0, sizeof(HAS_NEST));
    memset(DIST_MAP_CALCULATED, 0, sizeof(DIST_MAP_CALCULATED));
    memset(JUMP_DIST_CALCULATED, 0, sizeof(JUMP_DIST_CALCULATED));

    for (int r = 0; r < 20; ++r) {
        for (int c = 0; c < 20; ++c) {
            IS_NEST[r][c] = -1;
        }
    }

    if (!(cin >> N_GLOBAL >> K_GLOBAL)) return 0;
    GRID_GLOBAL.resize(N_GLOBAL);
    for (int i = 0; i < N_GLOBAL; ++i) {
        cin >> GRID_GLOBAL[i];
    }

    State initial_state;
    initial_state.stacks.assign(N_GLOBAL, vector<vector<int>>(N_GLOBAL));

    for (int r = 0; r < N_GLOBAL; ++r) {
        for (int c = 0; c < N_GLOBAL; ++c) {
            char ch = GRID_GLOBAL[r][c];
            if (ch == '#') {
                IS_WALL[r][c] = true;
            } else if (ch >= 'a' && ch <= 'l') {
                int color = ch - 'a';
                initial_state.stacks[r][c].push_back(color);
            } else if (ch >= 'A' && ch <= 'L') {
                int color = ch - 'A';
                IS_NEST[r][c] = color;
                NEST_POS[color] = {r, c};
                HAS_NEST[color] = true;
            }
        }
    }

    int max_c = -1;
    for (int c = 0; c < 12; ++c) {
        if (HAS_NEST[c]) max_c = max(max_c, c);
    }
    if (max_c != -1) {
        K_GLOBAL = max(K_GLOBAL, max_c + 1);
    }

    initial_state.top_color.assign(N_GLOBAL, vector<int>(N_GLOBAL, -1));
    initial_state.slimes_by_color.resize(K_GLOBAL);

    for (int r = 0; r < N_GLOBAL; ++r) {
        for (int c = 0; c < N_GLOBAL; ++c) {
            if (!initial_state.stacks[r][c].empty()) {
                int tc = initial_state.stacks[r][c].back();
                initial_state.top_color[r][c] = tc;
                initial_state.slimes_by_color[tc].insert({r, c});
            }
        }
    }

    for (int c = 0; c < K_GLOBAL; ++c) {
        if (HAS_NEST[c]) {
            get_dist_map_ptr(NEST_POS[c].first, NEST_POS[c].second);
            for (int r = 0; r < N_GLOBAL; ++r) {
                for (int col = 0; col < N_GLOBAL; ++col) {
                    NEST_DIST[c][r][col] = DIST_MAP_CACHE[NEST_POS[c].first][NEST_POS[c].second][r][col];
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

    mt19937 rng(42);

    // 1巡目: 完全シミュレーション (配列キャッシュにより数十ミリ秒で即座に完走)
    State best_state = initial_state;
    simulate_full(best_state, rng, false, start_time);
    int best_remaining = best_state.total_remaining_slimes();
    int best_ops = best_state.ans.size();

    // 2巡目以降: 1.90秒まで確率的探索を反復して手数を圧縮
    while (true) {
        auto now = chrono::steady_clock::now();
        if (chrono::duration<double>(now - start_time).count() >= PARAMS.time_limit) break;

        State cur = initial_state;
        simulate_full(cur, rng, true, start_time);
        int cur_remaining = cur.total_remaining_slimes();
        int cur_ops = cur.ans.size();

        if (cur_remaining < best_remaining) {
            best_remaining = cur_remaining;
            best_ops = cur_ops;
            best_state = move(cur);
        } else if (cur_remaining == best_remaining && cur_ops < best_ops) {
            best_ops = cur_ops;
            best_state = move(cur);
        }
    }

    // 解の出力
    for (auto& cmd : best_state.ans) {
        cout << cmd.r << " " << cmd.c << " " << cmd.k << " " << cmd.d << " " << cmd.l << "\n";
    }

    cout.flush();
    _Exit(0);
}