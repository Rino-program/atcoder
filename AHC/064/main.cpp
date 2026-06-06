#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <random>
#include <queue>
#include <array>
#include <cstdint>
#include <cmath>
#include <cstdlib> // keep exit(0) fast path

using namespace std;
using namespace std::chrono;

enum Action { INIT_ACT, FINALIZE_ACT, DIG_ACT, CLEAR_ACT };

struct Move { int move_type, i, j, k; Action act; };
struct Turn { vector<Move> moves; };

constexpr int MAX_R = 10;
constexpr int MAX_S_CAP = 15;
constexpr int MAX_T_CAP = 20;
constexpr int MAX_CAR = 100;

struct State {
    array<array<int, MAX_S_CAP>, MAX_R> S;
    array<array<int, MAX_T_CAP>, MAX_R> T;
    array<int, MAX_R> s_sz;
    array<int, MAX_R> t_sz;
    array<int, MAX_R> final_cnt;
    array<int, MAX_R> init_cnt;
    array<int, MAX_R> buffer_source;
    int finished_count;
    
    int parent_index;
    vector<Move> last_moves;
    array<int, MAX_R> t_line_score;
    double eval_score;
};

struct Candidate {
    Action act;
    int move_type; 
    int i, j, k;
    double score;
};

static inline uint64_t mix64(uint64_t x) {
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

static inline uint64_t turn_signature(const Turn& turn) {
    uint64_t h = 0x9e3779b97f4a7c15ULL ^ (uint64_t)turn.moves.size();
    for (const auto& m : turn.moves) {
        uint64_t v = (uint64_t)m.move_type;
        v = v * 131 + (uint64_t)m.i;
        v = v * 131 + (uint64_t)m.j;
        v = v * 131 + (uint64_t)m.k;
        h ^= mix64(v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2));
    }
    return h;
}

double evaluate(const State& st, int R) {
    double score = st.finished_count * 100000.0;
    
    for (int j = 0; j < R; ++j) {
        score += st.t_line_score[j];
    }
    return score;
}

