#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using Clock = std::chrono::steady_clock;

int N, M, C;
vector<int> D;
vector<vector<int>> Map;
vector<vector<int>> color_cells;
vector<int> color_cell_pos;
vector<int> alive_color_count;
vector<vector<int>> order_id;
vector<pair<int,int>> DIR = {{0,1},{1,0},{0,-1},{-1,0}};
vector<char> DIRC = {'R','D','L','U'};

vector<pair<int,int>> hebi;
int length_snake = 5;

Clock::time_point DEADLINE;
Clock::time_point SEARCH_DEADLINE;

static constexpr double TIME_LIMIT_SEC = 1.90;
static constexpr double OUTPUT_RESERVE = 0.006; // 出力バッファ（動的補正の下限側）
static constexpr ll NEG_INF = -(1LL << 60);
static constexpr int BEAM_WIDTH_HI = 55;
static constexpr int BEAM_WIDTH_MID = 35;
static constexpr int BEAM_WIDTH_LO = 22;
static constexpr int CANDIDATE_KEEP = 19;
static constexpr int HEAT_RADIUS = 11;
static constexpr int CANDIDATE_EVAL_LIMIT = 16;
static constexpr ll STEP_PENALTY_BEAM = 1;
static constexpr ll STEP_PENALTY_DFS = 1;
static ll W_NEED_DIST = 85;
static ll W_LOOP_REP = 350;
static ll W_ONEWAY = 1400;
static ll W_WRONG_EAT = 24000;
static ll W_ENDGAME_GUIDE = 220;

static constexpr ll BASE_W_NEED_DIST = 85;
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

int map_epoch = 1;
unordered_map<uint64_t, int> memo_ff;
unordered_map<uint64_t, int> memo_lmc;
unordered_map<uint64_t, ll> memo_ps;
unordered_map<uint64_t, bool> memo_rf;
unordered_map<uint64_t, int> memo_nd;

vector<int> scratch_blocked_stamp;
vector<int> scratch_vis_stamp;
vector<int> scratch_queue;
int scratch_stamp_token = 1;

static constexpr size_t MEMO_CAP_FF = 90000;
static constexpr size_t MEMO_CAP_LMC = 90000;
static constexpr size_t MEMO_CAP_PS = 140000;
static constexpr size_t MEMO_CAP_RF = 70000;
static constexpr size_t MEMO_CAP_ND = 180000;

inline void invalidate_search_memo() {
    memo_ff.clear();
    memo_lmc.clear();
    memo_ps.clear();
    memo_rf.clear();
    memo_nd.clear();
}

inline void invalidate_score_memo() {
    memo_ps.clear();
}

inline void maybe_trim_memo() {
    if (memo_ff.size() > MEMO_CAP_FF) memo_ff.clear();
    if (memo_lmc.size() > MEMO_CAP_LMC) memo_lmc.clear();
    if (memo_ps.size() > MEMO_CAP_PS) memo_ps.clear();
    if (memo_rf.size() > MEMO_CAP_RF) memo_rf.clear();
    if (memo_nd.size() > MEMO_CAP_ND) memo_nd.clear();
}

inline void ensure_scratch_buffers() {
    int sz = N * N;
    if ((int)scratch_blocked_stamp.size() != sz) {
        scratch_blocked_stamp.assign(sz, 0);
        scratch_vis_stamp.assign(sz, 0);
        scratch_queue.resize(sz);
        scratch_stamp_token = 1;
    }
}

