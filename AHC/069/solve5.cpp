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
// 時間管理 & 乱数生成器 (Xorshift64)
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

inline double rand_double() {
    return (double)xorshift64() / 18446744073709551615.0;
}

// ----------------------------------------------------------
// グローバル変数 & 定数
// ----------------------------------------------------------
const int dx[4] = {-1, 1, 0, 0};
const int dy[4] = {0, 0, -1, 1};

int N, M;
double R;
vector<string> grid;
vector<vector<int>> owner; // 各マスの占有グループID (-1: 空き)
int total_grass_cells = 0;

struct Group {
    int id;
    int s, t, p;
    long long v;
    vector<pair<int, int>> pos;
    double c = 0.0;
};

vector<Group> groups;
double sum_efficiency = 0.0;
int processed_count = 0;

// ----------------------------------------------------------
// 計算・評価関数
// ----------------------------------------------------------
int compute_perimeter(const vector<pair<int, int>>& region) {
    static int in_region[50][50] = {0};
    for (const auto& cell : region) in_region[cell.first][cell.second] = 1;

    int L = 0;
    for (const auto& cell : region) {
        for (int d = 0; d < 4; ++d) {
            int nr = cell.first + dx[d];
            int nc = cell.second + dy[d];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || in_region[nr][nc] == 0) {
                L++;
            }
        }
    }
    for (const auto& cell : region) in_region[cell.first][cell.second] = 0;
    return L;
}

double compute_compactness(const vector<pair<int, int>>& region) {
    if (region.empty()) return 0.0;
    int P = region.size();
    int L = compute_perimeter(region);
    if (L == 0) return 0.0;
    return min(1.0, 4.0 * sqrt((double)P) / (double)L);
}

// 壁寄せスコア（周りの障害物・境界と接している数）
int compute_contact_score(const vector<pair<int, int>>& region, int ignore_group_id = -1) {
    int contact = 0;
    static int in_region[50][50] = {0};
    for (const auto& cell : region) in_region[cell.first][cell.second] = 1;

    for (const auto& cell : region) {
        for (int d = 0; d < 4; ++d) {
            int nr = cell.first + dx[d];
            int nc = cell.second + dy[d];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || grid[nr][nc] == '#' || 
               (owner[nr][nc] != -1 && owner[nr][nc] != ignore_group_id && in_region[nr][nc] == 0)) {
                contact++;
            }
        }
    }
    for (const auto& cell : region) in_region[cell.first][cell.second] = 0;
    return contact;
}

// 統合スコア (コンパクト度 + 詰め込み効率)
double evaluate_region(const vector<pair<int, int>>& region, int ignore_group_id = -1) {
    if (region.empty()) return -1e9;
    double C = compute_compactness(region);
    int contact = compute_contact_score(region, ignore_group_id);
    return C * 1000.0 + contact * 1.0;
}

// ----------------------------------------------------------
// 連結性チェック関数
// ----------------------------------------------------------
bool check_connected_without(const vector<pair<int, int>>& region, int remove_idx, int in_region[50][50]) {
    int P = region.size();
    if (P <= 2) return true;

    int start_idx = (remove_idx == 0) ? 1 : 0;
    in_region[region[remove_idx].first][region[remove_idx].second] = 0;

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

    in_region[region[remove_idx].first][region[remove_idx].second] = 1;
    return count == P - 1;
}

