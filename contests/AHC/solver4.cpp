#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using Clock = std::chrono::steady_clock;

int N, M, C;
vector<int> D;
vector<vector<int>> Map;
vector<vector<int>> color_cells;
vector<vector<int>> order_id;
vector<pair<int,int>> DIR = {{0,1},{1,0},{0,-1},{-1,0}};
vector<char> DIRC = {'R','D','L','U'};

vector<pair<int,int>> hebi;
int length_snake = 5;

Clock::time_point DEADLINE;
Clock::time_point SEARCH_DEADLINE;

static constexpr double TIME_LIMIT_SEC = 1.88;
static constexpr double OUTPUT_RESERVE = 0.006; // 出力バッファ（動的補正の下限側）
static constexpr ll NEG_INF = -(1LL << 60);
static constexpr int BEAM_WIDTH_HI = 82;
static constexpr int BEAM_WIDTH_MID = 54;
static constexpr int BEAM_WIDTH_LO = 33;
static constexpr int CANDIDATE_KEEP = 19;
static constexpr int HEAT_RADIUS = 11;
static constexpr int CANDIDATE_EVAL_LIMIT = 16;
static constexpr ll STEP_PENALTY_BEAM = 20;
static constexpr ll STEP_PENALTY_DFS = 30;
static ll W_NEED_DIST = 130;
static ll W_LOOP_REP = 350;
static ll W_ONEWAY = 1400;
static ll W_WRONG_EAT = 24000;
static ll W_ENDGAME_GUIDE = 220;

static constexpr ll BASE_W_NEED_DIST = 130;
static constexpr ll BASE_W_LOOP_REP = 350;
static constexpr ll BASE_W_ONEWAY = 1400;
static constexpr ll BASE_W_WRONG_EAT = 24000;
static constexpr ll BASE_W_ENDGAME_GUIDE = 220;

int tune_moves = 0;
int tune_exact = 0;
int tune_wrong = 0;
int tune_deadend = 0;

vector<int> eaten_mark;
int eaten_token = 1;
deque<string> banned_prefixes;

uint64_t hash_body(const vector<pair<int,int>>& body);
bool in_endgame_mode(const vector<pair<int,int>>& body, int curr_len);

int map_epoch = 1;
unordered_map<uint64_t, int> memo_ff;
unordered_map<uint64_t, int> memo_lmc;
unordered_map<uint64_t, ll> memo_ps;

inline void invalidate_search_memo() {
    memo_ff.clear();
    memo_lmc.clear();
    memo_ps.clear();
}

inline void invalidate_score_memo() {
    memo_ps.clear();
}

inline uint64_t state_key_with_epoch(const vector<pair<int,int>>& body, uint64_t salt) {
    uint64_t key = hash_body(body);
    key ^= (uint64_t)map_epoch * 11400714819323198485ULL;
    key ^= salt;
    return key;
}

inline bool time_up()      { return Clock::now() >= SEARCH_DEADLINE; }
inline bool hard_time_up() { return Clock::now() >= DEADLINE; }
inline double hard_time_left_sec() {
    return chrono::duration<double>(DEADLINE - Clock::now()).count();
}
inline bool in_board(int x, int y) {
    return 0 <= x && x < N && 0 <= y && y < N;
}

inline int cell_id(int x, int y) {
    return x * N + y;
}

uint64_t hash_body(const vector<pair<int,int>>& body) {
    uint64_t h = 1469598103934665603ULL;
    for (auto [x, y] : body) {
        uint64_t v = (uint64_t)(x * 131 + y + 1);
        h ^= v;
        h *= 1099511628211ULL;
    }
    return h;
}

int nearest_required_distance(int x, int y, int curr_len) {
    if (curr_len >= M) return 0;
    int best = 1e9;
    for (int shift = 0; shift < 3 && curr_len + shift < M; shift++) {
        int target = D[curr_len + shift];
        int now_best = 1e9;
        for (int id : color_cells[target]) {
            int i = id / N, j = id % N;
            if (Map[i][j] != target) continue;
            now_best = min(now_best, abs(i - x) + abs(j - y));
        }
        if (now_best < 1e9) {
            best = min(best, now_best + shift * 2);
        }
    }
    return (best == 1e9) ? N * N : best;
}

bool has_immediate_target(const vector<pair<int,int>>& body, int curr_len) {
    if (curr_len >= M) return false;
    auto [hx, hy] = body.back();
    for (int d = 0; d < 4; d++) {
        int nx = hx + DIR[d].first, ny = hy + DIR[d].second;
        if (!in_board(nx, ny)) continue;
        if (Map[nx][ny] == D[curr_len]) return true;
    }
    return false;
}

bool in_endgame_mode(const vector<pair<int,int>>& body, int curr_len) {
    int remain_food = M - curr_len;
    int area = N * N;
    int len = (int)body.size();
    return (remain_food <= max(10, N / 2)) || (len * 100 >= area * 58);
}

void build_order_id() {
    order_id.assign(N, vector<int>(N, 0));
    int id = 0;
    for (int i = 0; i < N; i++) {
        if (i % 2 == 0) {
            for (int j = 0; j < N; j++) order_id[i][j] = id++;
        } else {
            for (int j = N - 1; j >= 0; j--) order_id[i][j] = id++;
        }
    }
}

ll endgame_guide_bonus(const vector<pair<int,int>>& body, int nx, int ny) {
    auto [hx, hy] = body.back();
    int area = N * N;
    int now = order_id[hx][hy];
    int to = order_id[nx][ny];
    int want = (now + 1) % area;
    int diff = (to - want + area) % area;
    ll score = -W_ENDGAME_GUIDE * (ll)diff;
    if (diff == 0) score += 4500LL;
    return score;
}