Turn generate_turn(const State& st, double noise, mt19937& rng, int R) {
    vector<Candidate> cands;
    cands.reserve(256);
    int total_T_size = 0;
    for(int j=0; j<R; ++j) total_T_size += st.t_sz[j];

    array<int, MAX_CAR> car_pos;
    array<int, MAX_CAR> car_line;
    car_pos.fill(-1);
    car_line.fill(-1);
    for (int j = 0; j < R; ++j) {
        int depth = 0;
        for (int p = st.t_sz[j] - 1; p >= 0; --p) {
            int car = st.T[j][p];
            car_pos[car] = depth;
            car_line[car] = j;
            depth++;
        }
    }

    for (int i = 0; i < R; ++i) {
        int target_car = i * 10 + st.final_cnt[i];
        int target_depth = car_pos[target_car];

        double urgent_bonus = 0.0;
        if (target_depth == 0) urgent_bonus = 50000.0; 
        else if (target_depth > 0 && target_depth <= 2) urgent_bonus = 8000.0;

        if (st.init_cnt[i] > 0) {
            int top_car = st.S[i][st.s_sz[i] - 1];
            int delay = (top_car % 10) - st.final_cnt[top_car / 10];
            if (delay < 0) delay = 10;

            for (int j = 0; j < R; ++j) {
                int space = MAX_T_CAP - st.t_sz[j];
                if (space > 0) {
                    int k = min(st.init_cnt[i], space);
                    double dist_penalty = abs(i - j) * 2.0;
                    double penalty = st.t_sz[j] * (10 - delay) * 1.5 + dist_penalty; 
                    
                    if (total_T_size < R * 18) {
                        cands.push_back({INIT_ACT, 0, i, j, k, 4000.0 + k * 10.0 - penalty + urgent_bonus});
                    } else {
                        cands.push_back({INIT_ACT, 0, i, j, k, 1000.0 + k * 5.0 - penalty + urgent_bonus});
                    }
                }
            }
        }

        int buffer_k = st.s_sz[i] - st.final_cnt[i] - st.init_cnt[i];
        if (buffer_k > 0) {
            int top_car = st.S[i][st.s_sz[i] - 1];
            int delay = (top_car % 10) - st.final_cnt[top_car / 10];
            if (delay < 0) delay = 10;

            for (int j = 0; j < R; ++j) {
                if (j == st.buffer_source[i]) continue; 
                int space = MAX_T_CAP - st.t_sz[j];
                if (space > 0) {
                    int k = min(buffer_k, space);
                    double dist_penalty = abs(i - j) * 2.0;
                    double penalty = st.t_sz[j] * (10 - delay) * 1.5 + dist_penalty;
                    cands.push_back({CLEAR_ACT, 0, i, j, k, 4500.0 + k * 10.0 - penalty + urgent_bonus}); 
                }
            }
        }
    }

    for (int j = 0; j < R; ++j) {
        if (st.t_sz[j] == 0) continue;
        int top = st.T[j][st.t_sz[j] - 1]; 
        int target_line = top / 10;
        
        if (top == target_line * 10 + st.final_cnt[target_line]) {
            if (st.init_cnt[target_line] == 0 && st.s_sz[target_line] == st.final_cnt[target_line]) {
                cands.push_back({FINALIZE_ACT, 1, target_line, j, 1, 100000.0}); 
            }
        }
    }

    for (int target_line = 0; target_line < R; ++target_line) {
        if (st.final_cnt[target_line] == 10) continue;
        
        int target = target_line * 10 + st.final_cnt[target_line];
        int found_j = car_line[target], pos = car_pos[target];
        
        if (found_j != -1 && pos > 0) {
            for (int i = 0; i < R; ++i) {
                if (i == target_line) continue;
                if (st.init_cnt[i] > 0) continue;
                if (st.s_sz[i] - st.final_cnt[i] - st.init_cnt[i] > 0) continue; 
                
                int space = MAX_S_CAP - st.s_sz[i];
                if (space > 0) {
                    int k = min(pos, space);
                    double dist_penalty = abs(i - found_j) * 2.0;
                    double penalty_S = st.final_cnt[i] * 30.0 + dist_penalty; 
                    cands.push_back({DIG_ACT, 1, i, found_j, k, 10000.0 - pos * 20.0 + k * 10.0 - penalty_S});
                }
            }
        }

        if (st.final_cnt[target_line] < 9) {
            int next_target = target + 1; 
            int next_found_j = car_line[next_target], next_pos = car_pos[next_target];

            if (next_found_j != -1 && next_pos > 0) {
                for (int i = 0; i < R; ++i) {
                    if (i == target_line) continue;
                    if (st.init_cnt[i] > 0) continue;
                    if (st.s_sz[i] - st.final_cnt[i] - st.init_cnt[i] > 0) continue; 
                    
                    int space = MAX_S_CAP - st.s_sz[i];
                    if (space > 0) {
                        int k = min(next_pos, space);
                        double dist_penalty = abs(i - next_found_j) * 2.0;
                        double penalty_S = st.final_cnt[i] * 30.0 + dist_penalty; 
                        cands.push_back({DIG_ACT, 1, i, next_found_j, k, 6000.0 - next_pos * 20.0 + k * 10.0 - penalty_S});
                    }
                }
            }
        }
    }

    if (noise > 0.0) {
        uniform_real_distribution<double> dist(0.0, noise);
        for (auto& c : cands) c.score += dist(rng);
    }

    sort(cands.begin(), cands.end(), [](const Candidate& a, const Candidate& b) {
        return a.score > b.score;
    });

    Turn turn;
    turn.moves.reserve(R);
    vector<char> s_used(R, 0), t_used(R, 0);
    vector<int> pending_s_cap(R), pending_t_cap(R);
    for(int i=0; i<R; ++i) pending_s_cap[i] = st.s_sz[i];
    for(int i=0; i<R; ++i) pending_t_cap[i] = st.t_sz[i];

    for (const auto& c : cands) {
        if (s_used[c.i] || t_used[c.j]) continue;
        
        bool cross = false;
        for (const auto& ex : turn.moves) {
            if ((ex.i - c.i) * (ex.j - c.j) <= 0) { cross = true; break; }
        }
        if (cross) continue;

        if (c.move_type == 0) { 
            if (pending_t_cap[c.j] + c.k > 20) continue;
            pending_t_cap[c.j] += c.k;
            pending_s_cap[c.i] -= c.k;
        } else { 
            if (pending_s_cap[c.i] + c.k > 15) continue;
            pending_s_cap[c.i] += c.k;
            pending_t_cap[c.j] -= c.k;
        }

        turn.moves.push_back({c.move_type, c.i, c.j, c.k, c.act});
        s_used[c.i] = true;
        t_used[c.j] = true;
    }
    return turn;
}

