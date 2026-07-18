#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <functional>

using namespace std;

/**
 * AtCoder Heuristic Contest 043 Solution
 * 
 * Approach:
 * 1. Treat the N x N grid as a graph where each cell is a node and 
 *    edges exist between adjacent cells if there is no wall.
 * 2. Use a greedy strategy to fix cards one by one into their target cells.
 * 3. In each step, identify "non-articulation points" of the remaining graph 
 *    of unfixed cells. Removing a non-articulation point ensures the 
 *    graph remains connected, allowing us to move other cards through it later.
 * 4. From the candidate non-articulation points, pick the one whose target 
 *    card is currently closest to it (using BFS to find shortest paths).
 * 5. Move the card to its target cell using a sequence of adjacent swaps 
 *    and mark the cell as "fixed".
 * 6. Repeat for N^2-1 cards. The final card will automatically be in place.
 * 
 * Score: E=0 (solved) is targeted. Minimizing operation count T improves the score.
 */

int N = 20;
int board[20][20];
int pos_r[400], pos_c[400];
bool wall_v[20][20]; // Vertical wall between (i, j) and (i, j+1)
bool wall_h[20][20]; // Horizontal wall between (i, j) and (i+1, j)
bool is_fixed[20][20];

struct Op {
    char type;
    int r, c, h, w;
};

vector<Op> ops;

/**
 * Performs a swap between two adjacent cells (r1, c1) and (r2, c2).
 * Records the operation and updates card positions.
 */
void perform_swap(int r1, int c1, int r2, int c2) {
    if (ops.size() >= 100000) return;
    if (r1 == r2) {
        // Horizontal adjacent swap
        ops.push_back({'H', r1, min(c1, c2), 1, 2});
    } else {
        // Vertical adjacent swap
        ops.push_back({'V', min(r1, r2), c1, 2, 1});
    }
    int card1 = board[r1][c1];
    int card2 = board[r2][c2];
    swap(board[r1][c1], board[r2][c2]);
    pos_r[board[r1][c1]] = r1;
    pos_c[board[r1][c1]] = c1;
    pos_r[board[r2][c2]] = r2;
    pos_c[board[r2][c2]] = c2;
}

/**
 * Finds the shortest path from (sr, sc) to (tr, tc) avoiding fixed cells and walls.
 */
vector<pair<int, int>> find_path(int sr, int sc, int tr, int tc) {
    if (sr == tr && sc == tc) return {};
    queue<pair<int, int>> q;
    q.push({sr, sc});
    vector<vector<pair<int, int>>> parent(N, vector<pair<int, int>>(N, {-1, -1}));
    parent[sr][sc] = {sr, sc};
    
    int dr[] = {0, 0, 1, -1};
    int dc[] = {1, -1, 0, 0};

    while (!q.empty()) {
        pair<int, int> curr = q.front(); q.pop();
        int r = curr.first, c = curr.second;
        if (r == tr && c == tc) break;
        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i], nc = c + dc[i];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || is_fixed[nr][nc]) continue;
            
            // Check for walls between current cell and neighbor
            if (dr[i] == 1 && wall_h[r][c]) continue;
            if (dr[i] == -1 && wall_h[nr][nc]) continue;
            if (dc[i] == 1 && wall_v[r][c]) continue;
            if (dc[i] == -1 && wall_v[r][nc]) continue;
            
            if (parent[nr][nc].first == -1) {
                parent[nr][nc] = {r, c};
                q.push({nr, nc});
            }
        }
    }
    
    vector<pair<int, int>> path;
    if (parent[tr][tc].first == -1) return {}; // No path found
    int cr = tr, cc = tc;
    while (cr != sr || cc != sc) {
        path.push_back({cr, cc});
        pair<int, int> p = parent[cr][cc];
        cr = p.first; cc = p.second;
    }
    reverse(path.begin(), path.end());
    return path;
}

/**
 * Uses Tarjan's algorithm to find all nodes whose removal keeps the remaining unfixed graph connected.
 */
