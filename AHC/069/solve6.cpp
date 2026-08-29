#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <queue>
#include <chrono>
#include <set>

using namespace std;

// ----------------------------------------------------------
// 時間管理 & 高速乱数 (Xorshift64)
// ----------------------------------------------------------
auto start_time = chrono::steady_clock::now();

inline double get_elapsed_time() {
    auto now = chrono::steady_clock::now();
    return chrono::duration<double>(now - start_time).count();
}

uint64_t rng_state = 88172645463325252ULL;
inline uint64_t xorshift64() {
    uint64_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return rng_state = x;
}

inline int rand_int(int a, int b) {
    return a + (int)(xorshift64() % (b - a + 1));
}

// ----------------------------------------------------------
// 定数 & グローバル変数
// ----------------------------------------------------------
const int dx[4] = {-1, 1, 0, 0};
const int dy[4] = {0, 0, -1, 1};

int N, M;
double R;
vector<string> grid;
vector<vector<int>> owner;
int total_grass_cells = 0;

struct Group {
    int id;
    int s, t, p;
    long long v;
    vector<pair<int, int>> pos;
};

vector<Group> groups;

// オンライン統計変数
double ema_p = 50.0;
double ema_dt = 10000.0;
double ema_v = 10000.0;

// ----------------------------------------------------------
// 完全防御バリデーション (WA を100%防止)
// ----------------------------------------------------------
bool validate_region(const vector<pair<int, int>>& region, int target_P, int ignore_id = -1) {
    if ((int)region.size() != target_P) return false;

    static bool vis[50][50] = {false};
    for (const auto& cell : region) {
        int r = cell.first, c = cell.second;
        if (r < 0 || r >= N || c < 0 || c >= N) return false;
        if (grid[r][c] != '.') return false;
        if (owner[r][c] != -1 && owner[r][c] != ignore_id) return false;
        if (vis[r][c]) return false; // 重複マスチェック
        vis[r][c] = true;
    }

    // BFSによる 4 連結性確認
    static pair<int, int> q[160];
    static bool reached[50][50] = {false};
    int head = 0, tail = 0;

    q[tail++] = region[0];
    reached[region[0].first][region[0].second] = true;
    int count = 0;

    while (head < tail) {
        auto curr = q[head++];
        count++;

        for (int d = 0; d < 4; ++d) {
            int nr = curr.first + dx[d];
            int nc = curr.second + dy[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                if (vis[nr][nc] && !reached[nr][nc]) {
                    reached[nr][nc] = true;
                    q[tail++] = {nr, nc};
                }
            }
        }
    }

    // クリーンアップ
    for (const auto& cell : region) {
        vis[cell.first][cell.second] = false;
        reached[cell.first][cell.second] = false;
    }

    return count == target_P;
}

// ----------------------------------------------------------
// 評価関数 & 外周計算
// ----------------------------------------------------------
int compute_perimeter(const vector<pair<int, int>>& region) {
    static int in_reg[50][50] = {0};
    for (const auto& cell : region) in_reg[cell.first][cell.second] = 1;

    int L = 0;
    for (const auto& cell : region) {
        for (int d = 0; d < 4; ++d) {
            int nr = cell.first + dx[d];
            int nc = cell.second + dy[d];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || in_reg[nr][nc] == 0) {
                L++;
            }
        }
    }
    for (const auto& cell : region) in_reg[cell.first][cell.second] = 0;
    return L;
}

double compute_compactness(const vector<pair<int, int>>& region) {
    if (region.empty()) return 0.0;
    int P = region.size();
    int L = compute_perimeter(region);
    if (L == 0) return 0.0;
    return min(1.0, 4.0 * sqrt((double)P) / (double)L);
}

int compute_contact_score(const vector<pair<int, int>>& region, int ignore_id = -1) {
    static int in_reg[50][50] = {0};
    for (const auto& cell : region) in_reg[cell.first][cell.second] = 1;

    int contact = 0;
    for (const auto& cell : region) {
        for (int d = 0; d < 4; ++d) {
            int nr = cell.first + dx[d];
            int nc = cell.second + dy[d];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || grid[nr][nc] == '#' ||
               (owner[nr][nc] != -1 && owner[nr][nc] != ignore_id && in_reg[nr][nc] == 0)) {
                contact++;
            }
        }
    }
    for (const auto& cell : region) in_reg[cell.first][cell.second] = 0;
    return contact;
}

double evaluate_region(const vector<pair<int, int>>& region, int ignore_id = -1) {
    if (region.empty()) return -1e9;
    double C = compute_compactness(region);
    int contact = compute_contact_score(region, ignore_id);
    return C * 2000.0 + contact * 1.5;
}

