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
// コンパクト度 & 外周長計算
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

// ----------------------------------------------------------
// 理想テンプレート生成 (正方形に近いポリオミノ)
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
            cur_r++;
            cur_c = 0;
            base.push_back({cur_r, cur_c});
            cur_c++;
        }
        rem--;
    }

    // 4回転パターンの生成 (重複排除)
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
// テンプレート配置探索 (Best-Fit / 壁寄せスコアリング)
// ----------------------------------------------------------
struct Placement {
    int contact_score = -1;
    vector<pair<int, int>> cells;
};

Placement find_best_template_placement(int P, int ignore_group_id = -1) {
    auto templates = generate_templates(P);
    Placement best_p;

    for (const auto& temp : templates) {
        int max_r = 0, max_c = 0;
        for (auto p : temp) {
            max_r = max(max_r, p.first);
            max_c = max(max_c, p.second);
        }

        for (int r = 0; r + max_r < N; ++r) {
            for (int c = 0; c + max_c < N; ++c) {
                bool valid = true;
                int contact = 0;
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

                    // 壁・障害物との接触判定 (Best-Fit壁寄せ評価)
                    for (int d = 0; d < 4; ++d) {
                        int nr = ar + dx[d];
                        int nc = ac + dy[d];
                        if (nr < 0 || nr >= N || nc < 0 || nc >= N || grid[nr][nc] == '#' || 
                           (owner[nr][nc] != -1 && owner[nr][nc] != ignore_group_id)) {
                            contact++;
                        }
                    }
                }

                if (valid && contact > best_p.contact_score) {
                    best_p.contact_score = contact;
                    best_p.cells = abs_cells;
                }
            }
        }
    }
    return best_p;
}

// ----------------------------------------------------------
// フォールバック: 領域収集 (BFS)
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

                // visited リセット
                for (int i = 0; i < N; ++i)
                    for (int j = 0; j < N; ++j) vis[i][j] = false;

                if ((int)region.size() == P) return region;
            }
        }
    }
    return {};
}

// ----------------------------------------------------------
// メイン処理 (インタラクティブ処理)
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

    for (int gi = 0; gi < M; ++gi) {
        int id, s, t, p;
        long long v;
        cin >> id >> s >> t >> p >> v;

        Group& g = groups[gi];
        g.id = gi; g.s = s; g.t = t; g.p = p; g.v = v;

        // 1. 退去時刻が現在時刻 S_i 未満のグループを解放
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

        // 2. 配置場所の最適探索
        Placement placement = find_best_template_placement(p);
        vector<pair<int, int>> best_region = placement.cells;

        if (best_region.empty()) {
            best_region = find_bfs_region(p);
        }

        int target_relocate_group = -1;
        vector<pair<int, int>> relocate_new_pos;

        // 3. 立ち退き・退避処理 (Relocation): 直接置けず、コスト R が低い場合に発動
        if (best_region.empty() && R <= 0.05 && cur_eff >= avg_eff * 0.8) {
            for (int j = 0; j < gi; ++j) {
                if (groups[j].pos.empty()) continue;

                long long move_cost = max(1LL, (long long)llround((double)groups[j].v * R));
                long long expected_gain = llround((double)v * 0.85);

                if (expected_gain - move_cost <= 0) continue;

                // グループ j を仮退去
                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = -1;

                // グループ i の領域探索
                Placement temp_p = find_best_template_placement(p);
                vector<pair<int, int>> candidate_i = temp_p.cells;
                if (candidate_i.empty()) candidate_i = find_bfs_region(p);

                if (!candidate_i.empty()) {
                    // グループ i を仮配置
                    for (auto cell : candidate_i) owner[cell.first][cell.second] = gi;

                    // グループ j の再配置先を探す
                    Placement j_p = find_best_template_placement(groups[j].p);
                    relocate_new_pos = j_p.cells;
                    if (relocate_new_pos.empty()) relocate_new_pos = find_bfs_region(groups[j].p);

                    // グループ i の仮配置を解除
                    for (auto cell : candidate_i) owner[cell.first][cell.second] = -1;

                    if (!relocate_new_pos.empty()) {
                        target_relocate_group = j;
                        best_region = candidate_i;
                        break;
                    }
                }

                // 復元
                for (auto cell : groups[j].pos) owner[cell.first][cell.second] = j;
            }
        }

        // 4. 移動命令の出力
        if (target_relocate_group != -1) {
            cout << 1 << "\n";
            cout << target_relocate_group << "\n";
            for (auto cell : relocate_new_pos) {
                cout << cell.first << " " << cell.second << "\n";
            }
            // マス owner 情報の更新
            for (auto cell : groups[target_relocate_group].pos) owner[cell.first][cell.second] = -1;
            for (auto cell : relocate_new_pos) owner[cell.first][cell.second] = target_relocate_group;
            groups[target_relocate_group].pos = relocate_new_pos;
        } else {
            cout << 0 << "\n";
        }

        // 5. 受入フィルタリング & 判定出力
        bool accept = false;
        if (!best_region.empty()) {
            double C = compute_compactness(best_region);
            double occupancy = 1.0 - (double)free_grass / total_grass_cells;

            // 混雑時には低単価グループを断り、高単価グループ用の空き枠を確保
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

        cout.flush(); // インタラクティブ形式必須のフラッシュ
    }

    return 0;
}