vector<pair<int, int>> get_non_articulation_points() {
    int start_r = -1, start_c = -1;
    int nodes_left = 0;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (!is_fixed[i][j]) {
                nodes_left++;
                if (start_r == -1) { start_r = i; start_c = j; }
            }
        }
    }
    if (nodes_left == 0) return {};
    if (nodes_left == 1) return {{start_r, start_c}};

    vector<vector<int>> disc(N, vector<int>(N, -1)), low(N, vector<int>(N, -1));
    vector<vector<bool>> is_art(N, vector<bool>(N, false));
    int timer = 0;

    function<void(int, int, int, int)> dfs = [&](int r, int c, int pr, int pc) {
        disc[r][c] = low[r][c] = ++timer;
        int children = 0;
        int dr[] = {0, 0, 1, -1};
        int dc[] = {1, -1, 0, 0};
        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i], nc = c + dc[i];
            if (nr < 0 || nr >= N || nc < 0 || nc >= N || is_fixed[nr][nc] || (nr == pr && nc == pc)) continue;
            if (dr[i] == 1 && wall_h[r][c]) continue;
            if (dr[i] == -1 && wall_h[nr][nc]) continue;
            if (dc[i] == 1 && wall_v[r][c]) continue;
            if (dc[i] == -1 && wall_v[r][nc]) continue;

            if (disc[nr][nc] != -1) {
                low[r][c] = min(low[r][c], disc[nr][nc]);
            } else {
                dfs(nr, nc, r, c);
                low[r][c] = min(low[r][c], low[nr][nc]);
                if (low[nr][nc] >= disc[r][c] && pr != -1) is_art[r][c] = true;
                children++;
            }
        }
        if (pr == -1 && children > 1) is_art[r][c] = true;
    };

    dfs(start_r, start_c, -1, -1);
    vector<pair<int, int>> candidates;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (!is_fixed[i][j] && !is_art[i][j]) {
                candidates.push_back({i, j});
            }
        }
    }
    return candidates;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    if (!(cin >> N)) return 0;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            cin >> board[i][j];
            pos_r[board[i][j]] = i;
            pos_c[board[i][j]] = j;
            is_fixed[i][j] = false;
        }
    }
    for (int i = 0; i < N; ++i) {
        string s; cin >> s;
        for (int j = 0; j < N - 1; ++j) wall_v[i][j] = (s[j] == '1');
    }
    for (int i = 0; i < N - 1; ++i) {
        string s; cin >> s;
        for (int j = 0; j < N; ++j) wall_h[i][j] = (s[j] == '1');
    }

    // Sequentially fix N^2-1 cells
    for (int step = 0; step < N * N - 1; ++step) {
        auto candidates = get_non_articulation_points();
        int best_dist = 1000000;
        pair<int, int> best_l = {-1, -1};
        vector<pair<int, int>> best_path;

        for (auto& L : candidates) {
            int tr = L.first, tc = L.second;
            int target_c = tr * N + tc;
            int cr = pos_r[target_c], cc = pos_c[target_c];
            vector<pair<int, int>> path = find_path(cr, cc, tr, tc);
            if ((int)path.size() < best_dist) {
                best_dist = path.size();
                best_l = L;
                best_path = path;
                if (best_dist == 0) break; // Card is already at target, fix it immediately
            }
        }

        if (best_l.first == -1) break;

        // Move the target card to its destination cell
        int tr = best_l.first, tc = best_l.second;
        int target_c = tr * N + tc;
        int curr_r = pos_r[target_c], curr_c = pos_c[target_c];
        for (auto& p : best_path) {
            perform_swap(curr_r, curr_c, p.first, p.second);
            curr_r = p.first; curr_c = p.second;
            if (ops.size() >= 100000) break;
        }
        is_fixed[tr][tc] = true;
        if (ops.size() >= 100000) break;
    }

    // Output operations
    for (auto& op : ops) {
        cout << op.type << " " << op.r << " " << op.c << " " << op.h << " " << op.w << "\n";
    }

    return 0;
}