inline int next_scratch_stamp() {
    if (++scratch_stamp_token == INT_MAX) {
        fill(scratch_blocked_stamp.begin(), scratch_blocked_stamp.end(), 0);
        fill(scratch_vis_stamp.begin(), scratch_vis_stamp.end(), 0);
        scratch_stamp_token = 1;
    }
    return scratch_stamp_token;
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

inline int dir_idx(char ch) {
    if (ch == 'R') return 0;
    if (ch == 'D') return 1;
    if (ch == 'L') return 2;
    if (ch == 'U') return 3;
    return -1;
}

inline int color_future_rank(int color, int curr_len, int look = 4) {
    for (int k = 0; k < look && curr_len + k < M; k++) {
        if (D[curr_len + k] == color) return k;
    }
    return -1;
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

    uint64_t key = (uint64_t)map_epoch;
    key = key * 1315423911ULL + (uint64_t)curr_len;
    key = key * 1315423911ULL + (uint64_t)cell_id(x, y);
    auto it = memo_nd.find(key);
    if (it != memo_nd.end()) return it->second;

    int best = 1e9;
    for (int shift = 0; shift < 3 && curr_len + shift < M; shift++) {
        int target = D[curr_len + shift];
        if (alive_color_count[target] == 0) continue;
        int now_best = 1e9;
        for (int id : color_cells[target]) {
            int i = id / N, j = id % N;
            now_best = min(now_best, abs(i - x) + abs(j - y));
        }
        if (now_best < 1e9) {
            best = min(best, now_best + shift * 2);
            if (best == 0) break;
        }
    }
    int ans = (best == 1e9) ? N * N : best;
    maybe_trim_memo();
    memo_nd[key] = ans;
    return ans;
}

inline ll wrong_eat_penalty(const vector<pair<int,int>>& body, int curr_len) {
    if (curr_len >= M) return 0;
    int target = D[curr_len];
    int remain_food = M - curr_len;
    if (alive_color_count[target] == 0) {
        // 次目標色が盤面に無い時は誤食抑制を緩めて生存を優先。
        return max(2800LL, W_WRONG_EAT / 8);
    }

    auto [hx, hy] = body.back();
    int nd = nearest_required_distance(hx, hy, curr_len);
    if (remain_food > max(7, M / 20)) {
        return max(2200LL, W_WRONG_EAT / 10);
    }
    if (nd >= N * N / 2) return max(3600LL, W_WRONG_EAT / 6);
    if (nd >= N) return max(5200LL, W_WRONG_EAT / 4);
    return W_WRONG_EAT;
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
    return (remain_food <= 7) || (len * 100 >= area * 58);
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
        W_WRONG_EAT = min(160000LL, W_WRONG_EAT + 7000LL * tune_wrong);
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
    // 重み変化時はスコア系キャッシュのみ破棄すれば十分
    invalidate_score_memo();
}

// ===================================================================
// ヒートマップ: 各色の餌が盤面のどこに集中しているかを前計算
// heatmap[col][i][j] = 色col の餌への近さ総和（距離減衰付き）
// ===================================================================
vector<vector<vector<double>>> heatmap;

void apply_food_effect(int sx, int sy, int color, double sign) {
    // 局所マンハッタン近似: 差分更新を高速化
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

// 位置(i,j)から「今後必要な色の餌がどれだけ近くにあるか」の加重スコア
// curr_len: 次に食べるべき目標のインデックス
double future_color_demand_score(int i, int j, int curr_len) {
    double score = 0.0, weight = 1.0;
    for (int k = 0; k < 6 && curr_len + k < M; k++) {
        score += weight * heatmap[D[curr_len + k]][i][j];
        weight *= 0.5;
    }
    return score;
}

// ===================================================================
// flood fill: 頭から到達できるマス数（詰み検出）
// body[1..size-2] を障害物、tail(body[0])は通れる
// ===================================================================
int flood_fill_reachable_raw(const vector<pair<int,int>>& body) {
    auto [hx, hy] = body.back();
    ensure_scratch_buffers();
    int blocked_stamp = next_scratch_stamp();
    int vis_stamp = next_scratch_stamp();

    for (int i = 1; i + 1 < (int)body.size(); i++) {
        scratch_blocked_stamp[cell_id(body[i].first, body[i].second)] = blocked_stamp;
    }

    int qh = 0, qt = 0;
    int start = cell_id(hx, hy);
    scratch_vis_stamp[start] = vis_stamp;
    scratch_queue[qt++] = start;
    int cnt = 0;
    while (qh < qt) {
        int cid = scratch_queue[qh++];
        int cx = cid / N, cy = cid % N;
        cnt++;
        for (auto [dx, dy] : DIR) {
            int nx = cx + dx, ny = cy + dy;
            if (!in_board(nx, ny)) continue;
            int nid = cell_id(nx, ny);
            if (scratch_vis_stamp[nid] == vis_stamp || scratch_blocked_stamp[nid] == blocked_stamp) continue;
            scratch_vis_stamp[nid] = vis_stamp;
            scratch_queue[qt++] = nid;
        }
    }
    return cnt;
}

int flood_fill_reachable(const vector<pair<int,int>>& body) {
    uint64_t key = state_key_with_epoch(body, 0xA17F00DULL);
    auto it = memo_ff.find(key);
    if (it != memo_ff.end()) return it->second;
    int v = flood_fill_reachable_raw(body);
    maybe_trim_memo();
    memo_ff[key] = v;
    return v;
}

inline void remove_color_cell(int color, int id) {
    int pos = color_cell_pos[id];
    if (pos < 0) return;
    auto& vec = color_cells[color];
    int last_id = vec.back();
    vec[pos] = last_id;
    color_cell_pos[last_id] = pos;
    vec.pop_back();
    color_cell_pos[id] = -1;
}

inline void add_color_cell(int color, int id) {
    if (color_cell_pos[id] != -1) return;
    color_cell_pos[id] = (int)color_cells[color].size();
    color_cells[color].push_back(id);
}

// ===================================================================
// get_priority: 今食べようとしている餌の色が目標色列に何番目に合うか
// ===================================================================
ll get_priority(int color, int curr_len) {
    if (curr_len >= M) return 0;
    ll score = 0;
    int remain_food = M - curr_len;
    if (color == D[curr_len]) {
        score += 100000LL;
    } else if (remain_food <= 7) {
        if (curr_len + 1 < M && color == D[curr_len + 1]) score += 22000LL;
        if (curr_len + 2 < M && color == D[curr_len + 2]) score += 5000LL;
        if (curr_len + 3 < M && color == D[curr_len + 3]) score += 1200LL;
        if (curr_len + 4 < M && color == D[curr_len + 4]) score += 300LL;
    } else {
        if (curr_len + 1 < M && color == D[curr_len + 1]) score -= 1800LL;
        if (curr_len + 2 < M && color == D[curr_len + 2]) score -= 3600LL;
        if (curr_len + 3 < M && color == D[curr_len + 3]) score -= 5200LL;
        if (curr_len + 4 < M && color == D[curr_len + 4]) score -= 6800LL;
    }
    return score;
}

// ===================================================================
// simulate_move: 1手シミュレーション
// ===================================================================
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

// ===================================================================
// position_safety: mobility + flood fill の複合安全スコア
// ===================================================================
ll position_safety(const vector<pair<int,int>>& body) {
    maybe_trim_memo();
    uint64_t cache_key = state_key_with_epoch(body, 0x50AFE71ULL);
    auto it_ps = memo_ps.find(cache_key);
    if (it_ps != memo_ps.end()) return it_ps->second;

    auto [hx, hy] = body.back();
    auto [tx, ty] = body.front();

    // mobility (合法手の数)
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

    // 詰み確定
    if (mob == 0) {
        memo_ps[cache_key] = -5000000LL;
        return -5000000LL;
    }

    ll score = mob * 1200LL;

    // 尾との距離を適度に確保（閉じ込め抑制）
    int tail_dist = abs(hx - tx) + abs(hy - ty);
    score += 80LL * tail_dist;

    // flood fill で到達可能マス数を評価
    int ff = flood_fill_reachable(body);
    int bl = (int)body.size();

    if (ff <= 1) {
        // ほぼ詰み
        ll v = -4000000LL + ff * 100LL;
        memo_ps[cache_key] = v;
        return v;
    } else if (ff < bl) {
        // 脱出スペースが蛇の長さより小さい → 危険
        score -= 2500LL * (bl - ff + 1);
    } else {
        // 十分な空間あり
        score += (ll)(log2((double)ff + 1) * 700.0);
    }

    // 1幅通路への過剰侵入を緩く抑制
    if (mob == 1) score -= (W_ONEWAY + 900LL);
    if (mob <= 2 && ff < bl + 4) {
        score -= 1600LL * (bl + 4 - ff);
    }

    memo_ps[cache_key] = score;
    return score;
}

ll outer_bias(int x, int y);

// ===================================================================
// ordered_moves: DFS 枝刈り用、候補手をスコア順にソート
// ===================================================================
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
            if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= wrong_eat_penalty(body, curr_len);
        } else {
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 500.0);
        }
        s += outer_bias(nx, ny);
        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        sc.push_back({s, d});
    }
    sort(sc.rbegin(), sc.rend());
    vector<int> res;
    for (auto &p : sc) res.push_back(p.second);
    return res;
}

