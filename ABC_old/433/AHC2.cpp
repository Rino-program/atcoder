#include <bits/stdc++.h>
using namespace std;

struct Solution {
    vector<int> actions;
    int score;
};

int N, M, K, T;
vector<vector<int>> graph;
vector<vector<char>> adj_matrix;
chrono::system_clock::time_point start_time;
const double TIME_LIMIT = 1.97;
const int MAX_CONE = 25;
const uint32_t CONE_MASK = (1u << MAX_CONE) - 1u;

mt19937 rng;

int rand_int(int l, int r) {
    uniform_int_distribution<int> dist(l, r);
    return dist(rng);
}

double rand_double() {
    uniform_real_distribution<double> dist(0.0, 1.0);
    return dist(rng);
}

struct Cone {
    uint32_t bits = 0;
    int len = 0;
};

inline Cone add_flavor(Cone c, char flavor) {
    int bit = (flavor == 'R') ? 1 : 0;
    c.bits = ((c.bits << 1) | bit) & CONE_MASK;
    if (c.len < MAX_CONE) c.len++;
    return c;
}

inline uint32_t encode_cone(const Cone& c) {
    return (static_cast<uint32_t>(c.len) << MAX_CONE) | c.bits;
}

inline uint32_t encode_added(const Cone& c, char flavor) {
    Cone nc = add_flavor(c, flavor);
    return encode_cone(nc);
}

double elapsed() {
    auto now = chrono::system_clock::now();
    return chrono::duration_cast<chrono::milliseconds>(now - start_time).count() / 1000.0;
}

bool is_adjacent(int a, int b) {
    return adj_matrix[a][b] != 0;
}

vector<int> build_valid_actions(const vector<int>& actions) {
    vector<int> result;
    vector<char> trees(N, 'W');
    int pos = 0;
    int prev = -1;

    for (int act : actions) {
        if (act == -1) {
            if (pos >= K && trees[pos] == 'W') {
                trees[pos] = 'R';
                result.push_back(-1);
            }
            continue;
        }

        if (act < 0 || act >= N) continue;
        if (act == prev) continue;
        if (!is_adjacent(pos, act)) continue;

        result.push_back(act);
        prev = pos;
        pos = act;
    }

    return result;
}

int evaluate(const vector<int>& actions) {
    vector<char> trees(N, 'W');
    vector<unordered_set<uint32_t>> inventory(K);
    int pos = 0, prev = -1;
    Cone cone;
    
    for (int act : actions) {
        if (act == -1) {
            if (pos >= K && trees[pos] == 'W') {
                trees[pos] = 'R';
            }
            continue;
        }
        
        bool valid = false;
        for (int adj : graph[pos]) {
            if (adj == act && adj != prev) {
                valid = true;
                break;
            }
        }
        if (!valid) continue;
        
        prev = pos;
        pos = act;
        
        if (pos >= K) {
            cone = add_flavor(cone, trees[pos]);
        } else {
            inventory[pos].insert(encode_cone(cone));
            cone = Cone();
        }
    }
    
    int total = 0;
    for (const auto& inv : inventory) total += inv.size();
    return total;
}

