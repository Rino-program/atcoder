#include <bits/stdc++.h>
using namespace std;

struct Solution {
    vector<int> actions;
    int score;
    
    bool operator<(const Solution& other) const {
        return score > other.score; // 降順（スコアが高いほど優先）
    }
};

int N, M, K, T;
vector<vector<int>> graph;
chrono::system_clock::time_point start_time;
const double TIME_LIMIT = 1.95;

double elapsed_time() {
    auto now = chrono::system_clock::now();
    return chrono::duration_cast<chrono::milliseconds>(now - start_time).count() / 1000.0;
}

// 解を評価
int evaluate(const vector<int>& actions) {
    vector<char> trees(N, 'W');
    vector<set<string>> inventory(K);
    int pos = 0, prev = -1;
    string cone = "";
    int valid_actions = 0;
    
    for (int act : actions) {
        if (act == -1) {
            // 木を変更
            if (pos >= K && trees[pos] == 'W') {
                trees[pos] = 'R';
            }
            continue;
        }
        
        // 移動可能性チェック
        bool valid = false;
        for (int adj : graph[pos]) {
            if (adj == act && adj != prev) {
                valid = true;
                break;
            }
        }
        if (!valid) continue;
        
        // 状態を更新
        int old_pos = pos;
        prev = old_pos;
        pos = act;
        valid_actions++;
        
        if (pos >= K) {
            // 木で収穫
            cone += trees[pos];
            if (cone.length() > 25) cone = cone.substr(cone.length() - 25);
        } else {
            // ショップで納品
            inventory[pos].insert(cone);
            cone = "";
        }
    }
    
    int total = 0;
    for (const auto& inv : inventory) total += inv.size();
    return total;
}

// Greedy初期解生成
Solution generate_greedy() {
    Solution sol;
    vector<char> trees(N, 'W');
    vector<set<string>> inventory(K);
    int pos = 0, prev = -1;
    string cone = "";
    int r_count = 0;
    int target_r = (N - K) * 5 / 7;
    
    while ((int)sol.actions.size() < T && elapsed_time() < TIME_LIMIT * 0.1) {
        vector<int> cands;
        for (int next : graph[pos]) {
            if (next != prev) cands.push_back(next);
        }
        if (cands.empty()) break;
        
        if ((int)sol.actions.size() < T && pos >= K && trees[pos] == 'W' && r_count < target_r && rand() % 80 == 0) {
            sol.actions.push_back(-1);
            trees[pos] = 'R';
            r_count++;
            continue;
        }
        
        int best = cands[0];
        int best_score = -1000;
        for (int next : cands) {
            int sc = rand() % 5;
            if (next >= K) {
                string fc = cone + trees[next];
                if (fc.length() <= 3) sc += 20;
                else if (fc.length() <= 5) sc += 10;
                else if (fc.length() <= 8) sc += 3;
            } else if (cone.length() > 0 && inventory[next].count(cone) == 0) {
                sc += 35;
                if (cone.length() <= 3) sc += 12;
            }
            if (sc > best_score) {
                best_score = sc;
                best = next;
            }
        }
        
        sol.actions.push_back(best);
        prev = pos;
        pos = best;
        
        if (pos >= K) {
            cone += trees[pos];
            if (cone.length() > 0 && rand() % 8 == 0) {
                for (int adj : graph[pos]) {
                    if (adj < K && adj != prev && inventory[adj].count(cone) == 0 && (int)sol.actions.size() < T) {
                        sol.actions.push_back(adj);
                        inventory[adj].insert(cone);
                        cone = "";
                        prev = pos;
                        pos = adj;
                        break;
                    }
                }
            }
        } else {
            inventory[pos].insert(cone);
            cone = "";
        }
    }
    
    sol.score = evaluate(sol.actions);
    return sol;
}

// ローカルサーチ（小規模な改善）
Solution local_search(Solution sol, double time_limit) {
    Solution best = sol;
    bool improved = true;
    
    while (improved && elapsed_time() < time_limit) {
        improved = false;
        
        // 各位置での小さな改善
        for (int i = 0; i < (int)best.actions.size() && elapsed_time() < time_limit; i++) {
            // 削除
            if ((int)best.actions.size() > 1) {
                Solution cand = best;
                cand.actions.erase(cand.actions.begin() + i);
                cand.score = evaluate(cand.actions);
                if (cand.score > best.score) {
                    best = cand;
                    improved = true;
                    break;
                }
            }
            
            // 置換（隣接ノード選択）
            if (best.actions[i] >= 0 && best.actions[i] < N) {
                for (int adj : graph[best.actions[i]]) {
                    if (elapsed_time() >= time_limit) break;
                    Solution cand = best;
                    cand.actions[i] = adj;
                    cand.score = evaluate(cand.actions);
                    if (cand.score > best.score) {
                        best = cand;
                        improved = true;
                        break;
                    }
                }
                if (improved) break;
            }
        }
    }
    
    return best;
}