// ----------------------------------------------------------
// 時間限界 焼きなまし最適化（常に良い結果のみを更新）
// ----------------------------------------------------------
vector<pair<int, int>> time_bounded_anneal(vector<pair<int, int>> base_region, double end_time, int ignore_group_id = -1) {
    if (base_region.empty()) return base_region;
    int P = base_region.size();
    if (P <= 2) return base_region;

    vector<pair<int, int>> cur_region = base_region;
    vector<pair<int, int>> best_region = base_region;

    double cur_score = evaluate_region(cur_region, ignore_group_id);
    double best_score = cur_score;

    static int in_region[50][50] = {0};
    for (const auto& p : cur_region) in_region[p.first][p.second] = 1;

    int iter = 0;
    while (true) {
        // 時間チェック（256回周期でコスト削減）
        if ((iter & 255) == 0) {
            if (get_elapsed_time() >= end_time) break;
        }
        iter++;

        int rem_idx = rand_int(0, P - 1);
        if (!check_connected_without(cur_region, rem_idx, in_region)) continue;

        static pair<int, int> candidates[600];
        int cand_cnt = 0;

        for (int i = 0; i < P; ++i) {
            if (i == rem_idx) continue;
            for (int d = 0; d < 4; ++d) {
                int nr = cur_region[i].first + dx[d];
                int nc = cur_region[i].second + dy[d];
                if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                    if (grid[nr][nc] == '.' && (owner[nr][nc] == -1 || owner[nr][nc] == ignore_group_id) && !in_region[nr][nc]) {
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

        double new_score = evaluate_region(cur_region, ignore_group_id);

        if (new_score >= cur_score) {
            cur_score = new_score;
            // 常に最良結果のみを採用
            if (cur_score > best_score) {
                best_score = cur_score;
                best_region = cur_region;
            }
        } else {
            // 復元
            in_region[add_cell.first][add_cell.second] = 0;
            in_region[old_cell.first][old_cell.second] = 1;
            cur_region[rem_idx] = old_cell;
        }
    }

    for (const auto& p : cur_region) in_region[p.first][p.second] = 0;
    return best_region;
}

// ----------------------------------------------------------
// 理想テンプレート生成
// ----------------------------------------------------------
vector<vector<pair<int, int>>> generate_templates(int P) {
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

// ----------------------------------------------------------
// テンプレート配置探索 (Best-Fit)
// ----------------------------------------------------------
vector<pair<int, int>> find_best_template_placement(int P, int ignore_group_id = -1) {
    auto templates = generate_templates(P);
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
                bool valid = true;
                vector<pair<int, int>> abs_cells;
                abs_cells.reserve(P);

                for (auto p : temp) {
                    int ar = r + p.first;
                    int ac = c + p.second;
                    if (grid[ar][ac] != '.' || (owner[ar][ac] != -1 && owner[ar][ac] != ignore_group_id)) {
                        valid = false;
                        break;
                    }
                    abs_cells.push_back({ar, ac});
                }

                if (valid) {
                    double score = evaluate_region(abs_cells, ignore_group_id);
                    if (score > best_score) {
                        best_score = score;
                        best_cells = abs_cells;
                    }
                }
            }
        }
    }
    return best_cells;
}

// ----------------------------------------------------------
// フォールバック BFS
// ----------------------------------------------------------
vector<pair<int, int>> find_bfs_region(int P, int ignore_group_id = -1) {
    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            if (grid[r][c] == '.' && (owner[r][c] == -1 || owner[r][c] == ignore_group_id)) {
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
                            if (grid[nr][nc] == '.' && (owner[nr][nc] == -1 || owner[nr][nc] == ignore_group_id)) {
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
// メイン処理
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

    const double TOTAL_TIME_LIMIT = 1.95; // 1.95秒安全限界

    for (int gi = 0; gi < M; ++gi) {
        int id, s, t, p;
        long long v;
        cin >> id >> s >> t >> p >> v;

        Group& g = groups[gi];
        g.id = gi; g.s = s; g.t = t; g.p = p; g.v = v;

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

        double cur_eff = (double)v / (p * max(1, t - s));
        sum_efficiency += cur_eff;
        processed_count++;
        double avg_eff = sum_efficiency / processed_count;

        // 2. 思考時間バジェットの割り当て (残りのターン数に応じた動的割り振り)
        double elapsed = get_elapsed_time();
        double remaining_time = max(0.0, TOTAL_TIME_LIMIT - elapsed);
        double time_budget = remaining_time / (M - gi);
        double turn_end_time = elapsed + time_budget;

        // 3. 初期解生成 (テンプレート & BFS)
        vector<pair<int, int>> best_region = find_best_template_placement(p);
        if (best_region.empty()) {
            best_region = find_bfs_region(p);
        }

        // 4. 移動（Relocation）処理
        int target_relocate_group = -1;
        vector<pair<int, int>> relocate_new_pos;

        if (best_region.empty() && R <= 0.05 && cur_eff >= avg_eff * 0.8) {
            for (int j = 0; j < gi; ++j) {
                if (groups[j].pos.empty()) continue;

                long long move_cost = max(1LL, (long long)llround((double)groups[j].v * R));
                long long expected_gain = llround((double)v * 0.85);

                if (expected_gain - move_cost <= 0) continue;

                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = -1;

                vector<pair<int, int>> candidate_i = find_best_template_placement(p);
                if (candidate_i.empty()) candidate_i = find_bfs_region(p);

                if (!candidate_i.empty()) {
                    for (auto cell : candidate_i) owner[cell.first][cell.second] = gi;

                    relocate_new_pos = find_best_template_placement(groups[j].p);
                    if (relocate_new_pos.empty()) relocate_new_pos = find_bfs_region(groups[j].p);

                    for (auto cell : candidate_i) owner[cell.first][cell.second] = -1;

                    if (!relocate_new_pos.empty()) {
                        target_relocate_group = j;
                        best_region = candidate_i;
                        break;
                    }
                }

                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = j;
            }
        }

        // 5. 【時間いっぱい思考機能】結果が悪化しない安全な焼きなまし最適化
        if (!best_region.empty() && get_elapsed_time() < turn_end_time) {
            best_region = time_bounded_anneal(best_region, turn_end_time);
        }

        // 6. 移動命令の出力
        if (target_relocate_group != -1) {
            cout << 1 << "\n";
            cout << target_relocate_group << "\n";
            for (auto cell : relocate_new_pos) {
                cout << cell.first << " " << cell.second << "\n";
            }
            for (auto cell : groups[target_relocate_group].pos) owner[cell.first][cell.second] = -1;
            for (auto cell : relocate_new_pos) owner[cell.first][cell.second] = target_relocate_group;
            groups[target_relocate_group].pos = relocate_new_pos;
        } else {
            cout << 0 << "\n";
        }

        // 7. 受入判定と出力
        bool accept = false;
        if (!best_region.empty()) {
            double C = compute_compactness(best_region);
            double occupancy = 1.0 - (double)free_grass / total_grass_cells;

            if (C >= 0.35) {
                if (occupancy < 0.65 || cur_eff >= avg_eff * 0.4) {
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
            g.c = compute_compactness(best_region);
        } else {
            cout << "No\n";
        }

        cout.flush();
    }

    return 0;
}