void online_tune_weights() {
    if (tune_moves < 8) return;

    if (tune_wrong > 0) {
        // 【改善策2】終盤は誤食ペナルティの上限を緩め、生存とルート探索を優先させる
        ll current_wrong_eat_max = in_endgame_mode(hebi, length_snake) ? 80000LL : 160000LL;
        W_WRONG_EAT = min(current_wrong_eat_max, W_WRONG_EAT + 7000LL * tune_wrong);
        W_NEED_DIST = min(260LL, W_NEED_DIST + 8LL);
    }
    if (tune_exact == 0) {
        W_NEED_DIST = min(260LL, W_NEED_DIST + 12LL);
    }
    if (tune_deadend > 0) {
        W_ONEWAY = min(3200LL, W_ONEWAY + 180LL * tune_deadend);
        W_ENDGAME_GUIDE = min(520LL, W_ENDGAME_GUIDE + 20LL * tune_deadend);
    }

    if (tune_wrong == 0 && tune_deadend == 0 && tune_exact > 0) {
        W_NEED_DIST = max(BASE_W_NEED_DIST, W_NEED_DIST - 4LL);
        W_LOOP_REP = max(BASE_W_LOOP_REP, W_LOOP_REP - 6LL);
        W_ONEWAY = max(BASE_W_ONEWAY, W_ONEWAY - 24LL);
        W_WRONG_EAT = max(BASE_W_WRONG_EAT, W_WRONG_EAT - 1800LL);
        W_ENDGAME_GUIDE = max(BASE_W_ENDGAME_GUIDE, W_ENDGAME_GUIDE - 6LL);
    }

    tune_moves = 0;
    tune_exact = 0;
    tune_wrong = 0;
    tune_deadend = 0;
    invalidate_score_memo();
}

vector<vector<vector<double>>> heatmap;

void apply_food_effect(int sx, int sy, int color, double sign) {
    for (int dx = -HEAT_RADIUS; dx <= HEAT_RADIUS; dx++) {
        int rem = HEAT_RADIUS - abs(dx);
        int x = sx + dx;
        if (x < 0 || x >= N) continue;
        for (int dy = -rem; dy <= rem; dy++) {
            int y = sy + dy;
            if (y < 0 || y >= N) continue;
            int d = abs(dx) + abs(dy);
            heatmap[color][x][y] += sign * (1.0 / (1.0 + d));
        }
    }
}

void build_heatmap() {
    heatmap.assign(C + 1, vector<vector<double>>(N, vector<double>(N, 0.0)));
    for (int si = 0; si < N; si++) {
        for (int sj = 0; sj < N; sj++) {
            int col = Map[si][sj];
            if (col == 0) continue;
            apply_food_effect(si, sj, col, +1.0);
        }
    }
}

double future_color_demand_score(int i, int j, int curr_len) {
    double score = 0.0, weight = 1.0;
    for (int k = 0; k < 6 && curr_len + k < M; k++) {
        score += weight * heatmap[D[curr_len + k]][i][j];
        weight *= 0.5;
    }
    return score;
}

int flood_fill_reachable_raw(const vector<pair<int,int>>& body) {
    auto [hx, hy] = body.back();
    vector<vector<bool>> blocked(N, vector<bool>(N, false));
    for (int i = 1; i+1 < (int)body.size(); i++)
        blocked[body[i].first][body[i].second] = true;
    vector<vector<bool>> vis(N, vector<bool>(N, false));
    queue<pair<int,int>> que;
    vis[hx][hy] = true;
    que.push({hx, hy});
    int cnt = 0;
    while (!que.empty()) {
        auto [cx, cy] = que.front(); que.pop();
        cnt++;
        for (auto [dx, dy] : DIR) {
            int nx = cx+dx, ny = cy+dy;
            if (!in_board(nx,ny) || vis[nx][ny] || blocked[nx][ny]) continue;
            vis[nx][ny] = true;
            que.push({nx, ny});
        }
    }
    return cnt;
}

int flood_fill_reachable(const vector<pair<int,int>>& body) {
    uint64_t key = state_key_with_epoch(body, 0xA17F00DULL);
    auto it = memo_ff.find(key);
    if (it != memo_ff.end()) return it->second;
    int v = flood_fill_reachable_raw(body);
    memo_ff[key] = v;
    return v;
}

ll get_priority(int color, int curr_len) {
    if (curr_len >= M) return 0;
    ll score = 0;
    if (color == D[curr_len])                     score += 100000LL;
    if (curr_len+1 < M && color == D[curr_len+1]) score += 28000LL;
    if (curr_len+2 < M && color == D[curr_len+2]) score += 8000LL;
    if (curr_len+3 < M && color == D[curr_len+3]) score += 2200LL;
    if (curr_len+4 < M && color == D[curr_len+4]) score += 600LL;
    return score;
}

bool simulate_move(const vector<pair<int,int>>& body, int d,
                   vector<pair<int,int>>& next_body, bool& ate) {
    auto [hx, hy] = body.back();
    int nx = hx + DIR[d].first, ny = hy + DIR[d].second;
    if (!in_board(nx, ny)) return false;
    if ((int)body.size() >= 2) {
        auto neck = body[(int)body.size()-2];
        if (nx == neck.first && ny == neck.second) return false;
    }
    ate = (Map[nx][ny] != 0);
    for (int i = 1; i+1 < (int)body.size(); i++)
        if (body[i].first == nx && body[i].second == ny) return false;
    if (ate && nx == body.front().first && ny == body.front().second) return false;
    next_body = body;
    if (!ate) next_body.erase(next_body.begin());
    next_body.push_back({nx, ny});
    return true;
}