// ===================================================================
// score_after: 再帰的な未来評価（depth は 3-4 程度に抑える）
// ===================================================================
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
        if (local <= -2800000LL) { best = max(best, local); continue; }

        auto [nx, ny] = nb.back();
        local += (ll)(future_color_demand_score(nx, ny, ate ? curr_len+1 : curr_len) * 1800.0);

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

// ===================================================================
// dfs_collect: 「次に餌を食べるまでの経路」を列挙
// ===================================================================
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

inline bool should_abort_near_trap(const vector<pair<int,int>>& body, int curr_len) {
    if (in_endgame_mode(body, curr_len)) return false;
    if (M - curr_len <= 10) return false;
    int lm = legal_move_count(body);
    if (lm >= 2) return false;
    int head_cc = flood_fill_reachable(body);
    int len = (int)body.size();
    return head_cc <= len + 4;
}

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
        if (safe <= -2800000LL) {
            path.pop_back();
            continue; // 詰みに向かう手は無視
        }

        ll step = acc_score + safe;
        step -= STEP_PENALTY_DFS * (ll)path.size();
        step += (ll)(future_color_demand_score(nx, ny, ate ? curr_len+1 : curr_len) * 500.0);

        if (ate) {
            ll total = step + get_priority(Map[nx][ny], curr_len);
            // ★ ヒートマップ: 食べた直後のポジションの将来色需要
            total += (ll)(future_color_demand_score(nx, ny, curr_len+1) * 4000.0);
            // ★ 食べた後の未来評価（future_depth は 3-4 に抑える）
            ll future = score_after(nb, curr_len+1, future_depth);
            total += (ll)(future * 0.85);
            out.push_back({total, path, true});
        } else {
            dfs_collect(nb, curr_len, depth-1, path, step, out, future_depth);
        }
        path.pop_back();
    }
}

// ===================================================================
// search_best_path: 反復深化
// 時間予算はターンごとに均等配分（残り時間 / 残りターン数）
// ===================================================================
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
                if (safe <= -2800000LL) continue;
                s += safe;
                s -= STEP_PENALTY_BEAM * (ll)(st.path.size() + 1);

                // A*風: 次に必要な餌までの距離をコスト化
                int need_dist = nearest_required_distance(nx, ny, curr_len);
                s -= W_NEED_DIST * need_dist;

                // ループ回避: 直近経路で同じ頭位置を繰り返すほど減点
                int id = cell_id(nx, ny);
                int rep = 0;
                for (int v : st.head_trace) if (v == id) rep++;
                s -= W_LOOP_REP * rep;

                // 2手詰みの簡易検出
                int legal2 = 0;
                for (int d2 = 0; d2 < 4; d2++) {
                    vector<pair<int,int>> nb2; bool ate2 = false;
                    if (simulate_move(nb, d2, nb2, ate2)) legal2++;
                }
                if (legal2 == 0) s -= 900000LL;

                s += (ll)(future_color_demand_score(nx, ny, curr_len) * 1200.0);
                if (in_endgame_mode(st.body, curr_len)) s += endgame_guide_bonus(st.body, nx, ny);

                string np = st.path;
                np.push_back(DIRC[d]);

                if (ate) {
                    if (curr_len < M && Map[nx][ny] != D[curr_len]) s -= wrong_eat_penalty(st.body, curr_len);
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

    // future_depth は固定3（score_after の再帰深さ上限）
    // 4^3 = 64 ノード程度なので軽い
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
    maybe_trim_memo();
    memo_lmc[key] = cnt;
    return cnt;
}

bool has_reachable_food_raw(const vector<pair<int,int>>& body) {
    auto [hx, hy] = body.back();
    ensure_scratch_buffers();
    int blocked_stamp = next_scratch_stamp();
    int vis_stamp = next_scratch_stamp();

    for (int i = 1; i + 1 < (int)body.size(); i++) {
        scratch_blocked_stamp[cell_id(body[i].first, body[i].second)] = blocked_stamp;
    }

    int qh = 0, qt = 0;
    int start = cell_id(hx, hy);
    scratch_vis_stamp[start] = vis_stamp;
    scratch_queue[qt++] = start;

    while (qh < qt) {
        int cid = scratch_queue[qh++];
        int x = cid / N, y = cid % N;
        if (Map[x][y] != 0) return true;

        for (auto [dx, dy] : DIR) {
            int nx = x + dx, ny = y + dy;
            if (!in_board(nx, ny)) continue;
            int nid = cell_id(nx, ny);
            if (scratch_blocked_stamp[nid] == blocked_stamp || scratch_vis_stamp[nid] == vis_stamp) continue;
            scratch_vis_stamp[nid] = vis_stamp;
            scratch_queue[qt++] = nid;
        }
    }
    return false;
}

bool has_reachable_food(const vector<pair<int,int>>& body) {
    uint64_t key = state_key_with_epoch(body, 0xF00DCAFEULL);
    auto it = memo_rf.find(key);
    if (it != memo_rf.end()) return it->second;
    bool ok = has_reachable_food_raw(body);
    maybe_trim_memo();
    memo_rf[key] = ok;
    return ok;
}

bool has_visible_food_light(const vector<pair<int,int>>& body) {
    auto [hx, hy] = body.back();
    static constexpr int VISIBLE_RADIUS = 3;
    for (int dx = -VISIBLE_RADIUS; dx <= VISIBLE_RADIUS; dx++) {
        int rem = VISIBLE_RADIUS - abs(dx);
        int x = hx + dx;
        if (x < 0 || x >= N) continue;
        for (int dy = -rem; dy <= rem; dy++) {
            int y = hy + dy;
            if (y < 0 || y >= N) continue;
            if (Map[x][y] != 0) return true;
        }
    }
    return false;
}