State apply_turn(const State& st, const Turn& turn, int R) {
    State next_st = st;
    array<char, MAX_R> touched_t{};
    for (const auto& c : turn.moves) {
        touched_t[c.j] = 1;
        if (c.act == INIT_ACT) {
            for (int d = 0; d < c.k; ++d) {
                next_st.T[c.j][next_st.t_sz[c.j]++] = next_st.S[c.i][next_st.s_sz[c.i] - 1];
                next_st.s_sz[c.i]--;
            }
            next_st.init_cnt[c.i] -= c.k;
        } else if (c.act == CLEAR_ACT) {
            for (int d = 0; d < c.k; ++d) {
                next_st.T[c.j][next_st.t_sz[c.j]++] = next_st.S[c.i][next_st.s_sz[c.i] - 1];
                next_st.s_sz[c.i]--;
            }
            int remaining_buffer = next_st.s_sz[c.i] - next_st.final_cnt[c.i] - next_st.init_cnt[c.i];
            if (remaining_buffer == 0) next_st.buffer_source[c.i] = -1;
        } else if (c.act == FINALIZE_ACT) {
            int car = next_st.T[c.j][next_st.t_sz[c.j] - 1];
            next_st.t_sz[c.j]--;
            next_st.S[c.i][next_st.s_sz[c.i]++] = car;
            next_st.final_cnt[c.i]++;
            next_st.finished_count++;
        } else if (c.act == DIG_ACT) {
            for (int d = 0; d < c.k; ++d) {
                int car = next_st.T[c.j][next_st.t_sz[c.j] - 1];
                next_st.t_sz[c.j]--;
                next_st.S[c.i][next_st.s_sz[c.i]++] = car;
            }
            next_st.buffer_source[c.i] = c.j; 
        }
    }

    double score = next_st.finished_count * 100000.0;
    for (int j = 0; j < R; ++j) {
        if (touched_t[j]) {
            if (next_st.t_sz[j] == 0) {
                next_st.t_line_score[j] = 200;
            } else {
                int line_score = 0;
                int depth = 0;
                for (int p = next_st.t_sz[j] - 1; p >= 0; --p) {
                    int car = next_st.T[j][p];
                    int delay = (car % 10) - next_st.final_cnt[car / 10];
                    if (delay < 0) delay = 10;
                    line_score += depth * delay * 2;
                    depth++;
                }
                next_st.t_line_score[j] = line_score;
            }
        }
        score += next_st.t_line_score[j];
    }
    next_st.eval_score = score;
    return next_st;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    auto start_time = steady_clock::now();
    const double TIME_LIMIT = 1.96;

    int R;
    if (!(cin >> R)) return 0;

    State initial_state{};
    for (int i = 0; i < R; ++i) {
        initial_state.s_sz[i] = 10;
        initial_state.t_sz[i] = 0;
        initial_state.final_cnt[i] = 0;
        initial_state.init_cnt[i] = 10;
        initial_state.buffer_source[i] = -1;
        initial_state.t_line_score[i] = 200;
    }
    initial_state.finished_count = 0;
    initial_state.parent_index = -1;
    initial_state.eval_score = R * 200.0;

    for (int i = 0; i < R; ++i) {
        for (int j = 0; j < 10; ++j) {
            int id; cin >> id;
            initial_state.S[i][j] = id;
        }
    }
    initial_state.eval_score = evaluate(initial_state, R);

    mt19937 rng(42);
    
    const int MAX_TURN = 3000;
    vector<priority_queue<pair<double, int>>> chokudai_qs(MAX_TURN);
    
    vector<State> states;
    states.reserve(2000000); 
    
    states.push_back(initial_state);
    chokudai_qs[0].push({initial_state.eval_score, 0});

    int best_turn_count = 1e9;
    int best_goal_idx = -1;
    
    const array<double, 3> noises = {0.0, 300.0, 800.0};

    int check_cnt = 0;
    bool time_up = false;

    // Allow immediate break from nested loops when time is up.
    while (!time_up) {
        bool updated = false;
        double elapsed = duration<double>(steady_clock::now() - start_time).count();
        int expand_width = 1;
        if (elapsed < TIME_LIMIT * 0.60) expand_width = 3;
        else if (elapsed < TIME_LIMIT * 0.90) expand_width = 2;
        
        for (int t = 0; t < MAX_TURN - 1 && !time_up; ++t) {
            for (int beam = 0; beam < expand_width && !time_up; ++beam) {
                if (chokudai_qs[t].empty()) break;

                int st_idx = chokudai_qs[t].top().second;
                chokudai_qs[t].pop();
                const State& st = states[st_idx];

                array<uint64_t, 3> generated_sig{};
                int generated_sig_cnt = 0;

                for (double n : noises) {
                    // Check elapsed time in the hottest loop.
                    if ((++check_cnt & 31) == 0) {
                        if (duration<double>(steady_clock::now() - start_time).count() > TIME_LIMIT) {
                            time_up = true;
                            break;
                        }
                    }

                    Turn turn = generate_turn(st, n, rng, R);
                    if (turn.moves.empty()) continue;

                    uint64_t sig = turn_signature(turn);
                    bool dup = false;
                    for (int s = 0; s < generated_sig_cnt; ++s) {
                        if (generated_sig[s] == sig) {
                            dup = true;
                            break;
                        }
                    }
                    if (dup) continue;
                    generated_sig[generated_sig_cnt++] = sig;

                    State next_st = apply_turn(st, turn, R);
                    next_st.parent_index = st_idx;
                    next_st.last_moves = turn.moves;

                    states.push_back(next_st);
                    int next_idx = states.size() - 1;

                    if (next_st.finished_count == 10 * R) {
                        if (t + 1 < best_turn_count) {
                            best_turn_count = t + 1;
                            best_goal_idx = next_idx;
                        }
                    } else if (t + 1 < best_turn_count) {
                        chokudai_qs[t + 1].push({next_st.eval_score, next_idx});
                        updated = true;
                    }
                }
            }
        }
        if (!updated) break; 
    }

    if (best_goal_idx == -1) {
        cout << 0 << "\n";
        cout.flush();
        exit(0); // skip destructor overhead on failure path
    }

    vector<Turn> best_ans;
    int curr = best_goal_idx;
    while (states[curr].parent_index != -1) {
        Turn t; 
        t.moves = states[curr].last_moves;
        best_ans.push_back(t);
        curr = states[curr].parent_index;
    }
    reverse(best_ans.begin(), best_ans.end());

    cout << best_ans.size() << "\n";
    for (const auto& t : best_ans) {
        cout << t.moves.size() << "\n";
        for (const auto& m : t.moves) {
            cout << m.move_type << " " << m.i << " " << m.j << " " << m.k << "\n";
        }
    }
    
    cout.flush();
    // Skip expensive vector<State> destruction before process exit.
    exit(0); 
}