ll position_safety(const vector<pair<int,int>>& body) {
    uint64_t cache_key = state_key_with_epoch(body, 0x50AFE71ULL);
    auto it_ps = memo_ps.find(cache_key);
    if (it_ps != memo_ps.end()) return it_ps->second;

    auto [hx, hy] = body.back();
    auto [tx, ty] = body.front();

    int mob = 0;
    for (int d = 0; d < 4; d++) {
        int nx = hx + DIR[d].first, ny = hy + DIR[d].second;
        if (!in_board(nx, ny)) continue;
        if ((int)body.size() >= 2) {
            auto neck = body[(int)body.size()-2];
            if (nx == neck.first && ny == neck.second) continue;
        }
        bool ate2 = (Map[nx][ny] != 0);
        bool bad = false;
        for (int i = 1; i+1 < (int)body.size(); i++)
            if (body[i].first==nx && body[i].second==ny) { bad=true; break; }
        if (bad) continue;
        if (ate2 && nx==body.front().first && ny==body.front().second) continue;
        mob++;
    }

    if (mob == 0) {
        memo_ps[cache_key] = -5000000LL;
        return -5000000LL;
    }

    ll score = mob * 1200LL;
    int tail_dist = abs(hx - tx) + abs(hy - ty);
    score += 80LL * tail_dist;

    int ff = flood_fill_reachable(body);
    int bl = (int)body.size();

    if (ff <= 1) {
        ll v = -4000000LL + ff * 100LL;
        memo_ps[cache_key] = v;
        return v;
    } else if (ff < bl) {
        score -= 2500LL * (bl - ff + 1);
    } else {
        score += (ll)(log2((double)ff + 1) * 700.0);
    }

    if (mob == 1) score -= W_ONEWAY;

    memo_ps[cache_key] = score;
    return score;
}

vector<int> ordered_moves(const vector<pair<int,int>>& body, int curr_len) {
    vector<pair<ll,int>> sc;
    sc.reserve(4);
    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        ll s = position_safety(nb);
        auto [nx, ny] = nb.back();

        if (ate) {
            s += get_priority(Map[nx][ny], curr_len);
            s += (ll)(future_color_demand_score(nx, ny, curr_len+1) * 3000.0);
            if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= W_WRONG_EAT;
        } else {
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 500.0);
        }
        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        sc.push_back({s, d});
    }
    sort(sc.rbegin(), sc.rend());
    vector<int> res;
    for (auto &p : sc) res.push_back(p.second);
    return res;
}

ll score_after(const vector<pair<int,int>>& body, int curr_len, int depth) {
    if (time_up()) return 0;
    if (depth <= 0) {
        auto [hx, hy] = body.back();
        return position_safety(body)
             + (ll)(future_color_demand_score(hx, hy, curr_len) * 2500.0);
    }

    auto moves = ordered_moves(body, curr_len);
    if (moves.empty()) return -5000000LL;

    ll best = NEG_INF;
    for (int d : moves) {
        if (time_up()) break;
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        ll local = position_safety(nb);
        if (local <= -3500000LL) { best = max(best, local); continue; }

        auto [nx, ny] = nb.back();
        local += (ll)(future_color_demand_score(nx, ny, ate ? curr_len+1 : curr_len) * 1800.0);
        local -= 15LL;

        if (ate) {
            local += get_priority(Map[nx][ny], curr_len);
            local += (ll)(score_after(nb, curr_len+1, depth-1) * 0.75);
        } else {
            local += (ll)(score_after(nb, curr_len, depth-1) * 0.75);
        }
        best = max(best, local);
    }
    return (best == NEG_INF) ? -5000000LL : best;
}

struct SearchResult {
    ll score = NEG_INF;
    string path;
    bool ok = false;
};

struct SearchPack {
    SearchResult best;
    vector<SearchResult> candidates;
};

vector<SearchResult> dedup_candidates(vector<SearchResult> cand, int keep_limit);
bool should_rollback_small_region(const vector<pair<int,int>>& body, int curr_len);
bool starts_with_banned_prefix(const string& path);

inline double search_time_left_sec() {
    return chrono::duration<double>(SEARCH_DEADLINE - Clock::now()).count();
}

void dfs_collect(const vector<pair<int,int>>& body, int curr_len, int depth,
                 string& path, ll acc_score,
                 vector<SearchResult>& out,
                 int future_depth) {
    if (time_up()) return;
    if (depth <= 0) return;

    auto moves = ordered_moves(body, curr_len);
    for (int d : moves) {
        if (time_up()) return;
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        path.push_back(DIRC[d]);
        auto [nx, ny] = nb.back();

        ll safe = position_safety(nb);
        if (safe <= -3500000LL) {
            path.pop_back();
            continue;
        }

        ll step = acc_score + safe;
        step -= 30LL * (ll)path.size();
        step += (ll)(future_color_demand_score(nx, ny, ate ? curr_len+1 : curr_len) * 500.0);

        if (ate) {
            ll total = step + get_priority(Map[nx][ny], curr_len);
            total += (ll)(future_color_demand_score(nx, ny, curr_len+1) * 4000.0);
            ll future = score_after(nb, curr_len+1, future_depth);
            total += (ll)(future * 0.85);
            out.push_back({total, path, true});
        } else {
            dfs_collect(nb, curr_len, depth-1, path, step, out, future_depth);
        }
        path.pop_back();
    }
}