int move_toward_reachable_food(const vector<pair<int,int>>& body, int curr_len) {
    auto [hx, hy] = body.back();
    ensure_scratch_buffers();
    int blocked_stamp = next_scratch_stamp();

    for (int i = 1; i + 1 < (int)body.size(); i++) {
        scratch_blocked_stamp[cell_id(body[i].first, body[i].second)] = blocked_stamp;
    }

    int sz = N * N;
    vector<int> dist(sz, -1);
    vector<int> first_dir(sz, -1);

    int qh = 0, qt = 0;
    int sid = cell_id(hx, hy);
    scratch_queue[qt++] = sid;
    dist[sid] = 0;

    int best_dir = -1;
    ll best_score = NEG_INF;

    while (qh < qt) {
        int cid = scratch_queue[qh++];
        int x = cid / N, y = cid % N;

        if (Map[x][y] != 0 && cid != sid) {
            int col = Map[x][y];
            int d0 = first_dir[cid];
            if (d0 != -1) {
                if (curr_len < M && col == D[curr_len]) return d0;
                ll score = get_priority(col, curr_len) - 240LL * dist[cid];
                if (score > best_score) {
                    best_score = score;
                    best_dir = d0;
                }
            }
        }

        for (int d = 0; d < 4; d++) {
            int nx = x + DIR[d].first, ny = y + DIR[d].second;
            if (!in_board(nx, ny)) continue;
            int nid = cell_id(nx, ny);
            if (scratch_blocked_stamp[nid] == blocked_stamp) continue;
            if (dist[nid] != -1) continue;

            dist[nid] = dist[cid] + 1;
            first_dir[nid] = (cid == sid ? d : first_dir[cid]);
            scratch_queue[qt++] = nid;
        }
    }

    return best_dir;
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

ll outer_bias(int x, int y) {
    int edge_dist = min(min(x, N - 1 - x), min(y, N - 1 - y));
    return (ll)(max(0, (N / 2) - edge_dist)) * 220LL;
}

int choose_survival_move(const vector<pair<int,int>>& body, int curr_len) {
    int best_d = -1;
    ll best_s = NEG_INF;
    int guided_dir = -1;
    if (M - curr_len <= max(18, N)) {
        guided_dir = move_toward_reachable_food(body, curr_len);
    }

    int cur_bbox = body_bbox_area(body);
    auto [hx, hy] = body.back();
    auto [tx, ty] = body.front();
    int cur_tail_dist = abs(hx - tx) + abs(hy - ty);
    bool stall_mode = (curr_len < M && !has_reachable_food(body));
    bool visible_food = has_visible_food_light(body);
    int remain_food = M - curr_len;

    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        auto [nx, ny] = nb.back();
        ll s = position_safety(nb);
        s += 900LL * legal_move_count(nb);

        int nd = nearest_required_distance(nx, ny, curr_len);
        if (stall_mode && !visible_food) {
            // 到達可能な餌がない間は、近辺で安全に時間を使いながら体を圧縮
            s -= 35LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 420.0);
        } else {
            // 餌が見えた/到達可能になったら追いに行く寄りへ
            s -= 95LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 980.0);
        }

        if (ate) {
            int got = Map[nx][ny];
            s += get_priority(got, curr_len);
            if (curr_len < M) {
                int rank = color_future_rank(got, curr_len, 4);
                if (rank == 0) s += 2500LL;
                else if (rank == 1) s -= 2200LL;
                else if (rank == 2) s -= 4200LL;
                else if (rank == 3) s -= 7000LL;
                else s -= (wrong_eat_penalty(body, curr_len) + 12000LL);
            }
            if (stall_mode && !visible_food && curr_len < M && got != D[curr_len]) {
                s -= wrong_eat_penalty(body, curr_len);
            }
        } else {
            int nbbox = body_bbox_area(nb);
            int ntail = abs(nx - nb.front().first) + abs(ny - nb.front().second);

            // 到達可能な餌が無い間は、うねって圧縮しながら生存継続
            if (stall_mode && !visible_food) {
                s += 180LL * (cur_bbox - nbbox);
                s += 110LL * (cur_tail_dist - ntail);
            }
            if (remain_food <= 3) {
                // 残り3個以下は、すぐ取りに行くよりも安全に巻いてから入る
                s += 260LL * legal_move_count(nb);
                s += 160LL * (ntail - cur_tail_dist);
                s += 70LL * (nbbox - cur_bbox);
            }
        }

        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        if (d == guided_dir) s += 1800LL;
        if (s > best_s) { best_s = s; best_d = d; }
    }
    return best_d;
}

int choose_endgame_cleanup_move(const vector<pair<int,int>>& body, int curr_len) {
    int guided_dir = move_toward_reachable_food(body, curr_len);
    int remain_food = M - curr_len;

    // 残り3個以下は「食べられるなら即食べる」を最優先。
    if (remain_food <= 3 && curr_len < M) {
        int target = D[curr_len];
        int best_exact_d = -1;
        ll best_exact_s = NEG_INF;
        int best_eat_d = -1;
        ll best_eat_s = NEG_INF;
        for (int d = 0; d < 4; d++) {
            vector<pair<int,int>> nb; bool ate = false;
            if (!simulate_move(body, d, nb, ate) || !ate) continue;
            auto [nx, ny] = nb.back();
            ll s = position_safety(nb);
            if (s <= -3200000LL) continue;
            int got = Map[nx][ny];
            if (got == target) {
                s += 200000LL;
                if (s > best_exact_s) {
                    best_exact_s = s;
                    best_exact_d = d;
                }
            }
            s += 70000LL;
            if (s > best_eat_s) {
                best_eat_s = s;
                best_eat_d = d;
            }
        }
        if (best_exact_d != -1) return best_exact_d;
        if (best_eat_d != -1) return best_eat_d;
    }

    int best_d = -1;
    ll best_s = NEG_INF;

    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;

        auto [nx, ny] = nb.back();
        ll s = position_safety(nb);
        if (s <= -2800000LL) continue;

        int nd = nearest_required_distance(nx, ny, curr_len);
        if (remain_food <= 3) {
            ll safety_bias = 0;
            safety_bias += 350LL * legal_move_count(nb);
            safety_bias += 180LL * (abs(nx - nb.front().first) + abs(ny - nb.front().second));
            safety_bias += 90LL * body_bbox_area(nb);
            s += safety_bias;
            s -= 55LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 260.0);
        } else if (remain_food <= 7) {
            s -= 35LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 520.0);
        } else if (remain_food <= max(12, N / 2)) {
            s -= 20LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 420.0);
        } else {
            s -= 110LL * nd;
            s += (ll)(future_color_demand_score(nx, ny, curr_len) * 1100.0);
        }

        if (ate) {
            int got = Map[nx][ny];
            s += get_priority(got, curr_len);
            if (curr_len < M) {
                if (got == D[curr_len]) {
                    s += 15000LL;
                } else {
                    if (remain_food <= 3) {
                        s += 5000LL;
                    } else if (remain_food <= 7) {
                        s += 9000LL;
                    } else if (remain_food <= max(12, N / 2)) {
                        s += 7000LL;
                        if (remain_food <= 10) s += 3500LL;
                    } else {
                        int rank = color_future_rank(got, curr_len, 4);
                        if (rank == 1) s -= 1200LL;
                        else if (rank == 2) s -= 2600LL;
                        else if (rank == 3) s -= 4200LL;
                        else s -= (wrong_eat_penalty(body, curr_len) / 2 + 4000LL);
                    }
                }
            }
        }
        if (d == guided_dir) s += 5000LL;
        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        if (s > best_s) {
            best_s = s;
            best_d = d;
        }
    }

    return best_d;
}