// 様々なGreedy戦略で初期解を生成
Solution greedy_strategy(int strategy_id) {
    Solution sol;
    vector<char> trees(N, 'W');
    vector<unordered_set<uint32_t>> inventory(K);
    vector<array<char, MAX_CONE + 1>> len_seen(K);
    int pos = 0, prev = -1;
    Cone cone;
    int r_count = 0;
    int target_r = (N - K) * 5 / 7;
    
    while ((int)sol.actions.size() < T) {
        vector<int> cands;
        for (int next : graph[pos]) {
            if (next != prev) cands.push_back(next);
        }
        if (cands.empty()) break;
        
        // 動的R化：近傍ショップの未出パターンに基づいて確率調整
        if ((int)sol.actions.size() < T && pos >= K && trees[pos] == 'W' && r_count < target_r) {
            int demand = 0;
            uint32_t cand_code = encode_added(cone, 'R');
            for (int shop : graph[pos]) {
                if (shop < K && inventory[shop].count(cand_code) == 0) demand++;
            }
            int base_prob = (strategy_id == 0) ? 90 : (strategy_id == 1) ? 110 : 70;
            int prob = max(20, base_prob - demand * 5);
            if (rand_int(0, prob - 1) == 0) {
                sol.actions.push_back(-1);
                trees[pos] = 'R';
                r_count++;
                continue;
            }
        }
        
        // 戦略に応じて評価関数を変える
        int best = cands[0];
        int best_score = -100000;
        for (int next : cands) {
            int sc = 0;
            
            if (next >= K) {
                int fc_len = min(cone.len + 1, MAX_CONE);
                uint32_t fc_code = encode_added(cone, trees[next]);
                if (strategy_id == 0) {
                    // 短さを強く優先
                    if (fc_len == 1) sc = 100;
                    else if (fc_len == 2) sc = 80;
                    else if (fc_len == 3) sc = 60;
                    else if (fc_len <= 5) sc = 30;
                    else sc = 5;
                } else if (strategy_id == 1) {
                    // バランス型
                    if (fc_len <= 3) sc = 50;
                    else if (fc_len <= 6) sc = 30;
                    else sc = 10;
                } else {
                    // 長めのパターンも作る
                    if (fc_len <= 5) sc = 40;
                    else if (fc_len <= 10) sc = 30;
                    else sc = 10;
                }
                
                // 隣接ショップのボーナス
                for (int shop : graph[next]) {
                    if (shop < K && inventory[shop].count(fc_code) == 0) {
                        sc += 30;
                    }
                }
                // 長さの多様性ボーナス
                for (int shop : graph[next]) {
                    if (shop < K && len_seen[shop][fc_len] == 0) {
                        sc += 15;
                    }
                }
            } else {
                uint32_t cone_code = encode_cone(cone);
                if (cone.len > 0 && inventory[next].count(cone_code) == 0) {
                    sc = 100;
                    if (cone.len <= 2) sc += 50;
                    else if (cone.len <= 4) sc += 30;
                } else if (cone.len == 0) {
                    sc = -50;
                }
            }
            
            sc += rand_int(0, 9);
            if (sc > best_score) {
                best_score = sc;
                best = next;
            }
        }
        
        sol.actions.push_back(best);
        prev = pos;
        pos = best;
        
        if (pos >= K) {
            cone = add_flavor(cone, trees[pos]);
            if (cone.len > 0 && rand_int(0, 7) == 0) {
                for (int adj : graph[pos]) {
                    if (adj < K && adj != prev && inventory[adj].count(encode_cone(cone)) == 0) {
                        sol.actions.push_back(adj);
                        inventory[adj].insert(encode_cone(cone));
                        len_seen[adj][cone.len] = 1;
                        cone = Cone();
                        prev = pos;
                        pos = adj;
                        break;
                    }
                }
            }
        } else {
            inventory[pos].insert(encode_cone(cone));
            len_seen[pos][cone.len] = 1;
            cone = Cone();
        }
    }
    
    sol.actions = build_valid_actions(sol.actions);
    sol.score = evaluate(sol.actions);
    return sol;
}

Solution random_strategy(int steps) {
    Solution sol;
    vector<char> trees(N, 'W');
    int pos = 0, prev = -1;
    Cone cone;
    for (int i = 0; i < steps; i++) {
        vector<int> cands;
        for (int next : graph[pos]) if (next != prev) cands.push_back(next);
        if (cands.empty()) break;

        if (pos >= K && trees[pos] == 'W' && rand_int(0, 9) == 0) {
            sol.actions.push_back(-1);
            trees[pos] = 'R';
            continue;
        }

        int next = cands[rand_int(0, (int)cands.size() - 1)];
        sol.actions.push_back(next);
        prev = pos;
        pos = next;
        if (pos >= K) {
            cone = add_flavor(cone, trees[pos]);
        } else {
            cone = Cone();
        }
    }
    sol.actions = build_valid_actions(sol.actions);
    sol.score = evaluate(sol.actions);
    return sol;
}

bool try_repair_segment(vector<int>& actions, int idx, int len) {
    if (actions.empty() || idx < 0 || idx >= (int)actions.size()) return false;

    int pos = 0, prev = -1;
    for (int i = 0; i < idx; i++) {
        int act = actions[i];
        if (act == -1) continue;
        if (!is_adjacent(pos, act) || act == prev) return false;
        prev = pos;
        pos = act;
    }

    int target = -1;
    for (int i = idx + len; i < (int)actions.size(); i++) {
        if (actions[i] >= 0) {
            target = actions[i];
            break;
        }
    }

    vector<int> path;
    function<bool(int,int,int)> dfs = [&](int cur, int pre, int depth) -> bool {
        if (depth == len) {
            if (target < 0) return true;
            return is_adjacent(cur, target) && target != pre;
        }
        auto adjs = graph[cur];
        shuffle(adjs.begin(), adjs.end(), rng);
        for (int nxt : adjs) {
            if (nxt == pre) continue;
            path.push_back(nxt);
            if (dfs(nxt, cur, depth + 1)) return true;
            path.pop_back();
        }
        return false;
    };

    if (!dfs(pos, prev, 0)) return false;

    for (int i = 0; i < len && idx + i < (int)actions.size(); i++) {
        actions[idx + i] = path[i];
    }
    return true;
}