// ----------------------------------------------------------
// O(1) 葉ノード判定付き高速連結性チェック
// ----------------------------------------------------------
bool check_connected_fast(const vector<pair<int, int>>& region, int remove_idx, int in_region[50][50]) {
    int P = region.size();
    if (P <= 2) return true;

    int r = region[remove_idx].first;
    int c = region[remove_idx].second;

    int n4 = 0;
    for (int d = 0; d < 4; ++d) {
        int nr = r + dx[d];
        int nc = c + dy[d];
        if (nr >= 0 && nr < N && nc >= 0 && nc < N && in_region[nr][nc]) {
            n4++;
        }
    }

    if (n4 == 1) return true; // 葉ノード (次数1) は削除しても絶対連結

    int start_idx = (remove_idx == 0) ? 1 : 0;
    in_region[r][c] = 0;

    static pair<int, int> q[160];
    static bool vis[50][50] = {false};
    for (const auto& p : region) vis[p.first][p.second] = false;

    int head = 0, tail = 0;
    q[tail++] = region[start_idx];
    vis[region[start_idx].first][region[start_idx].second] = true;

    int count = 0;
    while (head < tail) {
        auto curr = q[head++];
        count++;
        for (int d = 0; d < 4; ++d) {
            int nr = curr.first + dx[d];
            int nc = curr.second + dy[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                if (in_region[nr][nc] && !vis[nr][nc]) {
                    vis[nr][nc] = true;
                    q[tail++] = {nr, nc};
                }
            }
        }
    }

    in_region[r][c] = 1;
    return count == P - 1;
}

// ----------------------------------------------------------
// 高速焼きなまし最適化
// ----------------------------------------------------------
vector<pair<int, int>> ultra_fast_anneal(vector<pair<int, int>> base_region, double end_time, int ignore_id = -1) {
    if (base_region.empty()) return base_region;
    int P = base_region.size();
    if (P <= 2) return base_region;

    vector<pair<int, int>> cur_region = base_region;
    vector<pair<int, int>> best_region = base_region;

    double cur_score = evaluate_region(cur_region, ignore_id);
    double best_score = cur_score;

    static int in_region[50][50] = {0};
    for (const auto& p : cur_region) in_region[p.first][p.second] = 1;

    int iter = 0;
    while (true) {
        if ((iter & 63) == 0) { // 64 ループごとに時間チェック (オーバーシュート防止)
            if (get_elapsed_time() >= end_time) break;
        }
        iter++;

        int rem_idx = rand_int(0, P - 1);
        if (!check_connected_fast(cur_region, rem_idx, in_region)) continue;

        static pair<int, int> candidates[600];
        int cand_cnt = 0;

        for (int i = 0; i < P; ++i) {
            if (i == rem_idx) continue;
            for (int d = 0; d < 4; ++d) {
                int nr = cur_region[i].first + dx[d];
                int nc = cur_region[i].second + dy[d];
                if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                    if (grid[nr][nc] == '.' && (owner[nr][nc] == -1 || owner[nr][nc] == ignore_id) && !in_region[nr][nc]) {
                        candidates[cand_cnt++] = {nr, nc};
                    }
                }
            }
        }

        if (cand_cnt == 0) continue;

        pair<int, int> add_cell = candidates[rand_int(0, cand_cnt - 1)];
        pair<int, int> old_cell = cur_region[rem_idx];

        in_region[old_cell.first][old_cell.second] = 0;
        in_region[add_cell.first][add_cell.second] = 1;
        cur_region[rem_idx] = add_cell;

        double new_score = evaluate_region(cur_region, ignore_id);

        if (new_score >= cur_score) {
            cur_score = new_score;
            if (cur_score > best_score) {
                best_score = cur_score;
                best_region = cur_region;
            }
        } else {
            in_region[add_cell.first][add_cell.second] = 0;
            in_region[old_cell.first][old_cell.second] = 1;
            cur_region[rem_idx] = old_cell;
        }
    }

    for (const auto& p : cur_region) in_region[p.first][p.second] = 0;
    return best_region;
}