SearchPack search_best_path(const vector<pair<int,int>>& body, int curr_len,
                            int banned_first_dir = -1, int diversity_mode = 0) {
    SearchPack pack;
    auto& best = pack.best;
    auto& candidates = pack.candidates;

    struct BeamState {
        vector<pair<int,int>> body;
        string path;
        ll score;
        vector<int> head_trace;
    };

    auto depth_limit_from_time = [&](double tl, bool urgent) {
        int d;
        if      (tl > 0.100) d = 24;
        else if (tl > 0.060) d = 18;
        else if (tl > 0.030) d = 12;
        else                 d = 8;
        if (urgent) d += 4;
        return d;
    };

    auto beam_width_from_time = [&](double tl, bool urgent) {
        int w;
        if      (tl > 0.100) w = BEAM_WIDTH_HI;
        else if (tl > 0.050) w = BEAM_WIDTH_MID;
        else                 w = BEAM_WIDTH_LO;
        if (urgent) w = min(BEAM_WIDTH_HI, w + 12);
        if (diversity_mode == 1) w = max(20, w - 10);
        if (diversity_mode == 2) w = min(BEAM_WIDTH_HI, w + 6);
        return w;
    };

    bool urgent = has_immediate_target(body, curr_len);
    double tl0 = chrono::duration<double>(SEARCH_DEADLINE - Clock::now()).count();
    int beam_depth = depth_limit_from_time(tl0, urgent);
    int beam_width = beam_width_from_time(tl0, urgent);

    vector<BeamState> beam;
    beam.push_back({body, "", 0LL, {cell_id(body.back().first, body.back().second)}});

    for (int step = 0; step < beam_depth; step++) {
        if (time_up()) break;

        vector<BeamState> next;
        next.reserve((int)beam.size() * 3);

        for (const auto& st : beam) {
            if (time_up()) break;
            auto moves = ordered_moves(st.body, curr_len);
            for (int d : moves) {
                if (step == 0 && banned_first_dir != -1 && d == banned_first_dir) continue;
                vector<pair<int,int>> nb; bool ate = false;
                if (!simulate_move(st.body, d, nb, ate)) continue;

                auto [nx, ny] = nb.back();
                ll s = st.score;
                ll safe = position_safety(nb);
                if (safe <= -3500000LL) continue;
                s += safe;
                s -= 20LL * (ll)(st.path.size() + 1);

                int need_dist = nearest_required_distance(nx, ny, curr_len);
                s -= W_NEED_DIST * need_dist;

                int id = cell_id(nx, ny);
                int rep = 0;
                for (int v : st.head_trace) if (v == id) rep++;
                s -= W_LOOP_REP * rep;

                int legal2 = 0;
                for (int d2 = 0; d2 < 4; d2++) {
                    vector<pair<int,int>> nb2; bool ate2 = false;
                    if (simulate_move(nb, d2, nb2, ate2)) legal2++;
                }
                if (legal2 == 0) s -= 900000LL;

                s += (ll)(future_color_demand_score(nx, ny, curr_len) * 700.0);
                if (in_endgame_mode(st.body, curr_len)) s += endgame_guide_bonus(st.body, nx, ny);

                string np = st.path;
                np.push_back(DIRC[d]);

                if (ate) {
                    if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= W_WRONG_EAT;
                    ll total = s + get_priority(Map[nx][ny], curr_len);
                    total += (ll)(future_color_demand_score(nx, ny, curr_len+1) * 3500.0);
                    total += (ll)(score_after(nb, curr_len+1, 3) * 0.78);
                    candidates.push_back({total, np, true});
                    if (total > best.score) {
                        best.score = total;
                        best.path = np;
                        best.ok = true;
                    }
                    continue;
                }

                BeamState ns;
                ns.body = move(nb);
                ns.path = move(np);
                ns.score = s;
                ns.head_trace = st.head_trace;
                ns.head_trace.push_back(id);
                if ((int)ns.head_trace.size() > 18) ns.head_trace.erase(ns.head_trace.begin());
                next.push_back(move(ns));
            }
        }

        if (next.empty()) break;

        sort(next.begin(), next.end(), [](const BeamState& a, const BeamState& b) {
            if (a.score != b.score) return a.score > b.score;
            return a.path.size() < b.path.size();
        });

        unordered_map<uint64_t, ll> seen;
        vector<BeamState> uniq;
        uniq.reserve(min((int)next.size(), beam_width));
        for (auto& st : next) {
            uint64_t key = hash_body(st.body);
            key ^= (uint64_t)(curr_len + 1) * 1469598103934665603ULL;
            auto it = seen.find(key);
            if (it != seen.end() && it->second >= st.score) continue;
            seen[key] = st.score;
            uniq.push_back(move(st));
            if ((int)uniq.size() >= beam_width) break;
        }
        beam.swap(uniq);
    }

    if (best.ok) {
        candidates = dedup_candidates(move(candidates), CANDIDATE_KEEP);
        return pack;
    }

    const int future_depth = 3;
    int max_depth;
    double tl = chrono::duration<double>(SEARCH_DEADLINE - Clock::now()).count();
    if      (tl > 0.080) max_depth = 22;
    else if (tl > 0.040) max_depth = 14;
    else if (tl > 0.020) max_depth = 10;
    else                 max_depth = 6;

    for (int depth = 1; depth <= max_depth; depth++) {
        if (time_up()) break;
        vector<SearchResult> depth_candidates;
        string path;
        dfs_collect(body, curr_len, depth, path, 0LL, depth_candidates, future_depth);
        candidates.insert(candidates.end(), depth_candidates.begin(), depth_candidates.end());
        for (auto &c : depth_candidates)
            if (c.score > best.score) best = c;
    }
    candidates = dedup_candidates(move(candidates), CANDIDATE_KEEP);
    return pack;
}

