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
#include <sstream>
#include <chrono>
#include <functional>
#include <unordered_set>
#include <array>
#include <cstdint>

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
    // Cheap path-quality terms; kept as tie-breakers so they cannot override
    // a genuine reduction in remaining jump distance.
    int bonus_mobility = 3;
    int penalty_dead_end = 12;
    int bonus_safe_height = 4;

    // Chokudai-style mixed lookahead.  20..40% is explored by the tuner.
    int chokudai_mix_percent = 25;
    int chokudai_depth = 3;
    int chokudai_beam = 6;
    int chokudai_branch = 18;

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

static chrono::steady_clock::time_point SOLVER_DEADLINE;
static bool SOLVER_HAS_DEADLINE = false;

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

    bool record_move(int r, int c, int k, char d, int l, int tr, int tc) {
        int cur_h = stacks[r][c].size();
        if (r < 0 || r >= N_GLOBAL || c < 0 || c >= N_GLOBAL) return false;
        if (k < 0 || k >= cur_h || l < 1 || l > k + 1) return false;
        int di = 0, dj = 0;
        if (d == 'U') di = -1;
        else if (d == 'D') di = 1;
        else if (d == 'L') dj = -1;
        else if (d == 'R') dj = 1;
        else return false;
        int ar = r + di * l, ac = c + dj * l;
        if (ar != tr || ac != tc) return false;
        if (ar < 0 || ar >= N_GLOBAL || ac < 0 || ac >= N_GLOBAL) return false;
        for (int z = 1; z <= l; ++z) {
            int rr = r + di * z, cc = c + dj * z;
            if (rr < 0 || rr >= N_GLOBAL || cc < 0 || cc >= N_GLOBAL || IS_WALL[rr][cc]) return false;
        }
        if ((int)stacks[tr][tc].size() + (cur_h - k) > 8) return false;

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
        return true;
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
            if ((int)ans.size() >= PARAMS.max_ops || time_exceeded()) break;
            fired_in_round = false;
            for (int r = 0; r < N_GLOBAL; ++r) {
                for (int c = 0; c < N_GLOBAL; ++c) {
                    while (exec_single_catapult(r, c)) {
                        if (time_exceeded()) return any_fired;
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

    bool time_exceeded() const {
        return SOLVER_HAS_DEADLINE && chrono::steady_clock::now() >= SOLVER_DEADLINE;
    }

    // A compact Chokudai-style beam.  It is deliberately used as a
    // *decision oracle* inside the normal solver rather than as a separate
    // full solver, so its good moves and the existing greedy/catapult logic
    // are naturally mixed.
    using ChokMove = tuple<int,int,int,char,int,int,int>;

    long long chokudai_state_score(int depth) const {
        long long s = 0;
        int towers = 0;
        for (int c = 0; c < K_GLOBAL; ++c) {
            for (auto [r,col] : slimes_by_color[c]) {
                if (stacks[r][col].empty()) continue;
                int h = (int)stacks[r][col].size();
                int d = NEST_DIST[c][r][col];
                if (d >= INF) d = 1000;
                s += (long long)d * 24;
                s += (long long)h * 3;
                if (h >= 7) s += 8;
                ++towers;
            }
        }
        s += (long long)towers * 7;
        s += (long long)depth * 45;
        return s;
    }

    vector<ChokMove> chokudai_moves(int limit) const {
        struct Scored { long long sc; ChokMove mv; };
        vector<Scored> v;
        v.reserve(N_GLOBAL*N_GLOBAL*8);
        for (int r=0;r<N_GLOBAL;++r) for (int c=0;c<N_GLOBAL;++c) {
            int h=(int)stacks[r][c].size();
            if (h==0) continue;
            int color=stacks[r][c].back();
            int same=0;
            for(int i=h-1;i>=0 && stacks[r][c][i]==color;--i) ++same;
            int curd=NEST_DIST[color][r][c];
            if(curd>=INF) continue;
            for(int m=same;m>=1;--m){
                int k=h-m;
                int maxl=k+1;
                for(auto &d:DIRECTIONS) for(int l=1;l<=maxl;++l){
                    int tr=r+d.dr*l,tc=c+d.dc*l;
                    if(tr<0||tr>=N_GLOBAL||tc<0||tc>=N_GLOBAL||IS_WALL[tr][tc]) break;
                    if((int)stacks[tr][tc].size()+m>8) continue;
                    int nd=NEST_DIST[color][tr][tc];
                    if(nd>=INF) continue;
                    bool merge=!stacks[tr][tc].empty() && stacks[tr][tc].back()==color;
                    long long sc=(long long)(nd-curd)*40;
                    if(merge) sc-=180;
                    if(tr==NEST_POS[color].first && tc==NEST_POS[color].second) sc-=10000;
                    sc += (long long)l*2;
                    sc += (long long)max(0,(int)stacks[tr][tc].size()+m-6)*12;
                    v.push_back({sc,{r,c,k,d.name,l,tr,tc}});
                }
            }
        }
        sort(v.begin(),v.end(),[](const Scored&a,const Scored&b){return a.sc<b.sc;});
        vector<ChokMove> res;
        unordered_set<long long> seen;
        for(auto &x:v){
            auto [r,c,k,d,l,tr,tc]=x.mv;
            long long key=((((((long long)r*20+c)*9+k)*4+(d=='U'?0:d=='R'?1:d=='D'?2:3))*9+l)*20+tr)*20+tc;
            if(seen.insert(key).second){
                res.push_back(x.mv);
                if((int)res.size()>=limit) break;
            }
        }
        return res;
    }

    bool choose_chokudai_move(ChokMove &out) {
        if (time_exceeded()) return false;
        int depth_lim=max(1,min(3,PARAMS.chokudai_depth));
        int beam=max(2,min(10,PARAMS.chokudai_beam));
        int branch=max(6,min(30,PARAMS.chokudai_branch));

        struct Node {
            Solver st;
            ChokMove first;
            long long score;
            int depth;
        };
        vector<Node> layer;
        auto first_moves=chokudai_moves(branch);
        for(auto &mv:first_moves){
            if(time_exceeded()) return false;
            Solver ns=*this;
            ns.ans.clear();
            ns.global_recent_moves.clear();
            ns.recent_history_limit=PARAMS.recent_history_len;
            auto [r,c,k,d,l,tr,tc]=mv;
            if(!ns.record_move(r,c,k,d,l,tr,tc)) continue;
            ns.run_catapults_chain();
            long long sc=ns.chokudai_state_score(1);
            layer.push_back({std::move(ns),mv,sc,1});
        }
        if(layer.empty()) return false;
        sort(layer.begin(),layer.end(),[](const Node&a,const Node&b){return a.score<b.score;});
        if((int)layer.size()>beam) layer.resize(beam);

        ChokMove best_first=layer.front().first;
        long long best_score=layer.front().score;
        for(int dep=2;dep<=depth_lim && !layer.empty();++dep){
            vector<Node> next;
            for(auto &node:layer){
                if(time_exceeded()) break;
                auto moves=node.st.chokudai_moves(branch);
                int expanded=0;
                for(auto &mv:moves){
                    if(time_exceeded()) break;
                    Solver ns=node.st;
                    ns.ans.clear();
                    ns.global_recent_moves.clear();
                    ns.recent_history_limit=PARAMS.recent_history_len;
                    auto [r,c,k,d,l,tr,tc]=mv;
                    if(!ns.record_move(r,c,k,d,l,tr,tc)) continue;
                    ns.run_catapults_chain();
                    long long sc=ns.chokudai_state_score(dep);
                    next.push_back({std::move(ns),node.first,sc,dep});
                    if(++expanded>=branch) break;
                }
            }
            sort(next.begin(),next.end(),[](const Node&a,const Node&b){return a.score<b.score;});
            if((int)next.size()>beam) next.resize(beam);
            if(!next.empty() && next.front().score<best_score){ best_score=next.front().score; best_first=next.front().first; }
            layer.swap(next);
        }
        out=best_first;
        return true;
    }

    void solve() {
        set<pair<int, int>> stuck_slimes;
        set<pair<int, int>> skipped_slimes;
        vector<vector<int>> height8_pending(N_GLOBAL, vector<int>(N_GLOBAL, 0));
        vector<vector<int>> combo_cooldown(N_GLOBAL, vector<int>(N_GLOBAL, 0));
        recent_history_limit = PARAMS.recent_history_len;
        int last_remaining = total_remaining_slimes();
        int stagnant_rounds = 0;

        while ((int)ans.size() < PARAMS.max_ops && !time_exceeded()) {
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

            // Mix Chokudai decisions into the ordinary solver.  A period of 4
            // means roughly one quarter of decision points use lookahead;
            // the rest continue through the proven greedy/catapult path.
            if (PARAMS.chokudai_mix_percent > 0 && cur_ans_len > 0 &&
                uniform_int_distribution<int>(0,99)(rng) < PARAMS.chokudai_mix_percent &&
                !time_exceeded()) {
                ChokMove cm;
                if (choose_chokudai_move(cm)) {
                    auto [rr,cc,kk,dd,ll,trr,tcc]=cm;
                    if (record_move(rr,cc,kk,dd,ll,trr,tcc)) {
                        run_catapults_chain();
                        continue;
                    }
                }
            }

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
                // A combo is planned against the current state, but act1 changes the
                // state seen by act2/act3. Execute transactionally: either all three
                // commands are legal in sequence, or none of them is committed.
                auto backup_stacks = stacks;
                auto backup_top_color = top_color;
                auto backup_slimes_by_color = slimes_by_color;
                auto backup_ans = ans;
                auto backup_recent = global_recent_moves;
                auto backup_combo_cooldown = combo_cooldown;

                combo_cooldown[cur_r][cur_c] = ans.size() + PARAMS.combo_cooldown_steps;
                combo_cooldown[get<5>(act1)][get<6>(act1)] = ans.size() + PARAMS.combo_cooldown_steps;

                bool ok = true;
                ok = ok && record_move(get<0>(act1), get<1>(act1), get<2>(act1), get<3>(act1), get<4>(act1), get<5>(act1), get<6>(act1));
                ok = ok && record_move(get<0>(act2), get<1>(act2), get<2>(act2), get<3>(act2), get<4>(act2), get<5>(act2), get<6>(act2));
                ok = ok && record_move(get<0>(act3), get<1>(act3), get<2>(act3), get<3>(act3), get<4>(act3), get<5>(act3), get<6>(act3));

                if (ok) {
                    run_catapults_chain();
                    stuck_slimes.clear();
                    skipped_slimes.clear();
                    continue;
                }

                stacks = std::move(backup_stacks);
                top_color = std::move(backup_top_color);
                slimes_by_color = std::move(backup_slimes_by_color);
                ans = std::move(backup_ans);
                global_recent_moves = std::move(backup_recent);
                combo_cooldown = std::move(backup_combo_cooldown);
                combo_found = false;
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

                            // Cheap mobility / dead-end evaluation.  This is only a
                            // tie-breaker: it never defeats a strictly better jump-distance
                            // reduction.  The destination itself is evaluated as the state
                            // from which the next move will start.
                            int mobility = 0;
                            int open_same = 0;
                            for (auto &nd : DIRECTIONS) {
                                int nr = tr + nd.dr, nc = tc + nd.dc;
                                if (nr < 0 || nr >= N_GLOBAL || nc < 0 || nc >= N_GLOBAL || IS_WALL[nr][nc]) continue;
                                int nh = (int)stacks[nr][nc].size();
                                // Approximate post-landing capacity.  The moved block
                                // itself occupies the destination, so only count cells
                                // that can accept at least one slime later.
                                if (nh < 8) ++mobility;
                                if (!stacks[nr][nc].empty() && stacks[nr][nc].back() == color) ++open_same;
                            }
                            int path_bonus = mobility * PARAMS.bonus_mobility;
                            if (mobility == 0) path_bonus -= PARAMS.penalty_dead_end;
                            // Heights 7/8 are dangerous when landing on a different color;
                            // a lower or same-color landing keeps more future flexibility.
                            if (!merges_same_color && merged_height >= 7) {
                                path_bonus -= (merged_height - 6) * PARAMS.bonus_safe_height;
                            }
                            path_bonus += min(open_same, 3) * PARAMS.bonus_safe_height;
                            tie_breaker_bonus += path_bonus;

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


// ============================================================================
// Per-instance auto tuner
// - Runs the same solver in-process with many HyperParams candidates.
// - Keeps the best (shortest) legal solution found within the time budget.
// - Designed for later replacement/extension with Chokudai Search.
// ============================================================================
struct CandidateResult {
    long long ops = (1LL << 60);
    vector<MoveCommand> ans;
    HyperParams hp;
    bool complete = false;
};

static void reset_global_state_for_rerun() {
    memset(IS_WALL, 0, sizeof(IS_WALL));
    memset(HAS_NEST, 0, sizeof(HAS_NEST));
    memset(DIST_MAP_CALCULATED, 0, sizeof(DIST_MAP_CALCULATED));
    memset(JUMP_DIST_CALCULATED, 0, sizeof(JUMP_DIST_CALCULATED));
    for (int r = 0; r < 20; ++r) {
        for (int c = 0; c < 20; ++c) IS_NEST[r][c] = -1;
    }
    for (int c = 0; c < 12; ++c) {
        NEST_POS[c] = {-1, -1};
    }
}

static CandidateResult run_candidate(const string& input, const HyperParams& hp, chrono::steady_clock::time_point deadline) {
    PARAMS = hp;
    SOLVER_DEADLINE = deadline;
    SOLVER_HAS_DEADLINE = true;
    reset_global_state_for_rerun();

    istringstream iss(input);
    streambuf* old_in = cin.rdbuf(iss.rdbuf());

    Solver solver;
    solver.read_input();
    solver.init();
    solver.solve();

    cin.rdbuf(old_in);
    SOLVER_HAS_DEADLINE = false;

    CandidateResult res;
    res.ops = (long long)solver.ans.size();
    res.complete = (solver.total_remaining_slimes() == 0);
    res.ans = std::move(solver.ans);
    res.hp = hp;
    return res;
}

static bool better_result(const CandidateResult& a, const CandidateResult& b) {
    return a.ops < b.ops;
}


// ============================================================================
// Independent Chokudai Search
// - Never replaces the incumbent unless it reaches a complete solution with
//   strictly fewer operations.
// - Nodes are real Solver states, so all move legality/catapult effects are
//   evaluated by the same transition code as the final solver.
// - Each leaf gets a normal-solver rollout.  This is intentionally asymmetric:
//   Chokudai chooses promising prefixes, while the proven solver finishes them.
// ============================================================================
struct ChokudaiNode {
    Solver st;
    long long heuristic = (1LL << 60);
    int depth = 0;
};

static long long chokudai_heuristic(const Solver& st) {
    long long rem = st.total_remaining_slimes();
    long long h = rem * 1000LL;
    long long dist_sum = 0;
    long long tower_bonus = 0;
    for (int c = 0; c < K_GLOBAL; ++c) {
        for (auto [r, col] : st.slimes_by_color[c]) {
            if (st.stacks[r][col].empty()) continue;
            int hh = (int)st.stacks[r][col].size();
            int d = NEST_DIST[c][r][col];
            if (d >= INF) d = 1000;
            dist_sum += d;
            if (hh >= 7) tower_bonus += 20;
            if (hh >= 8) tower_bonus += 30;
            if (st.stacks[r][col].back() == c) tower_bonus += 8;
        }
    }
    // Lower is better.  The remaining count dominates, then true nest
    // distance, while useful tall/color-aligned towers are rewarded.
    h += dist_sum * 12;
    h -= tower_bonus;
    h += (long long)st.ans.size() * 2;
    return h;
}

static vector<Solver::ChokMove> chokudai_expand_moves(const Solver& st, int limit) {
    // Reuse the same move generator used by the existing lookahead, but do
    // not let a stochastic mix decide which moves survive the Chokudai beam.
    auto v = st.chokudai_moves(max(limit, 1));
    return v;
}

static CandidateResult run_chokudai_candidate(const string& input,
                                               const HyperParams& hp,
                                               chrono::steady_clock::time_point deadline,
                                               int incumbent_ops) {
    PARAMS = hp;
    SOLVER_DEADLINE = deadline;
    SOLVER_HAS_DEADLINE = true;
    reset_global_state_for_rerun();

    istringstream iss(input);
    streambuf* old_in = cin.rdbuf(iss.rdbuf());

    Solver root;
    root.read_input();
    root.init();

    CandidateResult best;
    best.hp = hp;
    best.ops = incumbent_ops;

    // The ordinary solver is used only as a completion oracle.  It is never
    // allowed to worsen the incumbent.
    if (!root.time_exceeded()) {
        Solver seed = root;
        seed.solve();
        if (seed.total_remaining_slimes() == 0 && (long long)seed.ans.size() < best.ops) {
            best.complete = true;
            best.ops = seed.ans.size();
            best.ans = seed.ans;
        }
    }

    const int depth_limit = max(1, min(4, hp.chokudai_depth));
    const int beam_width = max(2, min(12, hp.chokudai_beam));
    const int branch = max(6, min(36, hp.chokudai_branch));

    // Chokudai Search: one priority queue per depth.  We repeatedly visit
    // shallow queues, expand their best states, and feed children into the
    // next queue.  Thus a promising shallow prefix can be revisited many
    // times instead of being consumed by a single depth-first pass.
    struct Node {
        Solver st;
        long long score;
        int depth;
    };
    struct Cmp {
        bool operator()(const Node& a, const Node& b) const {
            if (a.score != b.score) return a.score > b.score;
            return a.st.ans.size() > b.st.ans.size();
        }
    };

    vector<priority_queue<Node, vector<Node>, Cmp>> q(depth_limit + 1);
    unordered_set<uint64_t> seen;
    seen.reserve(4096);

    auto state_key = [](const Solver& st) -> uint64_t {
        // Compact Zobrist-like deterministic hash of the complete stack state.
        // Collisions only suppress duplicate prefixes; they cannot invalidate
        // an output because every accepted node still carries its full state.
        uint64_t h = 1469598103934665603ULL;
        for (int r = 0; r < N_GLOBAL; ++r) {
            for (int c = 0; c < N_GLOBAL; ++c) {
                h ^= (uint64_t)(r * 23 + c * 29 + 1);
                h *= 1099511628211ULL;
                for (int x : st.stacks[r][c]) {
                    h ^= (uint64_t)(x + 1);
                    h *= 1099511628211ULL;
                }
                h ^= 0x9e3779b97f4a7c15ULL;
                h *= 1099511628211ULL;
            }
        }
        return h;
    };

    auto push_node = [&](Solver&& st, int depth) {
        if (root.time_exceeded()) return;
        uint64_t key = state_key(st);
        if (!seen.insert(key).second) return;
        long long sc = chokudai_heuristic(st);
        q[depth].push(Node{std::move(st), sc, depth});
        // Keep each depth bounded. priority_queue has no cheap arbitrary
        // deletion, so a small overflow is tolerated and pruned on pop.
    };

    auto seed_moves = chokudai_expand_moves(root, branch);
    for (auto &mv : seed_moves) {
        if (root.time_exceeded()) break;
        Solver ns = root;
        ns.ans.clear();
        ns.global_recent_moves.clear();
        auto [r,c,k,d,l,tr,tc] = mv;
        if (!ns.record_move(r,c,k,d,l,tr,tc)) continue;
        ns.run_catapults_chain();
        push_node(std::move(ns), 1);
    }

    // If a shallow state already solves the case, accept it only if it beats
    // the incumbent.  In normal operation the rollout below is stronger.
    while (!root.time_exceeded()) {
        bool expanded = false;

        // Fairly cycle through depths, as in classical Chokudai Search.
        for (int dep = 1; dep <= depth_limit && !root.time_exceeded(); ++dep) {
            if (q[dep].empty()) continue;
            expanded = true;

            Node node = std::move(const_cast<Node&>(q[dep].top()));
            q[dep].pop();

            // Complete the prefix with the proven solver.  This is the key
            // incumbent protection: a prefix matters only if its rollout
            // actually produces a better complete answer.
            Solver roll = node.st;
            roll.solve();
            if (roll.total_remaining_slimes() == 0) {
                long long ops = roll.ans.size();
                if (ops < best.ops) {
                    best.complete = true;
                    best.ops = ops;
                    best.ans = roll.ans;
                }
            }
            if (root.time_exceeded()) break;

            if (dep >= depth_limit) continue;

            auto moves = chokudai_expand_moves(node.st, branch);
            int emitted = 0;
            for (auto &mv : moves) {
                if (root.time_exceeded()) break;
                Solver ns = node.st;
                // Keep the complete prefix: the rollout result must contain
                // every move from the initial state, not only the suffix.
                // The state already carries the matching recent-move history.
                auto [r,c,k,d,l,tr,tc] = mv;
                if (!ns.record_move(r,c,k,d,l,tr,tc)) continue;
                ns.run_catapults_chain();
                push_node(std::move(ns), dep + 1);
                if (++emitted >= branch) break;
            }

            // Bound the useful population at this depth by keeping the best
            // beam_width * 2 nodes alive.  Older/worse nodes are discarded
            // lazily when popped, so the memory footprint stays small.
            if ((int)q[dep + 1].size() > beam_width * 2) {
                // priority_queue cannot trim its bottom efficiently; instead
                // allow the bounded queue to be consumed naturally.  The
                // branch count is already small enough for N<=20.
            }
        }

        if (!expanded) {
            // Restart from root when all queues are exhausted.  This makes the
            // full budget useful even after a beam has converged.
            if (root.time_exceeded()) break;
            auto moves = chokudai_expand_moves(root, branch);
            for (auto &mv : moves) {
                if (root.time_exceeded()) break;
                Solver ns = root;
                // Keep the complete prefix: the rollout result must contain
                // every move from the initial state, not only the suffix.
                // The state already carries the matching recent-move history.
                auto [r,c,k,d,l,tr,tc] = mv;
                if (!ns.record_move(r,c,k,d,l,tr,tc)) continue;
                ns.run_catapults_chain();
                push_node(std::move(ns), 1);
            }
        }
    }

    cin.rdbuf(old_in);
    SOLVER_HAS_DEADLINE = false;

    // If no Chokudai completion improved the incumbent, return an explicitly
    // incomplete result.  The caller therefore cannot accidentally replace
    // the incumbent with a worse solution.
    if (!best.complete || best.ops >= incumbent_ops) {
        best.complete = false;
        best.ops = (1LL << 60);
        best.ans.clear();
    }
    return best;
}

int main(int argc, char* argv[]) {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    ostringstream oss;
    oss << cin.rdbuf();
    const string input = oss.str();
    if (input.empty()) return 0;

    // ================================================================
    // Adaptive per-instance optimizer.
    //  * Baseline is executed first and is an absolute incumbent.
    //  * Every later run is raced against the current incumbent by setting
    //    max_ops = incumbent-1.  Bad candidates therefore terminate early.
    //  * The available wall-clock budget is measured, and the optimizer
    //    automatically estimates how many full evaluations fit into it.
    //  * Search proceeds from broad exploration -> elite refinement ->
    //    coordinate/local search -> final intensification.
    // ================================================================
    HyperParams base;
    base.max_ops = 99990;
    base.combo_cost_min = 2;
    base.combo_h_min = 4;
    base.combo_cooldown_steps = 30;
    base.height8_pending_steps = 15;
    base.recent_history_len = 50;
    base.bonus_catapult_align = 15;
    base.bonus_pass_through_same = 8;
    base.bonus_pass_through_diff = 15;
    base.bonus_merge_same = 220;
    base.bonus_merge_height = 12;
    base.penalty_repeated_short_move = 6;
    base.bonus_mobility = 3;
    base.penalty_dead_end = 12;
    base.bonus_safe_height = 4;
    // Hard baseline intentionally stays on the proven non-Chokudai path.
    // Chokudai is mixed only into the adaptive candidates below.
    base.chokudai_mix_percent = 0;
    base.chokudai_depth = 3;
    base.chokudai_beam = 6;
    base.chokudai_branch = 18;
    base.seed = 42;

    // argv[1] may specify the contest-side budget.  Default is 1.90 sec.
    double total_budget = 600;
    if (argc >= 2) {
        try { total_budget = stod(argv[1]); } catch (...) {}
    }
    total_budget = max(0.05, total_budget);

    // Hard wall-clock deadline.  Only a tiny fixed margin is kept for the
    // final stdout flush/process teardown; the optimizer itself is allowed
    // to use essentially all of the requested budget.
    // The caller-provided budget is the actual search budget.  Do not
    // subtract an arbitrary margin: the search loop itself stops at this
    // exact deadline, while final output is emitted only after the search.
    const double usable_budget = total_budget;
    const auto global_start = chrono::steady_clock::now();
    const auto global_deadline = global_start + chrono::duration_cast<chrono::steady_clock::duration>(chrono::duration<double>(usable_budget));
    auto elapsed = [&]() {
        return chrono::duration<double>(chrono::steady_clock::now() - global_start).count();
    };
    auto remaining_time = [&]() {
        return max(0.0, chrono::duration<double>(global_deadline - chrono::steady_clock::now()).count());
    };

    // The search is deliberately split into two phases: Adaptive first,
    // then Chokudai.  Reserve about one third of the total budget for
    // Chokudai, while letting Adaptive consume the first two thirds.
    const auto adaptive_deadline = global_start +
        chrono::duration_cast<chrono::steady_clock::duration>(
            chrono::duration<double>(usable_budget * (2.0 / 5.0)));
    auto remaining_adaptive_time = [&]() {
        return max(0.0, chrono::duration<double>(adaptive_deadline - chrono::steady_clock::now()).count());
    };

    CandidateResult best;
    best.ops = (1LL << 60);

    // Candidate execution can be capped just below the incumbent.  This is a
    // very effective form of racing: once a candidate is clearly worse than
    // the best solution, it does not consume the full solver runtime.
    auto run_raced_until = [&](const HyperParams& requested, const auto& deadline) -> CandidateResult {
        HyperParams hp = requested;
        if (best.ops < (1LL << 50)) {
            hp.max_ops = (int)max(1LL, best.ops - 1);
        } else {
            hp.max_ops = base.max_ops;
        }
        return run_candidate(input, hp, deadline);
    };

    auto run_raced_adaptive = [&](const HyperParams& requested) -> CandidateResult {
        return run_raced_until(requested, adaptive_deadline);
    };

    auto consider = [&](HyperParams hp) -> bool {
        if (remaining_adaptive_time() <= 0.0) return false;
        CandidateResult r = run_raced_adaptive(hp);
        // A capped/incomplete run cannot beat the incumbent and is ignored.
        if (r.complete && r.ops < best.ops) {
            best = std::move(r);
        }
        return true;
    };

    // ---------------------------------------------------------------
    // 0. HARD MINIMUM GUARANTEE: conventional solver FIRST.
    // ---------------------------------------------------------------
    {
        CandidateResult r = run_candidate(input, base, adaptive_deadline);
        best = std::move(r);
    }

    if (best.ops >= (1LL << 50)) return 0;

    // ---------------------------------------------------------------
    // Adaptive stage comes FIRST.  Chokudai is intentionally not mixed into
    // these candidates; its dedicated budget is reserved for the second
    // phase after Adaptive has produced the incumbent.
    // ---------------------------------------------------------------

    // ---------------------------------------------------------------
    // Parameter ranges.  These are deliberately broad, while the search
    // distribution is adaptive rather than a Cartesian grid.
    // ---------------------------------------------------------------
    struct Range { int lo, hi; };
    const Range RH{3,8}, RCD{10,135}, RP{4,80}, RHIST{15,130};
    const Range RCAT{3,40}, RSAME{0,24}, RDIFF{0,30}, RMERGE{0,360};
    const Range RMH{0,28}, RREP{0,20};
    const Range RMOB{0,14}, RDEAD{0,34}, RSAFE{0,14}, RCHOK{20,100};
    auto clampi = [](int x, const Range& r) { return max(r.lo, min(r.hi, x)); };

    mt19937 rng(0x0725A17u ^ (uint32_t)input.size());
    auto ri = [&](int lo, int hi) { return uniform_int_distribution<int>(lo,hi)(rng); };
    auto rf = [&]() { return uniform_real_distribution<double>(0.0,1.0)(rng); };

    struct Key {
        array<int,14> a;
        bool operator==(const Key& o) const { return a == o.a; }
    };
    struct KeyHash {
        size_t operator()(const Key& k) const {
            uint64_t h=1469598103934665603ULL;
            for(int v:k.a){h^=(uint64_t)(v+1009);h*=1099511628211ULL;}
            return (size_t)h;
        }
    };
    auto key_of = [](const HyperParams& x) {
        return Key{{x.combo_h_min,x.combo_cooldown_steps,x.height8_pending_steps,
                    x.recent_history_len,x.bonus_catapult_align,
                    x.bonus_pass_through_same,x.bonus_pass_through_diff,
                    x.bonus_merge_same,x.bonus_merge_height,
                    x.penalty_repeated_short_move,x.bonus_mobility,x.penalty_dead_end,x.bonus_safe_height}};
    };
    unordered_set<Key,KeyHash> seen;
    seen.insert(key_of(base));

    vector<CandidateResult> elite;
    const int ELITE_MAX=10;

    auto insert_elite = [&](CandidateResult r) {
        if (r.ops >= best.ops && r.ops >= (1LL<<50)) return;
        elite.push_back(std::move(r));
        sort(elite.begin(),elite.end(),[](const CandidateResult&a,const CandidateResult&b){return a.ops<b.ops;});
        // Deduplicate elite by parameter vector.
        vector<CandidateResult> tmp;
        unordered_set<Key,KeyHash> local;
        for (auto &x:elite) {
            if (local.insert(key_of(x.hp)).second) {
                tmp.push_back(std::move(x));
                if ((int)tmp.size()>=ELITE_MAX) break;
            }
        }
        elite.swap(tmp);
    };

    auto eval_unique = [&](HyperParams hp) -> bool {
        if (remaining_adaptive_time() <= 0.0) return false;
        Key k=key_of(hp);
        if (!seen.insert(k).second) return true;
        CandidateResult r=run_raced_adaptive(hp);
        if (r.complete && r.ops < best.ops) best=r;
        if (r.complete) insert_elite(std::move(r));
        return true;
    };

    auto random_hp = [&]() {
        HyperParams x=base;
        x.combo_h_min=ri(RH.lo,RH.hi);
        x.combo_cooldown_steps=ri(RCD.lo,RCD.hi);
        x.height8_pending_steps=ri(RP.lo,RP.hi);
        x.recent_history_len=ri(RHIST.lo,RHIST.hi);
        x.bonus_catapult_align=ri(RCAT.lo,RCAT.hi);
        x.bonus_pass_through_same=ri(RSAME.lo,RSAME.hi);
        x.bonus_pass_through_diff=ri(RDIFF.lo,RDIFF.hi);
        x.bonus_merge_same=ri(RMERGE.lo,RMERGE.hi);
        x.bonus_merge_height=ri(RMH.lo,RMH.hi);
        x.penalty_repeated_short_move=ri(RREP.lo,RREP.hi);
        x.bonus_mobility=ri(RMOB.lo,RMOB.hi);
        x.penalty_dead_end=ri(RDEAD.lo,RDEAD.hi);
        x.bonus_safe_height=ri(RSAFE.lo,RSAFE.hi);
        x.chokudai_mix_percent=0;
        return x;
    };

    // Log-scaled / triangular sampling around the current best.  This gives
    // much more density to useful regions than uniform grid enumeration.
    auto mutate = [&](const HyperParams& s, double strength) {
        HyperParams x=s;
        auto step=[&](int lo,int hi,int cur,double scale) {
            int span=max(1,(int)round((hi-lo)*scale*strength));
            return clampi(cur+ri(-span,span),Range{lo,hi});
        };
        if (rf()<0.70) x.combo_h_min=clampi(x.combo_h_min+ri(-1,1),RH);
        if (rf()<0.75) x.combo_cooldown_steps=step(RCD.lo,RCD.hi,x.combo_cooldown_steps,0.18);
        if (rf()<0.75) x.height8_pending_steps=step(RP.lo,RP.hi,x.height8_pending_steps,0.18);
        if (rf()<0.55) x.recent_history_len=step(RHIST.lo,RHIST.hi,x.recent_history_len,0.18);
        if (rf()<0.45) x.bonus_catapult_align=step(RCAT.lo,RCAT.hi,x.bonus_catapult_align,0.20);
        if (rf()<0.45) x.bonus_pass_through_same=step(RSAME.lo,RSAME.hi,x.bonus_pass_through_same,0.22);
        if (rf()<0.45) x.bonus_pass_through_diff=step(RDIFF.lo,RDIFF.hi,x.bonus_pass_through_diff,0.22);
        if (rf()<0.55) x.bonus_merge_same=step(RMERGE.lo,RMERGE.hi,x.bonus_merge_same,0.16);
        if (rf()<0.45) x.bonus_merge_height=step(RMH.lo,RMH.hi,x.bonus_merge_height,0.22);
        if (rf()<0.45) x.penalty_repeated_short_move=step(RREP.lo,RREP.hi,x.penalty_repeated_short_move,0.22);
        if (rf()<0.45) x.bonus_mobility=step(RMOB.lo,RMOB.hi,x.bonus_mobility,0.25);
        if (rf()<0.45) x.penalty_dead_end=step(RDEAD.lo,RDEAD.hi,x.penalty_dead_end,0.25);
        if (rf()<0.45) x.bonus_safe_height=step(RSAFE.lo,RSAFE.hi,x.bonus_safe_height,0.25);
        x.chokudai_mix_percent=0;
        return x;
    };

    auto crossover = [&](const HyperParams& a,const HyperParams& b) {
        HyperParams x=a;
        if(ri(0,1))x.combo_h_min=b.combo_h_min;
        if(ri(0,1))x.combo_cooldown_steps=b.combo_cooldown_steps;
        if(ri(0,1))x.height8_pending_steps=b.height8_pending_steps;
        if(ri(0,1))x.recent_history_len=b.recent_history_len;
        if(ri(0,1))x.bonus_catapult_align=b.bonus_catapult_align;
        if(ri(0,1))x.bonus_pass_through_same=b.bonus_pass_through_same;
        if(ri(0,1))x.bonus_pass_through_diff=b.bonus_pass_through_diff;
        if(ri(0,1))x.bonus_merge_same=b.bonus_merge_same;
        if(ri(0,1))x.bonus_merge_height=b.bonus_merge_height;
        if(ri(0,1))x.penalty_repeated_short_move=b.penalty_repeated_short_move;
        if(ri(0,1))x.bonus_mobility=b.bonus_mobility;
        if(ri(0,1))x.penalty_dead_end=b.penalty_dead_end;
        if(ri(0,1))x.bonus_safe_height=b.bonus_safe_height;
        x.chokudai_mix_percent=0;
        return x;
    };

    // ---------------------------------------------------------------
    // Automatically estimate candidate throughput.  We use a few diverse
    // probes, but never allow probing to consume the whole budget.
    // ---------------------------------------------------------------
    const double t_before_probe=elapsed();
    int probes=0;
    vector<HyperParams> probe_seed;
    {
        HyperParams x=base; x.combo_h_min=5; x.combo_cooldown_steps=60; x.height8_pending_steps=30;
        probe_seed.push_back(x);
        x=base; x.combo_h_min=6; x.combo_cooldown_steps=45; x.height8_pending_steps=55;
        probe_seed.push_back(x);
        x=base; x.combo_h_min=4; x.combo_cooldown_steps=90; x.height8_pending_steps=50;
        probe_seed.push_back(x);
        // Seeds from the previous good search family.
        x=base; x.combo_h_min=5; x.combo_cooldown_steps=60; x.height8_pending_steps=55; x.recent_history_len=50;
        probe_seed.push_back(x);
        x=base; x.combo_h_min=5; x.combo_cooldown_steps=45; x.height8_pending_steps=45; x.recent_history_len=50;
        probe_seed.push_back(x);
        x=base; x.combo_h_min=6; x.combo_cooldown_steps=60; x.height8_pending_steps=30; x.recent_history_len=70;
        probe_seed.push_back(x);
        for(auto &x:probe_seed){
            if(remaining_adaptive_time()<0.20) break;
            eval_unique(x); ++probes;
        }
    }
    const double probe_time=max(1e-4,elapsed()-t_before_probe);
    const double avg_probe=max(0.001,probe_time/max(1,probes));
    // Conservative estimate because racing becomes faster as incumbent improves.
    int estimated_full = max(8,(int)floor(remaining_adaptive_time()/avg_probe));

    // ---------------------------------------------------------------
    // Stage 1: broad exploration. Number of trials is derived from measured
    // throughput, not hard-coded for a particular machine.
    // ---------------------------------------------------------------
    int stage1 = max(12,min(48,estimated_full/3));
    for(int i=0;i<stage1 && remaining_adaptive_time()>0.0;++i) {
        eval_unique(random_hp());
    }

    // ---------------------------------------------------------------
    // Stage 2: elite refinement.  The elite pool is continuously improved;
    // mutation radius shrinks according to the fraction of time remaining.
    // ---------------------------------------------------------------
    while(remaining_adaptive_time()>0.0) {
        double frac=remaining_adaptive_time()/max(0.001,usable_budget*(2.0/3.0));
        if(frac<0.08) break;
        int batch = (frac>0.55 ? 14 : frac>0.30 ? 10 : 6);
        for(int i=0;i<batch && remaining_adaptive_time()>0.0;++i) {
            HyperParams x;
            if(elite.size()>=2 && rf()<0.80) {
                const auto &a=elite[ri(0,min((int)elite.size()-1,5))].hp;
                const auto &b=elite[ri(0,min((int)elite.size()-1,5))].hp;
                x=crossover(a,b);
                double strength = frac>0.55 ? 1.0 : frac>0.30 ? 0.55 : 0.25;
                x=mutate(x,strength);
            } else if(!elite.empty() && rf()<0.85) {
                x=mutate(elite.front().hp,frac>0.55?1.0:frac>0.30?0.55:0.25);
            } else x=random_hp();
            eval_unique(x);
        }

        // -----------------------------------------------------------
        // Stage 3: local coordinate refinement.  Only activate it once an
        // actual incumbent has beaten the baseline; this avoids wasting the
        // early exploration budget on a bad basin.
        // -----------------------------------------------------------
        if(!elite.empty() && remaining_adaptive_time()>0.35) {
            HyperParams c=elite.front().hp;
            static const int dirs[3]={-1,1,0};
            for(int d=0;d<14 && remaining_adaptive_time()>0.0;++d) {
                int trials= (frac>0.35 ? 2 : 1);
                for(int q=0;q<trials && remaining_adaptive_time()>0.0;++q) {
                    HyperParams x=c;
                    int s=(q==0?-1:1);
                    switch(d){
                        case 0:x.combo_h_min=clampi(x.combo_h_min+s,RH);break;
                        case 1:x.combo_cooldown_steps=clampi(x.combo_cooldown_steps+s*5,RCD);break;
                        case 2:x.height8_pending_steps=clampi(x.height8_pending_steps+s*5,RP);break;
                        case 3:x.recent_history_len=clampi(x.recent_history_len+s*10,RHIST);break;
                        case 4:x.bonus_catapult_align=clampi(x.bonus_catapult_align+s*3,RCAT);break;
                        case 5:x.bonus_pass_through_same=clampi(x.bonus_pass_through_same+s*2,RSAME);break;
                        case 6:x.bonus_pass_through_diff=clampi(x.bonus_pass_through_diff+s*2,RDIFF);break;
                        case 7:x.bonus_merge_same=clampi(x.bonus_merge_same+s*20,RMERGE);break;
                        case 8:x.bonus_merge_height=clampi(x.bonus_merge_height+s*3,RMH);break;
                        case 9:x.penalty_repeated_short_move=clampi(x.penalty_repeated_short_move+s*2,RREP);break;
                        case 10:x.bonus_mobility=clampi(x.bonus_mobility+s,RMOB);break;
                        case 11:x.penalty_dead_end=clampi(x.penalty_dead_end+s*2,RDEAD);break;
                        case 12:x.bonus_safe_height=clampi(x.bonus_safe_height+s,RSAFE);break;
                        case 13:break;
                    }
                    eval_unique(x);
                }
            }
        }

        // Final intensification automatically kicks in as time gets short.
        if(remaining_adaptive_time()<0.22 && !elite.empty()) {
            for(int z=0;z<20 && remaining_adaptive_time()>0.0;++z) {
                eval_unique(mutate(elite.front().hp,0.12));
            }
            break;
        }
    }

    // ---------------------------------------------------------------
    // Chokudai stage: starts only after Adaptive has finished.  It gets the
    // remaining wall-clock time (normally about one third of the total),
    // and is strictly incumbent-preserving: only a complete, strictly
    // better solution can replace the Adaptive result.
    // ---------------------------------------------------------------
    {
        HyperParams ch = base;
        ch.chokudai_mix_percent = 0;
        int chokudai_seed = 0;
        while (remaining_time() > 0.0) {
            ch.seed = 1009 + chokudai_seed * 7919;
            ch.chokudai_depth = 2 + (chokudai_seed % 3);
            ch.chokudai_beam = 5 + (chokudai_seed % 7);
            ch.chokudai_branch = 12 + (chokudai_seed % 17);
            CandidateResult r = run_chokudai_candidate(input, ch, global_deadline, (int)best.ops);
            if (r.complete && r.ops < best.ops) best = std::move(r);
            ++chokudai_seed;
        }
    }

    // The baseline is already in best and every replacement required strict
    // improvement, so the minimum guarantee is absolute.
    for(const auto &cmd:best.ans)
        cout<<cmd.r<<' '<<cmd.c<<' '<<cmd.k<<' '<<cmd.d<<' '<<cmd.l<<'\n';
    cout.flush();
    return 0;
}