// ----------------------------------------------------------
// 高速型テンプレート生成 & 配置探索
// ----------------------------------------------------------
vector<vector<pair<int, int>>> generate_min_perimeter_templates(int P) {
    int W = sqrt(P);
    if (W < 1) W = 1;
    int H = P / W;
    int rem = P - W * H;

    vector<pair<int, int>> base;
    for (int r = 0; r < H; ++r) {
        for (int c = 0; c < W; ++c) {
            base.push_back({r, c});
        }
    }
    int cur_r = H, cur_c = 0;
    while (rem > 0) {
        if (cur_c < W) {
            base.push_back({cur_r, cur_c});
            cur_c++;
        } else {
            cur_r++; cur_c = 0;
            base.push_back({cur_r, cur_c});
            cur_c++;
        }
        rem--;
    }

    vector<vector<pair<int, int>>> templates;
    set<vector<pair<int, int>>> unique_shapes;

    for (int rot = 0; rot < 4; ++rot) {
        vector<pair<int, int>> rotated;
        int min_r = 1e9, min_c = 1e9;
        for (auto p : base) {
            int pr = p.first, pc = p.second;
            int nr = pr, nc = pc;
            if (rot == 1) { nr = pc; nc = -pr; }
            else if (rot == 2) { nr = -pr; nc = -pc; }
            else if (rot == 3) { nr = -pc; nc = pr; }
            rotated.push_back({nr, nc});
            min_r = min(min_r, nr);
            min_c = min(min_c, nc);
        }
        for (auto& p : rotated) {
            p.first -= min_r;
            p.second -= min_c;
        }
        sort(rotated.begin(), rotated.end());
        if (unique_shapes.find(rotated) == unique_shapes.end()) {
            unique_shapes.insert(rotated);
            templates.push_back(rotated);
        }
    }
    return templates;
}

vector<pair<int, int>> find_best_template_placement(int P, int ignore_id = -1) {
    auto templates = generate_min_perimeter_templates(P);
    vector<pair<int, int>> best_cells;
    double best_score = -1e9;

    for (const auto& temp : templates) {
        int max_r = 0, max_c = 0;
        for (auto p : temp) {
            max_r = max(max_r, p.first);
            max_c = max(max_c, p.second);
        }

        for (int r = 0; r + max_r < N; ++r) {
            for (int c = 0; c + max_c < N; ++c) {
                // 高速枝刈り: 起点と終点が不適なら即スキップ
                if (grid[r][c] != '.' || (owner[r][c] != -1 && owner[r][c] != ignore_id)) continue;
                if (grid[r + max_r][c + max_c] != '.' || (owner[r + max_r][c + max_c] != -1 && owner[r + max_r][c + max_c] != ignore_id)) continue;

                bool valid = true;
                vector<pair<int, int>> abs_cells;
                abs_cells.reserve(P);

                for (auto p : temp) {
                    int ar = r + p.first;
                    int ac = c + p.second;
                    if (grid[ar][ac] != '.' || (owner[ar][ac] != -1 && owner[ar][ac] != ignore_id)) {
                        valid = false;
                        break;
                    }
                    abs_cells.push_back({ar, ac});
                }

                if (valid) {
                    double score = evaluate_region(abs_cells, ignore_id);
                    if (score > best_score) {
                        best_score = score;
                        best_cells = abs_cells;
                        // 高速化: コンパクト度 C >= 0.95 の理想形状を見つけたら探索を打ち切り
                        if (compute_compactness(best_cells) >= 0.95) return best_cells;
                    }
                }
            }
        }
    }
    return best_cells;
}

vector<pair<int, int>> find_bfs_region(int P, int ignore_id = -1) {
    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            if (grid[r][c] == '.' && (owner[r][c] == -1 || owner[r][c] == ignore_id)) {
                vector<pair<int, int>> region;
                static bool vis[50][50] = {false};
                queue<pair<int, int>> q;

                q.push({r, c});
                vis[r][c] = true;

                while (!q.empty() && (int)region.size() < P) {
                    auto [cr, cc] = q.front();
                    q.pop();
                    region.push_back({cr, cc});

                    for (int d = 0; d < 4; ++d) {
                        int nr = cr + dx[d];
                        int nc = cc + dy[d];
                        if (nr >= 0 && nr < N && nc >= 0 && nc < N && !vis[nr][nc]) {
                            if (grid[nr][nc] == '.' && (owner[nr][nc] == -1 || owner[nr][nc] == ignore_id)) {
                                vis[nr][nc] = true;
                                q.push({nr, nc});
                            }
                        }
                    }
                }

                for (int i = 0; i < N; ++i)
                    for (int j = 0; j < N; ++j) vis[i][j] = false;

                if ((int)region.size() == P) return region;
            }
        }
    }
    return {};
}