int legal_move_count(const vector<pair<int,int>>& body) {
    uint64_t key = state_key_with_epoch(body, 0x1E6A1ULL);
    auto it = memo_lmc.find(key);
    if (it != memo_lmc.end()) return it->second;

    int cnt = 0;
    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (simulate_move(body, d, nb, ate)) cnt++;
    }
    memo_lmc[key] = cnt;
    return cnt;
}

int body_bbox_area(const vector<pair<int,int>>& body) {
    int minx = N, miny = N, maxx = -1, maxy = -1;
    for (auto [x, y] : body) {
        minx = min(minx, x);
        miny = min(miny, y);
        maxx = max(maxx, x);
        maxy = max(maxy, y);
    }
    return (maxx - minx + 1) * (maxy - miny + 1);
}

int choose_survival_move(const vector<pair<int,int>>& body, int curr_len) {
    int best_d = -1;
    ll best_s = NEG_INF;

    int cur_bbox = body_bbox_area(body);
    auto [hx, hy] = body.back();
    auto [tx, ty] = body.front();
    int cur_tail_dist = abs(hx - tx) + abs(hy - ty);

    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        auto [nx, ny] = nb.back();
        ll s = position_safety(nb);
        s += 900LL * legal_move_count(nb);

        int nd = nearest_required_distance(nx, ny, curr_len);
        s -= 70LL * nd;
        s += (ll)(future_color_demand_score(nx, ny, curr_len) * 850.0);

        if (ate) {
            s += get_priority(Map[nx][ny], curr_len);
            if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= W_WRONG_EAT;
        } else {
            int nbbox = body_bbox_area(nb);
            int ntail = abs(nx - nb.front().first) + abs(ny - nb.front().second);

            if (nd >= N / 2) {
                s += 140LL * (cur_bbox - nbbox);
                s += 80LL * (cur_tail_dist - ntail);
            }
        }

        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        if (s > best_s) { best_s = s; best_d = d; }
    }
    return best_d;
}

SearchResult choose_candidate_with_rollback(const vector<pair<int,int>>& body, int curr_len,
                                            const vector<SearchResult>& candidates) {
    if (candidates.empty()) return SearchResult{};

    SearchResult picked = candidates.front();
    ll best_key_a = -(1LL << 60);
    ll best_key_b = -(1LL << 60);
    ll best_key_c = -(1LL << 60);

    struct ShortEval {
        int idx;
        int exact_cnt;
        int wrong_cnt;
        ll score;
    };
    vector<ShortEval> shortlist;
    shortlist.reserve(min((int)candidates.size(), CANDIDATE_EVAL_LIMIT));

    const int QUICK_STEPS = 6;
    const int FULL_LIMIT = 6;

    int checked = 0;
    for (int ci = 0; ci < (int)candidates.size(); ci++) {
        const auto& cand = candidates[ci];
        if (checked >= CANDIDATE_EVAL_LIMIT) break;
        if (!cand.ok || cand.path.empty()) continue;
        if (starts_with_banned_prefix(cand.path)) continue;
        checked++;

        auto tmp_body = body;
        int tmp_len = curr_len;
        bool bad = false;
        int exact_cnt = 0;
        int wrong_cnt = 0;
        eaten_token++;
        if (eaten_token == INT_MAX) {
            fill(eaten_mark.begin(), eaten_mark.end(), 0);
            eaten_token = 1;
        }
        int token = eaten_token;

        int step_idx = 0;
        for (char ch : cand.path) {
            if (step_idx >= QUICK_STEPS) break;
            int d = -1;
            for (int i = 0; i < 4; i++) if (DIRC[i] == ch) d = i;
            if (d == -1) { bad = true; break; }

            auto [hx, hy] = tmp_body.back();
            int nx = hx + DIR[d].first, ny = hy + DIR[d].second;

            vector<pair<int,int>> nb; bool ate = false;
            if (!in_board(nx, ny)) { bad = true; break; }
            if ((int)tmp_body.size() >= 2) {
                auto neck = tmp_body[(int)tmp_body.size()-2];
                if (nx == neck.first && ny == neck.second) { bad = true; break; }
            }
            int nid = cell_id(nx, ny);
            int cell = (eaten_mark[nid] == token) ? 0 : Map[nx][ny];
            ate = (cell != 0);
            for (int i = 1; i+1 < (int)tmp_body.size(); i++) {
                if (tmp_body[i].first == nx && tmp_body[i].second == ny) { bad = true; break; }
            }
            if (bad) break;
            if (ate && nx == tmp_body.front().first && ny == tmp_body.front().second) { bad = true; break; }

            nb = tmp_body;
            if (!ate) nb.erase(nb.begin());
            nb.push_back({nx, ny});
            tmp_body.swap(nb);

            if (ate) {
                int got = cell;
                if (tmp_len < M && got != D[tmp_len]) {
                    wrong_cnt++;
                } else {
                    exact_cnt++;
                }
                eaten_mark[nid] = token;
                tmp_len++;
            }
            step_idx++;
        }

        if (bad) continue;
        shortlist.push_back({ci, exact_cnt, wrong_cnt, cand.score});
    }

    sort(shortlist.begin(), shortlist.end(), [](const ShortEval& a, const ShortEval& b) {
        if (a.exact_cnt != b.exact_cnt) return a.exact_cnt > b.exact_cnt;
        if (a.wrong_cnt != b.wrong_cnt) return a.wrong_cnt < b.wrong_cnt;
        return a.score > b.score;
    });

    int full_checked = 0;
    for (const auto& se : shortlist) {
        if (full_checked >= FULL_LIMIT) break;
        const auto& cand = candidates[se.idx];
        full_checked++;

        auto tmp_body = body;
        int tmp_len = curr_len;
        bool bad = false;
        int exact_cnt = 0;
        int wrong_cnt = 0;
        eaten_token++;
        if (eaten_token == INT_MAX) {
            fill(eaten_mark.begin(), eaten_mark.end(), 0);
            eaten_token = 1;
        }
        int token = eaten_token;

        for (char ch : cand.path) {
            int d = -1;
            for (int i = 0; i < 4; i++) if (DIRC[i] == ch) d = i;
            if (d == -1) { bad = true; break; }

            auto [hx, hy] = tmp_body.back();
            int nx = hx + DIR[d].first, ny = hy + DIR[d].second;

            vector<pair<int,int>> nb; bool ate = false;
            if (!in_board(nx, ny)) { bad = true; break; }
            if ((int)tmp_body.size() >= 2) {
                auto neck = tmp_body[(int)tmp_body.size()-2];
                if (nx == neck.first && ny == neck.second) { bad = true; break; }
            }
            int nid = cell_id(nx, ny);
            int cell = (eaten_mark[nid] == token) ? 0 : Map[nx][ny];
            ate = (cell != 0);
            for (int i = 1; i+1 < (int)tmp_body.size(); i++) {
                if (tmp_body[i].first == nx && tmp_body[i].second == ny) { bad = true; break; }
            }
            if (bad) break;
            if (ate && nx == tmp_body.front().first && ny == tmp_body.front().second) { bad = true; break; }

            nb = tmp_body;
            if (!ate) nb.erase(nb.begin());
            nb.push_back({nx, ny});
            tmp_body.swap(nb);

            if (ate) {
                int got = cell;
                if (tmp_len < M && got != D[tmp_len]) {
                    wrong_cnt++;
                } else {
                    exact_cnt++;
                }
                eaten_mark[nid] = token;
                tmp_len++;
            }
        }

        if (bad) continue;

        ll key_a = exact_cnt;
        ll key_b = -wrong_cnt;
        ll key_c = cand.score;
        if (key_a > best_key_a ||
            (key_a == best_key_a && (key_b > best_key_b ||
            (key_b == best_key_b && key_c > best_key_c)))) {
            best_key_a = key_a;
            best_key_b = key_b;
            best_key_c = key_c;
            picked = cand;
        }
    }

    return picked;
}