vector<int> mutate_actions(const vector<int>& actions) {
    vector<int> neighbor = actions;
    if (neighbor.empty()) return neighbor;

    int type = rand_int(0, 2);
    if (type == 0) {
        int idx = rand_int(0, (int)neighbor.size() - 1);
        if (neighbor[idx] >= 0) {
            int current_pos = -1;
            for (int j = idx - 1; j >= 0; j--) {
                if (neighbor[j] >= 0) { current_pos = neighbor[j]; break; }
            }
            if (current_pos >= 0) {
                int prev_node = -1;
                for (int j = idx - 2; j >= 0; j--) {
                    if (neighbor[j] >= 0 && neighbor[j] != current_pos) { prev_node = neighbor[j]; break; }
                }
                int next_node = -1;
                for (int j = idx + 1; j < (int)neighbor.size(); j++) {
                    if (neighbor[j] >= 0) { next_node = neighbor[j]; break; }
                }
                vector<int> valid_adjs;
                for (int adj : graph[current_pos]) {
                    if (adj == prev_node) continue;
                    if (next_node >= 0) {
                        if (next_node == current_pos) continue;
                        if (is_adjacent(adj, next_node)) valid_adjs.push_back(adj);
                    } else {
                        valid_adjs.push_back(adj);
                    }
                }
                if (!valid_adjs.empty()) neighbor[idx] = valid_adjs[rand_int(0, (int)valid_adjs.size() - 1)];
            }
        }
    } else if (type == 1) {
        int idx = rand_int(0, (int)neighbor.size() - 1);
        int len = rand_int(2, 5);
        try_repair_segment(neighbor, idx, len);
    } else {
        int idx = rand_int(0, (int)neighbor.size() - 1);
        if (idx + 2 < (int)neighbor.size()) {
            int a = neighbor[idx];
            int b = neighbor[idx + 1];
            if (a >= 0 && b >= 0) {
                neighbor[idx] = b;
                neighbor[idx + 1] = a;
            }
        }
    }

    return neighbor;
}

// 焼きなまし法（カスタマイズ可能・安全版）
Solution simulated_annealing(Solution init, double time_budget, double T0_ratio) {
    Solution best = init;
    Solution current = init;
    
    double T0 = init.score * T0_ratio;
    double T1 = 0.1;
    
    while (elapsed() < time_budget) {
        double progress = (elapsed() - (time_budget - time_budget)) / time_budget;
        progress = max(0.0, min(1.0, progress));
        double temp = T0 * pow(T1 / T0, progress) + 1e-9;
        
        Solution neighbor;
        neighbor.actions = mutate_actions(current.actions);
        neighbor.actions = build_valid_actions(neighbor.actions);
        neighbor.score = evaluate(neighbor.actions);
        
        int delta = neighbor.score - current.score;
        if (delta > 0 || (double)rand() / RAND_MAX < exp((double)delta / (temp + 1e-9))) {
            current = neighbor;
            if (current.score > best.score) {
                best = current;
            }
        }
    }
    
    return best;
}

int main() {
    unsigned seed = (unsigned)chrono::system_clock::now().time_since_epoch().count();
    if (const char* env = getenv("SEED")) {
        seed = static_cast<unsigned>(stoul(env));
    }
    rng.seed(seed);
    start_time = chrono::system_clock::now();
    
    cin >> N >> M >> K >> T;
    
    graph.resize(N);
    for (int i = 0; i < M; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }
    adj_matrix.assign(N, vector<char>(N, 0));
    for (int i = 0; i < N; i++) {
        for (int j : graph[i]) adj_matrix[i][j] = 1;
    }
    
    for (int i = 0; i < N; i++) {
        int x, y;
        cin >> x >> y;
    }
    
    // 多様な初期解生成
    const int NUM_STRATEGIES = 8;
    vector<Solution> solutions;
    solutions.reserve(NUM_STRATEGIES);
    for (int s = 0; s < NUM_STRATEGIES && elapsed() < TIME_LIMIT * 0.2; s++) {
        if (s < 5) solutions.push_back(greedy_strategy(s % 3));
        else solutions.push_back(random_strategy(T / 2));
    }

    Solution best_overall = solutions[0];
    for (auto& sol : solutions) if (sol.score > best_overall.score) best_overall = sol;

    // 適応的な時間配分で探索を継続
    int no_improve = 0;
    while (elapsed() < TIME_LIMIT) {
        double remaining = TIME_LIMIT - elapsed();
        double slice = min(0.12, max(0.02, remaining * 0.2));

        int s = rand_int(0, (int)solutions.size() - 1);
        double T0_ratio = 0.6 + rand_double() * 0.6; // 0.6～1.2

        Solution improved = simulated_annealing(solutions[s], elapsed() + slice, T0_ratio);
        if (improved.score > solutions[s].score) {
            solutions[s] = improved;
        }

        if (improved.score > best_overall.score) {
            best_overall = improved;
            no_improve = 0;
        } else {
            no_improve++;
        }

        if (no_improve >= 8 && elapsed() < TIME_LIMIT * 0.9) {
            // 多様化リスタート
            Solution fresh = (rand_int(0, 1) == 0) ? greedy_strategy(rand_int(0, 2)) : random_strategy(T / 2);
            int worst = 0;
            for (int i = 1; i < (int)solutions.size(); i++) {
                if (solutions[i].score < solutions[worst].score) worst = i;
            }
            solutions[worst] = fresh;
            no_improve = 0;
        }
    }
    
    // 出力
    vector<int> valid_actions = build_valid_actions(best_overall.actions);
    int output_count = min((int)valid_actions.size(), T);
    for (int i = 0; i < output_count; i++) {
        cout << valid_actions[i] << endl;
    }
    
    return 0;
}