// ----------------------------------------------------------
// メイン制御部
// ----------------------------------------------------------
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N >> M >> R)) return 0;

    grid.resize(N);
    for (int i = 0; i < N; ++i) {
        cin >> grid[i];
        for (int j = 0; j < N; ++j) {
            if (grid[i][j] == '.') total_grass_cells++;
        }
    }

    owner.assign(N, vector<int>(N, -1));
    groups.resize(M);

    const double TOTAL_TIME_LIMIT = 1.80; // 1.8秒制限で安全マージン確保

    for (int gi = 0; gi < M; ++gi) {
        int id, s, t, p;
        long long v;
        cin >> id >> s >> t >> p >> v;

        Group& g = groups[gi];
        g.id = gi; g.s = s; g.t = t; g.p = p; g.v = v;

        // EMA オンライン更新
        ema_p = 0.9 * ema_p + 0.1 * p;
        ema_dt = 0.9 * ema_dt + 0.1 * (t - s);
        ema_v = 0.9 * ema_v + 0.1 * v;

        // 1. 退去処理
        int free_grass = 0;
        for (int j = 0; j < gi; ++j) {
            if (!groups[j].pos.empty() && groups[j].t < s) {
                for (const auto& cell : groups[j].pos) {
                    owner[cell.first][cell.second] = -1;
                }
                groups[j].pos.clear();
            }
        }

        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                if (grid[r][c] == '.' && owner[r][c] == -1) free_grass++;
            }
        }

        // 2. 時間配分
        double elapsed = get_elapsed_time();
        double remaining_time = max(0.0, TOTAL_TIME_LIMIT - elapsed);
        double time_budget = remaining_time / (M - gi);
        double turn_end_time = elapsed + time_budget;

        // 3. 初期配置探索
        vector<pair<int, int>> best_region = find_best_template_placement(p);
        if (best_region.empty()) {
            best_region = find_bfs_region(p);
        }

        // 4. 退避移動探索 (安全な排他制御付き)
        int target_relocate_group = -1;
        vector<pair<int, int>> relocate_new_pos;

        if (best_region.empty() && R <= 0.05 && v >= ema_v * 0.9) {
            for (int j = 0; j < gi; ++j) {
                if (groups[j].pos.empty()) continue;

                long long move_cost = max(1LL, (long long)llround((double)groups[j].v * R));
                if (v * 0.8 - move_cost <= 0) continue;

                // グループ j の領域を一旦クリア
                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = -1;

                vector<pair<int, int>> candidate_i = find_best_template_placement(p);
                if (candidate_i.empty()) candidate_i = find_bfs_region(p);

                if (!candidate_i.empty()) {
                    // グループ i を仮ロック
                    for (auto cell : candidate_i) owner[cell.first][cell.second] = gi;

                    relocate_new_pos = find_best_template_placement(groups[j].p);
                    if (relocate_new_pos.empty()) relocate_new_pos = find_bfs_region(groups[j].p);

                    // 仮ロック解除
                    for (auto cell : candidate_i) owner[cell.first][cell.second] = -1;

                    if (!relocate_new_pos.empty()) {
                        target_relocate_group = j;
                        best_region = candidate_i;

                        // 重要: グループ j の退避先を owner に即座に反映 (SA 衝突を100%防止)
                        for (auto cell : relocate_new_pos) owner[cell.first][cell.second] = target_relocate_group;
                        groups[target_relocate_group].pos = relocate_new_pos;
                        break;
                    }
                }

                // 失敗時は元に戻す
                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = j;
            }
        }

        // 5. 高速 SA 最適化
        if (!best_region.empty() && get_elapsed_time() < turn_end_time) {
            best_region = ultra_fast_anneal(best_region, turn_end_time);
        }

        // 6. 退避移動の出力
        if (target_relocate_group != -1) {
            cout << 1 << "\n";
            cout << target_relocate_group << "\n";
            for (auto cell : relocate_new_pos) {
                cout << cell.first << " " << cell.second << "\n";
            }
        } else {
            cout << 0 << "\n";
        }

        // 7. 受入判定 & 出力 (完全バリデーション)
        bool accept = false;

        // 出力前に絶対検証 (不正があれば安全な BFS 配置にフォールバック)
        if (!validate_region(best_region, p)) {
            best_region = find_bfs_region(p);
        }

        if (validate_region(best_region, p)) {
            double C = compute_compactness(best_region);
            double unit_density = (double)v / (p * max(1, t - s));
            double avg_unit_density = ema_v / (ema_p * max(1.0, ema_dt));
            double free_ratio = (double)free_grass / total_grass_cells;

            if (C >= 0.25) {
                if (free_ratio >= 0.30 || unit_density >= avg_unit_density * 0.40) {
                    accept = true;
                }
            }
        }

        if (accept) {
            cout << "Yes\n";
            for (const auto& cell : best_region) {
                cout << cell.first << " " << cell.second << "\n";
                owner[cell.first][cell.second] = gi;
            }
            g.pos = best_region;
        } else {
            cout << "No\n";
        }

        cout.flush();
    }

    return 0;
}