struct DecisionCheckpoint {
    vector<pair<int,int>> body;
    int eat_history_size;
    int curr_len;
    int exact_match_count;
    string answer_snapshot;
    vector<SearchResult> alternatives;
};

struct EatEvent {
    int x, y, color;
    bool exact;
};

vector<EatEvent> eat_history;
int exact_match_count = 0;

int choose_fallback_move(const vector<pair<int,int>>& body, int curr_len) {
    int best_d = -1;
    ll best_s = NEG_INF;
    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;
        auto [nx, ny] = nb.back();
        ll s = position_safety(nb);
        s += (ll)(future_color_demand_score(nx, ny, curr_len) * 1000.0);
        if (ate) {
            s += get_priority(Map[nx][ny], curr_len);
            if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= W_WRONG_EAT;
        }
        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        if (s > best_s) { best_s = s; best_d = d; }
    }
    return best_d;
}

bool apply_and_output_move(char ch, vector<pair<int,int>>& body, int& curr_len) {
    int d = -1;
    for (int i = 0; i < 4; i++) if (DIRC[i] == ch) { d = i; break; }
    if (d == -1) return false;
    vector<pair<int,int>> nb; bool ate = false;
    if (!simulate_move(body, d, nb, ate)) return false;
    body.swap(nb);
    tune_moves++;
    if (ate) {
        auto [x, y] = body.back();
        int color = Map[x][y];
        bool exact = (curr_len < M && color == D[curr_len]);
        curr_len++;
        if (exact) {
            exact_match_count++;
            tune_exact++;
        } else {
            tune_wrong++;
        }
        eat_history.push_back({x, y, color, exact});
        apply_food_effect(x, y, color, -1.0);
        Map[x][y] = 0;
        map_epoch++;
        invalidate_search_memo();
    }
    return true;
}