// ビームサーチ的な局所改善
Solution improve_with_beam(Solution sol, int beam_width, double time_budget) {
    Solution best = sol;
    priority_queue<Solution> beam;
    beam.push(sol);
    
    set<string> visited; // 重複チェック
    
    int iterations = 0;
    while (!beam.empty() && elapsed_time() < time_budget) {
        Solution current = beam.top();
        beam.pop();
        
        // 近傍解を生成
        for (int seg_len = 1; seg_len <= 3 && elapsed_time() < time_budget; seg_len++) {
            // セグメントを置換
            for (int start = 0; start < (int)current.actions.size() && elapsed_time() < time_budget; start += max(1, (int)current.actions.size() / 10)) {
                // 削除
                if (current.actions.size() > 1) {
                    Solution neighbor = current;
                    int end = min((int)neighbor.actions.size(), start + seg_len);
                    neighbor.actions.erase(neighbor.actions.begin() + start, neighbor.actions.begin() + end);
                    neighbor.score = evaluate(neighbor.actions);
                    
                    if (neighbor.score > best.score) {
                        best = neighbor;
                    }
                    
                    if (neighbor.score >= current.score * 0.9) {
                        beam.push(neighbor);
                    }
                }
                
                // 置換
                if (start < (int)current.actions.size() && current.actions[start] >= 0) {
                    for (int adj : graph[current.actions[start]]) {
                        Solution neighbor = current;
                        neighbor.actions[start] = adj;
                        neighbor.score = evaluate(neighbor.actions);
                        
                        if (neighbor.score > best.score) {
                            best = neighbor;
                        }
                        
                        if (neighbor.score >= current.score * 0.9) {
                            beam.push(neighbor);
                        }
                        
                        if (elapsed_time() >= time_budget) break;
                    }
                }
            }
        }
        
        // ビーム幅を制限
        while (beam.size() > (size_t)beam_width) {
            beam.pop();
        }
        
        iterations++;
    }
    
    // 最後にローカルサーチ
    best = local_search(best, time_budget);
    return best;
}

// 焼きなまし法
Solution simulated_annealing(Solution initial, double time_budget) {
    Solution best = initial;
    Solution current = initial;
    
    double T0 = 500.0;
    double T1 = 1.0;
    int iter = 0;
    
    while (elapsed_time() < time_budget) {
        double progress = elapsed_time() / time_budget;
        double temp = T0 * pow(T1 / T0, progress);
        
        Solution neighbor = current;
        int modify_count = 1 + rand() % 4;
        
        for (int i = 0; i < modify_count && !neighbor.actions.empty(); i++) {
            int idx = rand() % neighbor.actions.size();
            
            if (rand() % 5 == 0 && neighbor.actions.size() > 1) {
                neighbor.actions.erase(neighbor.actions.begin() + idx);
            } else if (rand() % 5 == 0 && (int)neighbor.actions.size() < T) {
                neighbor.actions.insert(neighbor.actions.begin() + idx, -1);
            } else {
                neighbor.actions[idx] = (rand() % 10 == 0) ? -1 : rand() % N;
            }
        }
        
        neighbor.score = evaluate(neighbor.actions);
        
        int delta = neighbor.score - current.score;
        if (delta > 0 || (double)rand() / RAND_MAX < exp(delta / (temp + 1e-9))) {
            current = neighbor;
            if (current.score > best.score) {
                best = current;
            }
        }
        
        iter++;
    }
    
    return best;
}

int main() {
    srand(time(0));
    start_time = chrono::system_clock::now();
    
    cin >> N >> M >> K >> T;
    
    graph.resize(N);
    for (int i = 0; i < M; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }
    
    for (int i = 0; i < N; i++) {
        int x, y;
        cin >> x >> y;
    }
    
    // Phase 1: 初期解生成（0～10%）
    Solution best_sol = generate_greedy();
    
    // Phase 2: ビームサーチ的改善（10%～50%）
    double phase2_end = TIME_LIMIT * 0.5;
    best_sol = improve_with_beam(best_sol, 50, phase2_end);
    
    // Phase 3: 焼きなまし法（50%～95%）
    double phase3_end = TIME_LIMIT * 0.95;
    Solution sa_result = simulated_annealing(best_sol, phase3_end);
    if (sa_result.score > best_sol.score) {
        best_sol = sa_result;
    }
    
    // Phase 4: 最終チューニング（95%～100%）
    best_sol = improve_with_beam(best_sol, 20, TIME_LIMIT);
    
    // 出力
    int output_count = min((int)best_sol.actions.size(), T);
    for (int i = 0; i < output_count; i++) {
        cout << best_sol.actions[i] << endl;
    }
    
    return 0;
}