SearchResult choose_candidate_with_rollback(const vector<pair<int,int>>& body, int curr_len,
                                            const vector<SearchResult>& candidates) {
    if (candidates.empty()) return SearchResult{};

    SearchResult picked = candidates.front();
    if (M - curr_len <= 7) {
        ll best_cleanup_total = -(1LL << 60);
        ll best_cleanup_score = -(1LL << 60);
        for (const auto& cand : candidates) {
            if (!cand.ok || cand.path.empty()) continue;
            if (starts_with_banned_prefix(cand.path)) continue;
            ll total = 0;
            ll score = cand.score;
            int eaten = 0;
            int exact = 0;
            int wrong = 0;
            int tmp_len = curr_len;
            auto tmp_body = body;
            for (char ch : cand.path) {
                int d = dir_idx(ch);
                if (d == -1) break;
                vector<pair<int,int>> nb; bool ate = false;
                if (!simulate_move(tmp_body, d, nb, ate)) break;
                tmp_body.swap(nb);
                if (ate) {
                    int got = Map[tmp_body.back().first][tmp_body.back().second];
                    eaten++;
                    if (tmp_len < M && got == D[tmp_len]) exact++;
                    else if (tmp_len < M) wrong++;
                    tmp_len++;
                }
            }
            total = eaten * 1000LL + exact * 120LL - wrong * 20LL;
            if (total > best_cleanup_total || (total == best_cleanup_total && score > best_cleanup_score)) {
                best_cleanup_total = total;
                best_cleanup_score = score;
                picked = cand;
            }
        }
        return picked;
    }

    ll best_key_rate = -(1LL << 60);  // exact率(千分率)の最大化用
    ll best_key_total = -(1LL << 60); // 総摂食数の最大化用
    ll best_key_exact = -(1LL << 60);  // exact の最大化用
    ll best_key_wrong = -(1LL << 60);  // wrong の最小化用(符号反転)
    ll best_key_score = -(1LL << 60);  // 元スコア

    struct ShortEval {
        int idx;
        int total_cnt;
        int exact_rate_mille;
        int exact_cnt;
        int wrong_cnt;
        ll score;
    };
    vector<ShortEval> shortlist;
    shortlist.reserve(min((int)candidates.size(), CANDIDATE_EVAL_LIMIT));

    const int QUICK_STEPS = 8;
    const int FULL_LIMIT = 8;

    struct PathEval {
        bool valid = false;
        int total_cnt = 0;
        int exact_cnt = 0;
        int wrong_cnt = 0;
    };

    auto eval_path = [&](const string& path, int max_steps) -> PathEval {
        PathEval out;
        auto tmp_body = body;
        int tmp_len = curr_len;

        eaten_token++;
        if (eaten_token == INT_MAX) {
            fill(eaten_mark.begin(), eaten_mark.end(), 0);
            eaten_token = 1;
        }
        int token = eaten_token;

        int steps = min((int)path.size(), max_steps);
        for (int i = 0; i < steps; i++) {
            int d = dir_idx(path[i]);
            if (d == -1) return out;

            auto [hx, hy] = tmp_body.back();
            int nx = hx + DIR[d].first, ny = hy + DIR[d].second;
            if (!in_board(nx, ny)) return out;
            if ((int)tmp_body.size() >= 2) {
                auto neck = tmp_body[(int)tmp_body.size()-2];
                if (nx == neck.first && ny == neck.second) return out;
            }

            int nid = cell_id(nx, ny);
            int cell = (eaten_mark[nid] == token) ? 0 : Map[nx][ny];
            bool ate = (cell != 0);
            for (int j = 1; j + 1 < (int)tmp_body.size(); j++) {
                if (tmp_body[j].first == nx && tmp_body[j].second == ny) return out;
            }
            if (ate && nx == tmp_body.front().first && ny == tmp_body.front().second) return out;

            if (!ate) tmp_body.erase(tmp_body.begin());
            tmp_body.push_back({nx, ny});

            if (ate) {
                out.total_cnt++;
                if (tmp_len < M && cell != D[tmp_len]) out.wrong_cnt++;
                else out.exact_cnt++;
                eaten_mark[nid] = token;
                tmp_len++;
            }
        }

        out.valid = true;
        return out;
    };

    int checked = 0;
    for (int ci = 0; ci < (int)candidates.size(); ci++) {
        const auto& cand = candidates[ci];
        if (checked >= CANDIDATE_EVAL_LIMIT) break;
        if (!cand.ok || cand.path.empty()) continue;
        if (starts_with_banned_prefix(cand.path)) continue;
        checked++;

        PathEval e = eval_path(cand.path, QUICK_STEPS);
        if (!e.valid) continue;
        int rate = (e.total_cnt > 0) ? (1000 * e.exact_cnt / e.total_cnt) : 0;
        shortlist.push_back({ci, e.total_cnt, rate, e.exact_cnt, e.wrong_cnt, cand.score});
    }

    sort(shortlist.begin(), shortlist.end(), [](const ShortEval& a, const ShortEval& b) {
        if (a.total_cnt != b.total_cnt) return a.total_cnt > b.total_cnt;
        if (a.exact_rate_mille != b.exact_rate_mille) return a.exact_rate_mille > b.exact_rate_mille;
        if (a.exact_cnt != b.exact_cnt) return a.exact_cnt > b.exact_cnt;
        if (a.wrong_cnt != b.wrong_cnt) return a.wrong_cnt < b.wrong_cnt;
        return a.score > b.score;
    });

    int full_checked = 0;
    for (const auto& se : shortlist) {
        if (full_checked >= FULL_LIMIT) break;
        const auto& cand = candidates[se.idx];
        full_checked++;

        PathEval e = eval_path(cand.path, INT_MAX);
        if (!e.valid) continue;

        ll key_total = e.total_cnt;
        ll key_rate = (e.total_cnt > 0) ? (1000LL * e.exact_cnt / e.total_cnt) : 0LL;
        ll key_exact = e.exact_cnt;
        ll key_wrong = -e.wrong_cnt;
        ll key_score = cand.score;
        bool better = false;
        if (key_total != best_key_total) better = (key_total > best_key_total);
        else if (key_rate != best_key_rate) better = (key_rate > best_key_rate);
        else if (key_exact != best_key_exact) better = (key_exact > best_key_exact);
        else if (key_wrong != best_key_wrong) better = (key_wrong > best_key_wrong);
        else better = (key_score > best_key_score);

        if (better) {
            best_key_rate = key_rate;
            best_key_total = key_total;
            best_key_exact = key_exact;
            best_key_wrong = key_wrong;
            best_key_score = key_score;
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

// ===================================================================
// choose_fallback_move: 経路なしの緊急1手
// ===================================================================
int choose_fallback_move(const vector<pair<int,int>>& body, int curr_len) {
    int guided_dir = -1;
    if (M - curr_len <= max(32, N)) {
        guided_dir = move_toward_reachable_food(body, curr_len);
    }
    int best_d = -1;
    ll best_s = NEG_INF;
    int remain_food = M - curr_len;
    for (int d = 0; d < 4; d++) {
        vector<pair<int,int>> nb; bool ate = false;
        if (!simulate_move(body, d, nb, ate)) continue;
        auto [nx, ny] = nb.back();
        ll s = position_safety(nb);
        int lm = legal_move_count(nb);
        s += 1100LL * lm;
        if (lm <= 1) s -= 2600LL;
        s += (ll)(future_color_demand_score(nx, ny, curr_len) * 1000.0);
        if (remain_food <= 7) {
            s += 480LL * lm;
            s -= 180LL * nearest_required_distance(nx, ny, curr_len);
        }
        if (ate) {
            int got = Map[nx][ny];
            s += get_priority(got, curr_len);
            if (curr_len < M) {
                int rank = color_future_rank(got, curr_len, 4);
                if (rank == 0) s += 3200LL;
                else if (rank == 1) s -= 2600LL;
                else if (rank == 2) s -= 5200LL;
                else if (rank == 3) s -= 8000LL;
                else s -= (wrong_eat_penalty(body, curr_len) + 13000LL);
            }
        }
        if (d == guided_dir) s += 1600LL;
        if (in_endgame_mode(body, curr_len)) s += endgame_guide_bonus(body, nx, ny);
        if (s > best_s) { best_s = s; best_d = d; }
    }
    return best_d;
}

// ===================================================================
// apply_and_output_move
// ===================================================================
bool apply_and_output_move(char ch, vector<pair<int,int>>& body, int& curr_len) {
    int d = dir_idx(ch);
    if (d == -1) return false;
    vector<pair<int,int>> nb; bool ate = false;
    if (!simulate_move(body, d, nb, ate)) return false;
    body.swap(nb);
    tune_moves++;
    if (ate) {
        auto [x, y] = body.back();
        int id = cell_id(x, y);
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
        remove_color_cell(color, id);
        Map[x][y] = 0;
        alive_color_count[color]--;
        map_epoch++;
        if (map_epoch % 64 == 0) build_heatmap();
        invalidate_search_memo();
    }
    return true;
}

void rollback_eat_history_to(int target_size) {
    while ((int)eat_history.size() > target_size) {
        auto ev = eat_history.back(); eat_history.pop_back();
        int id = cell_id(ev.x, ev.y);
        Map[ev.x][ev.y] = ev.color;
        add_color_cell(ev.color, id);
        alive_color_count[ev.color]++;
        apply_food_effect(ev.x, ev.y, ev.color, +1.0);
        if (ev.exact) exact_match_count--;
        map_epoch++;
        if (map_epoch % 64 == 0) build_heatmap();
    }
    invalidate_search_memo();
}

// ===================================================================
// main
// ===================================================================
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> N >> M >> C;
    D.resize(M);
    for (int &x : D) cin >> x;
    Map.assign(N, vector<int>(N));
    color_cell_pos.assign(N * N, -1);
    color_cells.assign(C + 1, {});
    alive_color_count.assign(C + 1, 0);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            cin >> Map[i][j];
            if (Map[i][j] != 0) {
                int col = Map[i][j];
                int id = cell_id(i, j);
                color_cell_pos[id] = (int)color_cells[col].size();
                color_cells[col].push_back(id);
                alive_color_count[col]++;
            }
        }

    hebi = {{0,0},{1,0},{2,0},{3,0},{4,0}};

    auto start = Clock::now();
    DEADLINE = start + chrono::microseconds((ll)(TIME_LIMIT_SEC * 1e6));

    // ヒートマップを最初に構築
    build_heatmap();
    build_order_id();
    eaten_mark.assign(N * N, 0);
    banned_prefixes.clear();

    string answer;
    vector<DecisionCheckpoint> checkpoints;
    double budget_bias = 1.16;
    string best_answer_backup = answer;
    int best_len_backup = length_snake;
    int best_exact_backup = exact_match_count;
    int best_rate_backup = 0;
    int best_step_backup = 0;

    auto update_backup = [&]() {
        int cur_steps = (int)answer.size();
        int eaten_now = max(0, length_snake - 5);
        int rate_now = (eaten_now > 0) ? (1000 * exact_match_count / eaten_now) : 0;
        if (length_snake > best_len_backup ||
            (length_snake == best_len_backup && rate_now > best_rate_backup) ||
            (length_snake == best_len_backup && rate_now == best_rate_backup && exact_match_count > best_exact_backup) ||
            (length_snake == best_len_backup && rate_now == best_rate_backup && exact_match_count == best_exact_backup && cur_steps > best_step_backup)) {
            best_len_backup = length_snake;
            best_rate_backup = rate_now;
            best_exact_backup = exact_match_count;
            best_step_backup = cur_steps;
            best_answer_backup = answer;
        }
    };

    while (length_snake < M && !hard_time_up()) {
        double remaining = hard_time_left_sec();
        if (remaining <= OUTPUT_RESERVE) break;

        // 残り3個以下は重探索を避け、回収を最優先。
        if (M - length_snake <= 3) {
            int d = choose_endgame_cleanup_move(hebi, length_snake);
            if (d == -1) d = choose_fallback_move(hebi, length_snake);
            if (d == -1) d = choose_survival_move(hebi, length_snake);
            if (d == -1) break;
            int before_len = length_snake;
            if (apply_and_output_move(DIRC[d], hebi, length_snake) && length_snake >= before_len) {
                answer.push_back(DIRC[d]);
            }
            update_backup();
            online_tune_weights();
            continue;
        }

        // ターンごとの探索時間予算:
        // 残りターン数を推定し、均等配分する
        // ただし最低でも 0.01 秒、最大でも 0.42 秒
        int turns_left = M - length_snake;
        double reserve = max(OUTPUT_RESERVE, min(0.022, 0.0032 + 0.000016 * (double)turns_left));
        double budget_per_turn = (remaining - reserve) / turns_left;
        budget_per_turn = max(budget_per_turn, 0.01);
        budget_per_turn = min(budget_per_turn * budget_bias, 0.25);

        // 近くに必要色があるターンは探索予算を増やす
        if (has_immediate_target(hebi, length_snake)) {
            budget_per_turn = min(0.29, budget_per_turn * 1.28);
        }

        SEARCH_DEADLINE = Clock::now()
            + chrono::microseconds((ll)(budget_per_turn * 1e6));
        // SEARCH_DEADLINE が DEADLINE を超えないようにする
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

        // 余剰時間があれば探索を追加実行して候補プールを拡張（タイムリミット対策）
        double left0 = search_time_left_sec();
        int max_extra_try = 3;
        if      (left0 >= 0.090) max_extra_try = 6;
        else if (left0 >= 0.060) max_extra_try = 5;
        else if (left0 >= 0.038) max_extra_try = 4;
        else if (left0 >= 0.022) max_extra_try = 3;
        else if (left0 >= 0.012) max_extra_try = 2;

        // 終盤は再探索回数を抑えて、ループ継続と最終掃除に時間を残す
        if (turns_left <= 10) max_extra_try = min(max_extra_try, 1);
        else if (turns_left <= 20) max_extra_try = min(max_extra_try, 2);
        else if (turns_left <= 40) max_extra_try = min(max_extra_try, 4);

        int extra_try = 0;
        while (!time_up() && extra_try < max_extra_try) {
            double left = search_time_left_sec();
            if (left < 0.0120) break;
            if (extra_try >= 1 && left < 0.0200) break;
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

        if (used < budget_per_turn * 0.95) budget_bias = min(2.05, budget_bias * 1.07);
        else if (used > budget_per_turn * 1.02) budget_bias = max(0.90, budget_bias * 0.97);

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
            bool aborted_midway = false;
            for (char ch : best.path) {
                int before_len = length_snake;
                vector<pair<int,int>> prev_body = hebi;
                int prev_hist = (int)eat_history.size();

                if (!apply_and_output_move(ch, hebi, length_snake)) break;
                answer.push_back(ch);
                progressed.push_back(ch);

                // 実行中に詰みが見えたら直前に戻して別候補へ
                if (length_snake < M && legal_move_count(hebi) == 0) {
                    hebi = prev_body;
                    rollback_eat_history_to(prev_hist);
                    length_snake = before_len;
                    tune_deadend++;
                    if (!answer.empty()) answer.pop_back();
                    aborted_midway = true;
                    break;
                }
                if (length_snake < M && should_abort_near_trap(hebi, length_snake)) {
                    hebi = prev_body;
                    rollback_eat_history_to(prev_hist);
                    length_snake = before_len;
                    tune_deadend++;
                    if (!answer.empty()) answer.pop_back();
                    aborted_midway = true;
                    break;
                }

                // 終盤前に小部屋へ閉じ込め傾向なら巻き戻して別ルートへ
                if ((int)progressed.size() % 4 == 0 && turns_left > 24 && hard_time_left_sec() >= 0.16
                    && search_time_left_sec() >= 0.008
                    && legal_move_count(hebi) <= 3
                    && should_rollback_small_region(hebi, length_snake)) {
                    hebi = prev_body;
                    rollback_eat_history_to(prev_hist);
                    length_snake = before_len;
                    if (!answer.empty()) answer.pop_back();
                    tune_deadend++;
                    aborted_midway = true;
                    break;
                }
            }

            if (aborted_midway) {
                auto cp_restore = checkpoints.back();
                hebi = cp_restore.body;
                rollback_eat_history_to(cp_restore.eat_history_size);
                length_snake = cp_restore.curr_len;
                exact_match_count = cp_restore.exact_match_count;
                answer = cp_restore.answer_snapshot;

                if (!progressed.empty()) {
                    banned_prefixes.push_back(progressed);
                    if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                }
            }
            update_backup();
            online_tune_weights();
            continue;
        }

        // フォールバック
        int d = choose_fallback_move(hebi, length_snake);
        if (d == -1) {
            bool restored = false;
            while (!checkpoints.empty() && !restored) {
                auto& cp = checkpoints.back();
                bool tried_this_checkpoint = false;

                while (!restored) {
                    hebi = cp.body;
                    rollback_eat_history_to(cp.eat_history_size);
                    length_snake = cp.curr_len;
                    exact_match_count = cp.exact_match_count;
                    answer = cp.answer_snapshot;

                    SearchResult alt = choose_candidate_with_rollback(hebi, length_snake, cp.alternatives);
                    if (!alt.ok || alt.path.empty()) break;
                    tried_this_checkpoint = true;

                    string progressed;
                    bool aborted_midway = false;
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
                            aborted_midway = true;
                            break;
                        }
                        if (length_snake < M && should_abort_near_trap(hebi, length_snake)) {
                            hebi = prev_body;
                            rollback_eat_history_to(prev_hist);
                            length_snake = before_len;
                            tune_deadend++;
                            if (!answer.empty()) answer.pop_back();
                            aborted_midway = true;
                            break;
                        }
                        if ((int)progressed.size() % 4 == 0 && turns_left > 24 && hard_time_left_sec() >= 0.16
                            && search_time_left_sec() >= 0.008
                            && legal_move_count(hebi) <= 3
                            && should_rollback_small_region(hebi, length_snake)) {
                            hebi = prev_body;
                            rollback_eat_history_to(prev_hist);
                            length_snake = before_len;
                            tune_deadend++;
                            if (!answer.empty()) answer.pop_back();
                            aborted_midway = true;
                            break;
                        }
                    }

                    if (aborted_midway) {
                        hebi = cp.body;
                        rollback_eat_history_to(cp.eat_history_size);
                        length_snake = cp.curr_len;
                        exact_match_count = cp.exact_match_count;
                        answer = cp.answer_snapshot;
                        if (!progressed.empty()) {
                            banned_prefixes.push_back(progressed);
                            if ((int)banned_prefixes.size() > 64) banned_prefixes.pop_front();
                        }
                        continue;
                    }

                    restored = true;
                }

                if (!restored) {
                    if (tried_this_checkpoint || !cp.alternatives.empty()) {
                        checkpoints.pop_back();
                    } else {
                        checkpoints.pop_back();
                    }
                }
            }
            if (!restored) {
                // 探索候補が尽きても、合法手がある限り生存継続して取り切りを狙う
                int sd = in_endgame_mode(hebi, length_snake)
                    ? choose_endgame_cleanup_move(hebi, length_snake)
                    : choose_survival_move(hebi, length_snake);
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

    // 時間が余れば、過去チェックポイントへ戻って行動を再検討する
    if (!hard_time_up() && !checkpoints.empty()) {
        int revisit_idx = (int)checkpoints.size() - 1;
        while (revisit_idx >= 0 && !hard_time_up() && hard_time_left_sec() > OUTPUT_RESERVE + 0.0012) {
            auto cp = checkpoints[revisit_idx--];

            hebi = cp.body;
            rollback_eat_history_to(cp.eat_history_size);
            length_snake = cp.curr_len;
            exact_match_count = cp.exact_match_count;
            answer = cp.answer_snapshot;

            double left_hard = hard_time_left_sec();
            double refine_cap = (length_snake < M) ? 0.040 : 0.022;
            double refine_budget = min(refine_cap, max(0.0070, left_hard * 0.48));
            SEARCH_DEADLINE = Clock::now() + chrono::microseconds((ll)(refine_budget * 1e6));
            if (SEARCH_DEADLINE > DEADLINE - chrono::milliseconds(1)) {
                SEARCH_DEADLINE = DEADLINE - chrono::milliseconds(1);
            }

            SearchPack pack = search_best_path(hebi, length_snake);
            vector<SearchResult> cand = cp.alternatives;
            cand.insert(cand.end(), pack.candidates.begin(), pack.candidates.end());

            if (!time_up() && search_time_left_sec() >= 0.0045) {
                int ban0 = -1;
                if (pack.best.ok && !pack.best.path.empty()) {
                    ban0 = dir_idx(pack.best.path[0]);
                }
                SearchPack extra = search_best_path(hebi, length_snake, ban0, 2);
                cand.insert(cand.end(), extra.candidates.begin(), extra.candidates.end());
            }

            cand = dedup_candidates(move(cand), CANDIDATE_KEEP * 2);
            SearchResult best = choose_candidate_with_rollback(hebi, length_snake, cand);

            if (best.ok && !best.path.empty()) {
                for (char ch : best.path) {
                    int prev_len = length_snake;
                    if (!apply_and_output_move(ch, hebi, length_snake)) break;
                    answer.push_back(ch);
                    if (length_snake < M && legal_move_count(hebi) == 0) break;
                    if (length_snake >= M) break;
                    if (hard_time_up()) break;
                    if (length_snake == prev_len && search_time_left_sec() < 0.0015) break;
                }
            } else {
                int d = choose_fallback_move(hebi, length_snake);
                if (d != -1 && !hard_time_up()) {
                    int prev_len = length_snake;
                    if (apply_and_output_move(DIRC[d], hebi, length_snake) && length_snake >= prev_len) {
                        answer.push_back(DIRC[d]);
                    }
                }
            }

            update_backup();
            online_tune_weights();
        }
    }

    // 最後に現在状態から取り切りを優先した短い掃除を行う
    while (length_snake < M && !hard_time_up() && hard_time_left_sec() > OUTPUT_RESERVE + 0.0001) {
        int d = (M - length_snake <= 7) ? choose_endgame_cleanup_move(hebi, length_snake) : -1;
        if (d == -1) d = choose_fallback_move(hebi, length_snake);
        if (d == -1) d = choose_survival_move(hebi, length_snake);
        if (d == -1) break;
        int before_len = length_snake;
        if (!apply_and_output_move(DIRC[d], hebi, length_snake)) break;
        answer.push_back(DIRC[d]);
        if (length_snake == before_len) break;
    }

    // 最後は現在解とバックアップ解の良い方を出力する
    if ((int)answer.size() > (int)best_answer_backup.size()) {
        best_answer_backup = answer;
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
    ensure_scratch_buffers();
    int blocked_stamp = next_scratch_stamp();
    int vis_stamp = next_scratch_stamp();

    for (int i = 1; i + 1 < (int)body.size(); i++) {
        scratch_blocked_stamp[cell_id(body[i].first, body[i].second)] = blocked_stamp;
    }

    int best = 0;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int sid = cell_id(i, j);
            if (scratch_blocked_stamp[sid] == blocked_stamp || scratch_vis_stamp[sid] == vis_stamp) continue;

            int qh = 0, qt = 0;
            scratch_vis_stamp[sid] = vis_stamp;
            scratch_queue[qt++] = sid;
            int cnt = 0;
            while (qh < qt) {
                int cid = scratch_queue[qh++];
                int x = cid / N, y = cid % N;
                cnt++;
                for (auto [dx, dy] : DIR) {
                    int nx = x + dx, ny = y + dy;
                    if (!in_board(nx, ny)) continue;
                    int nid = cell_id(nx, ny);
                    if (scratch_blocked_stamp[nid] == blocked_stamp || scratch_vis_stamp[nid] == vis_stamp) continue;
                    scratch_vis_stamp[nid] = vis_stamp;
                    scratch_queue[qt++] = nid;
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
    // まず軽量判定: 十分広いなら重い全域連結成分計算を省略
    if (head_cc > len + 14) return false;

    // 時間が薄いときは軽量条件だけで返す
    if (search_time_left_sec() < 0.010) {
        return head_cc <= len + 10;
    }

    int best_cc = largest_free_component(body);
    int gap = best_cc - head_cc;
    return (gap >= max(7, N / 3)) && (head_cc <= len + 12);
}

bool starts_with_banned_prefix(const string& path) {
    for (const auto& pref : banned_prefixes) {
        if ((int)pref.size() <= (int)path.size() && equal(pref.begin(), pref.end(), path.begin())) {
            return true;
        }
    }
    return false;
}