void rollback_eat_history_to(int target_size) {
    while ((int)eat_history.size() > target_size) {
        auto ev = eat_history.back(); eat_history.pop_back();
        Map[ev.x][ev.y] = ev.color;
        apply_food_effect(ev.x, ev.y, ev.color, +1.0);
        if (ev.exact) exact_match_count--;
        map_epoch++;
    }
    invalidate_search_memo();
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> N >> M >> C;
    D.resize(M);
    for (int &x : D) cin >> x;
    Map.assign(N, vector<int>(N));
    color_cells.assign(C + 1, {});
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            cin >> Map[i][j];
            if (Map[i][j] != 0) color_cells[Map[i][j]].push_back(cell_id(i, j));
        }

    hebi = {{0,0},{1,0},{2,0},{3,0},{4,0}};

    auto start = Clock::now();
    DEADLINE = start + chrono::milliseconds(1950);

    build_heatmap();
    build_order_id();
    eaten_mark.assign(N * N, 0);
    banned_prefixes.clear();

    string answer;
    vector<DecisionCheckpoint> checkpoints;
    double budget_bias = 1.0;
    string best_answer_backup = answer;
    int best_len_backup = length_snake;
    int best_exact_backup = exact_match_count;
    int best_step_backup = 0;

    // 【改善策0】 ご指定の重み付けでバックアップ更新式を修正（生存ターンを評価）
    auto update_backup = [&]() {
        int cur_steps = (int)answer.size();
        double current_score = length_snake * 1.0 + exact_match_count * 0.6 + cur_steps * 0.1;
        double best_score = best_len_backup * 1.0 + best_exact_backup * 0.6 + best_step_backup * 0.1;

        if (current_score > best_score) {
            best_len_backup = length_snake;
            best_exact_backup = exact_match_count;
            best_step_backup = cur_steps;
            best_answer_backup = answer;
        }
    };

    while (length_snake < M && !hard_time_up()) {
        double remaining = hard_time_left_sec();
        if (remaining <= OUTPUT_RESERVE) break;

        // 【改善策1】 後半に時間を残すため、見積もりターン数に少し余裕（バッファ）を持たせる
        int turns_left = M - length_snake;
        double safe_turns = turns_left + (M * 0.2); 
        double reserve = max(OUTPUT_RESERVE, min(0.03, 0.004 + 0.00002 * (double)turns_left));
        double budget_per_turn = (remaining - reserve) / safe_turns;
        
        budget_per_turn = max(budget_per_turn, 0.01);
        budget_per_turn = min(budget_per_turn * budget_bias, 0.22);

        if (has_immediate_target(hebi, length_snake)) {
            budget_per_turn = min(0.24, budget_per_turn * 1.35);
        }

        SEARCH_DEADLINE = Clock::now()
            + chrono::microseconds((ll)(budget_per_turn * 1e6));
        if (SEARCH_DEADLINE > DEADLINE - chrono::milliseconds(2))
            SEARCH_DEADLINE = DEADLINE - chrono::milliseconds(2);

        auto search_start = Clock::now();
        SearchPack pack = search_best_path(hebi, length_snake);
        vector<SearchResult> all_candidates = pack.candidates;
        int banned_first_dir = -1;
        if (pack.best.ok && !pack.best.path.empty()) {
            char c0 = pack.best.path[0];
            for (int i = 0; i < 4; i++) if (DIRC[i] == c0) banned_first_dir = i;
        }

        int extra_try = 0;
        while (!time_up() && extra_try < 2) {
            double left = search_time_left_sec();
            if (left < 0.0160) break;
            SearchPack extra = search_best_path(hebi, length_snake, banned_first_dir, extra_try + 1);
            all_candidates.insert(all_candidates.end(), extra.candidates.begin(), extra.candidates.end());
            if (extra.best.ok && !extra.best.path.empty()) {
                char c0 = extra.best.path[0];
                for (int i = 0; i < 4; i++) if (DIRC[i] == c0) banned_first_dir = i;
            }
            extra_try++;
        }
        auto search_end = Clock::now();
        double used = chrono::duration<double>(search_end - search_start).count();

        if (used < budget_per_turn * 0.80) budget_bias = min(1.60, budget_bias * 1.05);
        else if (used > budget_per_turn * 1.05) budget_bias = max(0.70, budget_bias * 0.92);

        all_candidates = dedup_candidates(move(all_candidates), CANDIDATE_KEEP * 2);
        SearchResult best = choose_candidate_with_rollback(hebi, length_snake, all_candidates);

        if (best.ok && !best.path.empty()) {
            DecisionCheckpoint cp;
            cp.body = hebi;
            cp.eat_history_size = (int)eat_history.size();
            cp.curr_len = length_snake;
            cp.exact_match_count = exact_match_count;
            cp.answer_snapshot = answer;
            for (auto &c : all_candidates) {
                if (c.path != best.path) cp.alternatives.push_back(c);
            }
            checkpoints.push_back(move(cp));
            if ((int)checkpoints.size() > 16) checkpoints.erase(checkpoints.begin());

            string progressed;
            for (char ch : best.path) {
                int before_len = length_snake;
                vector<pair<int,int>> prev_body = hebi;
                int prev_hist = (int)eat_history.size();

                if (!apply_and_output_move(ch, hebi, length_snake)) break;
                answer.push_back(ch);
                progressed.push_back(ch);

                if (length_snake < M && legal_move_count(hebi) == 0) {
                    hebi = prev_body;
                    rollback_eat_history_to(prev_hist);
                    length_snake = before_len;
                    tune_deadend++;
                    if (!answer.empty()) answer.pop_back();
                    if (!progressed.empty()) {
                        banned_prefixes.push_back(progressed);
                        if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                    }
                    break;
                }

                if ((int)progressed.size() % 6 == 0 && turns_left > 24 && hard_time_left_sec() >= 0.18
                    && search_time_left_sec() >= 0.008
                    && legal_move_count(hebi) <= 2
                    && should_rollback_small_region(hebi, length_snake)) {
                    hebi = prev_body;
                    rollback_eat_history_to(prev_hist);
                    length_snake = before_len;
                    if (!answer.empty()) answer.pop_back();
                    tune_deadend++;
                    if (!progressed.empty()) {
                        banned_prefixes.push_back(progressed);
                        if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                    }
                    break;
                }
            }
            update_backup();
            online_tune_weights();
            continue;
        }

        int d = choose_fallback_move(hebi, length_snake);
        if (d == -1) {
            bool restored = false;
            int cp_attempts = 0;
            
            // 【改善策3】 残り時間が少ない時は、遠い過去までの無駄な巻き戻しを切り捨てる
            int max_cp_attempts = (hard_time_left_sec() < 0.15) ? 3 : 16;
            
            while (!checkpoints.empty() && !restored && cp_attempts < max_cp_attempts) {
                cp_attempts++;
                auto cp = move(checkpoints.back());
                checkpoints.pop_back();
                hebi = cp.body;
                rollback_eat_history_to(cp.eat_history_size);
                length_snake = cp.curr_len;
                exact_match_count = cp.exact_match_count;
                answer = cp.answer_snapshot;

                SearchResult alt = choose_candidate_with_rollback(hebi, length_snake, cp.alternatives);
                if (alt.ok && !alt.path.empty()) {
                    string progressed;
                    for (char ch : alt.path) {
                        int before_len = length_snake;
                        vector<pair<int,int>> prev_body = hebi;
                        int prev_hist = (int)eat_history.size();
                        if (!apply_and_output_move(ch, hebi, length_snake)) break;
                        answer.push_back(ch);
                        progressed.push_back(ch);
                        if (length_snake < M && legal_move_count(hebi) == 0) {
                            hebi = prev_body;
                            rollback_eat_history_to(prev_hist);
                            length_snake = before_len;
                            tune_deadend++;
                            if (!answer.empty()) answer.pop_back();
                            if (!progressed.empty()) {
                                banned_prefixes.push_back(progressed);
                                if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                            }
                            break;
                        }
                        if ((int)progressed.size() % 6 == 0 && turns_left > 24 && hard_time_left_sec() >= 0.18
                            && search_time_left_sec() >= 0.008
                            && legal_move_count(hebi) <= 2
                            && should_rollback_small_region(hebi, length_snake)) {
                            hebi = prev_body;
                            rollback_eat_history_to(prev_hist);
                            length_snake = before_len;
                            tune_deadend++;
                            if (!answer.empty()) answer.pop_back();
                            if (!progressed.empty()) {
                                banned_prefixes.push_back(progressed);
                                if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                            }
                            break;
                        }
                    }
                    restored = true;
                }
            }
            if (!restored) {
                int sd = choose_survival_move(hebi, length_snake);
                if (sd == -1) break;
                int before_len2 = length_snake;
                if (apply_and_output_move(DIRC[sd], hebi, length_snake) && length_snake >= before_len2) {
                    answer.push_back(DIRC[sd]);
                }
                update_backup();
                online_tune_weights();
                continue;
            }
            update_backup();
            online_tune_weights();
            continue;
        }
        int before_len = length_snake;
        if (apply_and_output_move(DIRC[d], hebi, length_snake) && length_snake >= before_len) {
            answer.push_back(DIRC[d]);
        }
        update_backup();
        online_tune_weights();
    }

    for (char ch : best_answer_backup) cout << ch << '\n';
    cout.flush();
    return 0;
}

vector<SearchResult> dedup_candidates(vector<SearchResult> cand, int keep_limit) {
    sort(cand.begin(), cand.end(), [](const SearchResult& a, const SearchResult& b) {
        return a.score > b.score;
    });

    unordered_set<string> seen_path;
    vector<SearchResult> uniq;
    uniq.reserve(min((int)cand.size(), keep_limit));

    for (auto &c : cand) {
        if (!c.ok || c.path.empty()) continue;
        if (!seen_path.insert(c.path).second) continue;

        uniq.push_back(c);
        if ((int)uniq.size() >= keep_limit) break;
    }
    return uniq;
}

int largest_free_component(const vector<pair<int,int>>& body) {
    vector<vector<bool>> blocked(N, vector<bool>(N, false));
    for (int i = 1; i + 1 < (int)body.size(); i++) {
        blocked[body[i].first][body[i].second] = true;
    }

    vector<vector<bool>> vis(N, vector<bool>(N, false));
    int best = 0;
    queue<pair<int,int>> que;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (blocked[i][j] || vis[i][j]) continue;
            vis[i][j] = true;
            que.push({i, j});
            int cnt = 0;
            while (!que.empty()) {
                auto [x, y] = que.front(); que.pop();
                cnt++;
                for (auto [dx, dy] : DIR) {
                    int nx = x + dx, ny = y + dy;
                    if (!in_board(nx, ny) || blocked[nx][ny] || vis[nx][ny]) continue;
                    vis[nx][ny] = true;
                    que.push({nx, ny});
                }
            }
            best = max(best, cnt);
        }
    }
    return best;
}

bool should_rollback_small_region(const vector<pair<int,int>>& body, int curr_len) {
    if (in_endgame_mode(body, curr_len)) return false;
    int head_cc = flood_fill_reachable(body);
    int len = (int)body.size();
    if (head_cc > len + 14) return false;

    if (search_time_left_sec() < 0.010) {
        return head_cc <= len + 6;
    }

    int best_cc = largest_free_component(body);
    int gap = best_cc - head_cc;
    return (gap >= max(8, N / 2)) && (head_cc <= len + 10);
}

bool starts_with_banned_prefix(const string& path) {
    for (const auto& pref : banned_prefixes) {
        if ((int)pref.size() <= (int)path.size() && equal(pref.begin(), pref.end(), path.begin())) {
            return true;
        }
    }
    return false;
}
