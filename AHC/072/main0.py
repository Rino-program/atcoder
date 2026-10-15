# AtCoder Competition Template v2.3.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/.template/main.py &template.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a

import os, sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
from bisect import bisect_left, bisect_right
from copy import deepcopy
import operator
import heapq
import math
import string

# ===== 設定・制限解除 =====
sys.setrecursionlimit(2*10**6)

# ===== 入力ヘルパ =====
input = lambda: sys.stdin.readline().rstrip()
INT = lambda: int(input())
INT0 = lambda: int(input()) - 1
MAP = lambda: map(int, input().split())
MAP0 = lambda: (int(x) - 1 for x in input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: [int(x) - 1 for x in input().split()]
TUPLE = lambda: tuple(map(int, input().split()))
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

# ===== 高速 print =====
def print(*args, sep=' ', end='\n', file=None, flush=False):
    file = file or sys.stdout
    sep = ' ' if sep is None else sep
    end = '\n' if end is None else end
    file.write(sep.join(map(str, args)) + end)
    flush and file.flush()

# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 関数短縮 =====
pr = print
en = enumerate
hepu = heapq.heappush
hepo = heapq.heappop
bil = bisect_left
bir = bisect_right
dedict = defaultdict

# ===== 方向ベクトル(上(負)から時計回り) =====
DIR4 = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIR8 = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
DIR9 = DIR8 + ((0, 0),) # 中央は最後

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
Yes = lambda **kwargs: print("Yes", **kwargs)
No = lambda **kwargs: print("No", **kwargs)
yes = lambda **kwargs: print("yes", **kwargs)
no = lambda **kwargs: print("no", **kwargs)
YES = lambda **kwargs: print("YES", **kwargs)
NO = lambda **kwargs: print("NO", **kwargs)

def yn(cond: bool, yes: str = "Yes", no: str = "No", **kwargs) -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no, **kwargs)

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    print('\n'.join(sep.join(map(str, row)) for row in grid))

# ===== デバッグ =====
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, sep=' ', end='\n', flush=False) -> None:
        """デバッグ出力（標準エラー）"""
        print("[DEBUG]", *args, sep=sep, end=end, file=sys.stderr, flush=flush)
else:
    def debug(*args, **kwargs) -> None:
        pass

# ===== template.py =====

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # =========================================================================
    # [SECTION 1-1: 入力受け取りと盤面情報のパース]
    # =========================================================================
    first = LIST()
    if len(first) >= 2:
        N, K = first[0], first[1]
    else:
        N = first[0]
        K = 12

    grid = STRS(N)

    is_wall = [[False] * N for _ in range(N)]
    is_nest = [[None] * N for _ in range(N)]
    nest_pos = {}
    stacks = [[[] for _ in range(N)] for _ in range(N)]

    for r in range(N):
        for c in range(N):
            ch = grid[r][c]
            if ch == '#':
                is_wall[r][c] = True
            elif 'a' <= ch <= 'l':
                color = ord(ch) - ord('a')
                stacks[r][c].append(color)
            elif 'A' <= ch <= 'L':
                color = ord(ch) - ord('A')
                is_nest[r][c] = color
                nest_pos[color] = (r, c)

    if nest_pos:
        K = max(K, max(nest_pos.keys()) + 1)

    # =========================================================================
    # [SECTION 1-2: 最上段スライムの差分管理用データ構造と更新関数]
    # =========================================================================
    top_color = [[-1] * N for _ in range(N)]
    slimes_by_color = [set() for _ in range(K)]

    def update_cell(r: int, c: int) -> None:
        """マスの最上段の色の変化を検知し、差分を更新する"""
        old_c = top_color[r][c]
        new_c = stacks[r][c][-1] if stacks[r][c] else -1
        if old_c == new_c:
            return
        if old_c != -1:
            slimes_by_color[old_c].discard((r, c))
        if new_c != -1:
            slimes_by_color[new_c].add((r, c))
        top_color[r][c] = new_c

    for r in range(N):
        for c in range(N):
            if stacks[r][c]:
                top_color[r][c] = stacks[r][c][-1]
                slimes_by_color[stacks[r][c][-1]].add((r, c))

    # =========================================================================
    # [SECTION 1-3: 方向定義と探索定数]
    # =========================================================================
    DIRECTIONS = [
        ('U', -1, 0),
        ('R', 0, 1),
        ('D', 1, 0),
        ('L', 0, -1),
    ]

    ans = []
    MAX_OPS = 99990
    PHASE2_MAX_MERGE_DIST = 4  # 寄り道を許容する最大床距離

    # =========================================================================
    # [SECTION 2-1: マス間最短距離マップ (get_dist_map) と巣からの距離]
    # =========================================================================
    dist_map_cache = {}

    def get_dist_map(pos):
        """床のみを通るマス間最短距離マップ（BFS）"""
        if pos in dist_map_cache:
            return dist_map_cache[pos]
        d_map = [[INF] * N for _ in range(N)]
        sr, sc = pos
        d_map[sr][sc] = 0
        q = deque([(sr, sc)])
        while q:
            r, c = q.popleft()
            for dr, dc in DIR4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < N and 0 <= nc < N and not is_wall[nr][nc]:
                    if d_map[nr][nc] == INF:
                        d_map[nr][nc] = d_map[r][c] + 1
                        q.append((nr, nc))
        dist_map_cache[pos] = d_map
        return d_map

    # 各巣からの最短距離マップ
    dist = []
    for c in range(K):
        if c in nest_pos:
            dist.append(get_dist_map(nest_pos[c]))
        else:
            dist.append([[INF] * N for _ in range(N)])

    # =========================================================================
    # [SECTION 2-2: 最大飛距離考慮ジャンプ距離マップ (get_jump_dist)]
    # =========================================================================
    jump_dist_cache = {}

    def get_jump_dist(target_coord, max_len):
        """ジャンプ飛距離 max_len を考慮した最小操作回数マップ（BFS）"""
        key = (target_coord, max_len)
        if key in jump_dist_cache:
            return jump_dist_cache[key]
        j_dist = [[INF] * N for _ in range(N)]
        tr, tc = target_coord
        j_dist[tr][tc] = 0
        q = deque([(tr, tc)])
        while q:
            r, c = q.popleft()
            d_cur = j_dist[r][c]
            for _, dr, dc in DIRECTIONS:
                for l in range(1, max_len + 1):
                    nr = r + dr * l
                    nc = c + dc * l
                    if not (0 <= nr < N and 0 <= nc < N):
                        break
                    if is_wall[nr][nc]:
                        break
                    if j_dist[nr][nc] == INF:
                        j_dist[nr][nc] = d_cur + 1
                        q.append((nr, nc))
        jump_dist_cache[key] = j_dist
        return j_dist

    # =========================================================================
    # [SECTION 4-1: フェーズ2 状態管理変数と次回搬送対象の探索]
    # =========================================================================
    import random

    stuck_slimes = set()
    skipped_slimes = set()
    height8_pending = {}
    
    # 大域的な直近移動履歴（直近6手でピンポン・三角巡回を防止）
    global_recent_moves = deque(maxlen=6)
    # SECTION 6-1 のブーストコンボのクールダウン管理: (r, c) -> 解除 ans 長さ
    combo_cooldown = {}

    while len(ans) < MAX_OPS:
        cur_ans_len = len(ans)
        height8_pending = {pos: unl for pos, unl in height8_pending.items() if cur_ans_len < unl}
        combo_cooldown = {pos: unl for pos, unl in combo_cooldown.items() if cur_ans_len < unl}

        best_slime = None
        best_pri = (-1, -1)
        is_height_8 = False

        # 1. 高さ8のスライムを最優先で探索（遠い方から）
        for c_idx in range(K):
            for r, c in slimes_by_color[c_idx]:
                if len(stacks[r][c]) == 8:
                    if (r, c) not in stuck_slimes and (r, c) not in height8_pending and (r, c) not in skipped_slimes:
                        d = dist[c_idx][r][c]
                        if d < INF and d > best_pri[0]:
                            best_pri = (d, 8)
                            best_slime = (r, c)
                            is_height_8 = True

        # 2. 通常のスライムを探索（巣から遠い方最優先、同距離なら高さが高い合流塔を優先）
        if best_slime is None:
            best_pri = (-1, -1)
            for c_idx in range(K):
                for r, c in slimes_by_color[c_idx]:
                    if (r, c) not in stuck_slimes and (r, c) not in skipped_slimes and (r, c) not in height8_pending:
                        d = dist[c_idx][r][c]
                        if d < INF:
                            h_val = len(stacks[r][c])
                            pri = (d, h_val)
                            if pri > best_pri:
                                best_pri = pri
                                best_slime = (r, c)
                                is_height_8 = False

        # スライムが見つからない場合、保留・スキップを解除して再挑戦（スタックはSECTION 5で打開）
        if best_slime is None:
            if height8_pending:
                height8_pending.clear()
                continue
            if skipped_slimes:
                skipped_slimes.clear()
                continue

        # =====================================================================
        # [SECTION 5-1: 詰まり復帰処理 - 前進・退避（道あけ）探索]
        # =====================================================================
        if best_slime is None:
            if height8_pending:
                height8_pending.clear()
                continue

            if skipped_slimes:
                skipped_slimes.clear()
                continue

            all_slimes = []
            for c_idx in range(K):
                for r, c in slimes_by_color[c_idx]:
                    all_slimes.append((len(stacks[r][c]), dist[c_idx][r][c], r, c))

            if not all_slimes:
                break

            # 塔の高さが高いもの、同高さなら巣から遠いものを優先
            all_slimes.sort(key=lambda x: (x[0], x[1]), reverse=True)

            fallback_move = None
            best_fb_score = (-INF, -INF, -INF)

            # 優先度1: 前進できる手があるか全スライムから探索
            for _, _, hr, hc in all_slimes:
                clr = stacks[hr][hc][-1]
                cur_h = len(stacks[hr][hc])
                sc = sum(1 for v in reversed(stacks[hr][hc]) if v == clr)
                c_dist = dist[clr][hr][hc]

                for move_cnt in range(sc, 0, -1):
                    k_val = cur_h - move_cnt
                    max_l_val = k_val + 1

                    for d_str, dr, dc in DIRECTIONS:
                        for l_val in range(1, max_l_val + 1):
                            tr = hr + dr * l_val
                            tc = hc + dc * l_val
                            if not (0 <= tr < N and 0 <= tc < N):
                                break
                            if is_wall[tr][tc]:
                                break
                            if len(stacks[tr][tc]) + move_cnt > 8:
                                continue

                            # 直近の往復ピンポンは禁止
                            if ((hr, hc), (tr, tc)) in global_recent_moves or ((tr, tc), (hr, hc)) in global_recent_moves:
                                continue

                            cand_d = dist[clr][tr][tc]
                            if cand_d < c_dist:
                                delta = c_dist - cand_d
                                score = (delta, -cand_d, -l_val)
                                if score > best_fb_score:
                                    best_fb_score = score
                                    fallback_move = (hr, hc, k_val, d_str, l_val, tr, tc)

                if fallback_move is not None:
                    break

            # 優先度2: 前進できない場合、空きマスへの退避（道あけ）を全スライムから探索
            if fallback_move is None:
                for _, _, hr, hc in all_slimes:
                    clr = stacks[hr][hc][-1]
                    cur_h = len(stacks[hr][hc])
                    sc = sum(1 for v in reversed(stacks[hr][hc]) if v == clr)

                    for move_cnt in range(sc, 0, -1):
                        k_val = cur_h - move_cnt
                        max_l_val = k_val + 1

                        for d_str, dr, dc in DIRECTIONS:
                            for l_val in range(1, max_l_val + 1):
                                tr = hr + dr * l_val
                                tc = hc + dc * l_val
                                if not (0 <= tr < N and 0 <= tc < N):
                                    break
                                if is_wall[tr][tc]:
                                    break
                                # 空きマスへの退避を最優先
                                if len(stacks[tr][tc]) == 0:
                                    if ((hr, hc), (tr, tc)) in global_recent_moves or ((tr, tc), (hr, hc)) in global_recent_moves:
                                        continue
                                    fallback_move = (hr, hc, k_val, d_str, l_val, tr, tc)
                                    break
                            if fallback_move is not None:
                                break
                        if fallback_move is not None:
                            break
                    if fallback_move is not None:
                        break

            # =================================================================
            # [SECTION 5-2: 詰まり復帰処理 - 全探索退避 ＆ 最後のセーフティネット]
            # =================================================================
            # 優先度3: 全スライムから履歴に引っかからない合法的1手を探索
            if fallback_move is None:
                all_slime_coords = [pos for c_set in slimes_by_color for pos in c_set]
                random.shuffle(all_slime_coords)
                
                for sr, sc in all_slime_coords:
                    clr = stacks[sr][sc][-1]
                    h = len(stacks[sr][sc])
                    sc_cnt = sum(1 for v in reversed(stacks[sr][sc]) if v == clr)

                    for move_cnt in range(sc_cnt, 0, -1):
                        k_val = h - move_cnt
                        max_l_val = k_val + 1

                        for d_str, dr, dc in DIRECTIONS:
                            for l_val in range(1, max_l_val + 1):
                                tr = sr + dr * l_val
                                tc = sc + dc * l_val
                                if not (0 <= tr < N and 0 <= tc < N) or is_wall[tr][tc]:
                                    break
                                if len(stacks[tr][tc]) + move_cnt <= 8:
                                    if ((sr, sc), (tr, tc)) not in global_recent_moves and ((tr, tc), (sr, sc)) not in global_recent_moves:
                                        fallback_move = (sr, sc, k_val, d_str, l_val, tr, tc)
                                        break
                            if fallback_move is not None:
                                break
                        if fallback_move is not None:
                            break
                    if fallback_move is not None:
                        break

            # 優先度4 (最後のセーフティネット): 履歴で窒息している場合、履歴制限を解除して確実に動かす
            if fallback_move is None:
                global_recent_moves.clear()  # 窒息を解除
                cand_safety = []
                all_slime_coords = [pos for c_set in slimes_by_color for pos in c_set]

                for sr, sc in all_slime_coords:
                    clr = stacks[sr][sc][-1]
                    h = len(stacks[sr][sc])
                    sc_cnt = sum(1 for v in reversed(stacks[sr][sc]) if v == clr)

                    for move_cnt in range(sc_cnt, 0, -1):
                        k_val = h - move_cnt
                        max_l_val = k_val + 1

                        for d_str, dr, dc in DIRECTIONS:
                            for l_val in range(1, max_l_val + 1):
                                tr = sr + dr * l_val
                                tc = sc + dc * l_val
                                if not (0 <= tr < N and 0 <= tc < N) or is_wall[tr][tc]:
                                    break
                                if len(stacks[tr][tc]) + move_cnt <= 8:
                                    # 巣への距離が近い、または空きマスを優先
                                    d_cand = dist[clr][tr][tc]
                                    cand_safety.append((d_cand, sr, sc, k_val, d_str, l_val, tr, tc))

                if cand_safety:
                    cand_safety.sort(key=lambda x: x[0])  # 最も巣に近いマスへ跳ぶ
                    _, b_sr, b_sc, b_k, b_d, b_l, b_tr, b_tc = cand_safety[0]
                    fallback_move = (b_sr, b_sc, b_k, b_d, b_l, b_tr, b_tc)

            # 盤面上に物理的に合法手が1手も存在しない場合のみ終了
            if fallback_move is None:
                break

            f_hr, f_hc, f_k, f_d_str, f_l, f_tr, f_tc = fallback_move
            ans.append(f"{f_hr} {f_hc} {f_k} {f_d_str} {f_l}")
            global_recent_moves.append(((f_hr, f_hc), (f_tr, f_tc)))

            moving = stacks[f_hr][f_hc][f_k:]
            stacks[f_hr][f_hc] = stacks[f_hr][f_hc][:f_k]
            stacks[f_tr][f_tc].extend(reversed(moving))

            if is_nest[f_tr][f_tc] is not None:
                nc = is_nest[f_tr][f_tc]
                while stacks[f_tr][f_tc] and stacks[f_tr][f_tc][-1] == nc:
                    stacks[f_tr][f_tc].pop()

            if is_nest[f_hr][f_hc] is not None:
                nc = is_nest[f_hr][f_hc]
                while stacks[f_hr][f_hc] and stacks[f_hr][f_hc][-1] == nc:
                    stacks[f_hr][f_hc].pop()

            update_cell(f_hr, f_hc)
            update_cell(f_tr, f_tc)

            # 盤面の配置が変化したため、全スタック状態を解除して再挑戦
            stuck_slimes.clear()
            skipped_slimes.clear()
            height8_pending.clear()
            continue

        # =====================================================================
        # [SECTION 6-1: 汎用分割・踏み台ブースト合流探索 (クールダウン連動)]
        # =====================================================================
        cur_r, cur_c = best_slime
        color = stacks[cur_r][cur_c][-1]
        goal_nest_r, goal_nest_c = nest_pos[color]
        step_limit = N * N
        moved_any = False

        recent_visited = deque(maxlen=6)
        recent_visited.append((cur_r, cur_c))
        start_nest_dist = dist[color][cur_r][cur_c]

        h_cur = len(stacks[cur_r][cur_c])
        same_count = sum(1 for v in reversed(stacks[cur_r][cur_c]) if v == color)
        base_k = h_cur - same_count
        base_max_l = base_k + 1

        j_direct = get_jump_dist((goal_nest_r, goal_nest_c), base_max_l)
        cost_direct = j_direct[cur_r][cur_c]

        best_combo = None
        min_combo_cost = cost_direct

        # 高さ5以上、直行3手以上、かつクールダウン中でない場合のみ分割・踏み台コンボを検討
        in_cooldown = (cur_ans_len < combo_cooldown.get((cur_r, cur_c), 0))
        if h_cur >= 5 and cost_direct >= 3 and not in_cooldown:
            for split_k in range(1, h_cur):
                m_fly = h_cur - split_k
                max_l_split = split_k + 1

                for d_str, dr, dc in DIRECTIONS:
                    for l_val in range(1, max_l_split + 1):
                        tr = cur_r + dr * l_val
                        tc = cur_c + dc * l_val

                        if not (0 <= tr < N and 0 <= tc < N):
                            break
                        if is_wall[tr][tc]:
                            break
                        if len(stacks[tr][tc]) + m_fly > 8:
                            continue

                        new_h_tr = len(stacks[tr][tc]) + m_fly
                        top_sc = m_fly if len(stacks[tr][tc]) == 0 else sum(1 for v in reversed(stacks[tr][tc] + [color]*m_fly) if v == color)
                        top_max_l = max(1, new_h_tr - top_sc + 1)
                        cost_top_goal = get_jump_dist((goal_nest_r, goal_nest_c), top_max_l)[tr][tc]
                        if cost_top_goal >= INF:
                            continue

                        for sr in range(max(0, cur_r - 2), min(N, cur_r + 3)):
                            for sc in range(max(0, cur_c - 2), min(N, cur_c + 3)):
                                if (sr, sc) == (cur_r, cur_c) or (sr, sc) == (tr, tc) or is_wall[sr][sc]:
                                    continue
                                h_step = len(stacks[sr][sc])
                                if 1 <= h_step < 8:
                                    cap = 8 - h_step
                                    send_cnt = min(split_k, cap)
                                    rem_k = split_k - send_cnt
                                    step_max_l = rem_k + 1

                                    dr_s = sr - cur_r
                                    dc_s = sc - cur_c
                                    step1_dir = None
                                    step1_len = 0
                                    if dr_s == 0 and 1 <= abs(dc_s) <= step_max_l:
                                        s_dir_str = 'R' if dc_s > 0 else 'L'
                                        sgn = 1 if dc_s > 0 else -1
                                        if all(not is_wall[cur_r][cur_c + sgn * step] for step in range(1, abs(dc_s) + 1)):
                                            step1_dir = s_dir_str
                                            step1_len = abs(dc_s)
                                    elif dc_s == 0 and 1 <= abs(dr_s) <= step_max_l:
                                        s_dir_str = 'D' if dr_s > 0 else 'U'
                                        sgn = 1 if dr_s > 0 else -1
                                        if all(not is_wall[cur_r + sgn * step][cur_c] for step in range(1, abs(dr_s) + 1)):
                                            step1_dir = s_dir_str
                                            step1_len = abs(dr_s)

                                    if step1_dir is not None:
                                        boosted_h = h_step + send_cnt
                                        b_k = h_step
                                        b_max_l = b_k + 1
                                        
                                        dr_t = tr - sr
                                        dc_t = tc - sc
                                        step2_dir = None
                                        step2_len = 0
                                        if dr_t == 0 and 1 <= abs(dc_t) <= b_max_l:
                                            s2_dir_str = 'R' if dc_t > 0 else 'L'
                                            sgn2 = 1 if dc_t > 0 else -1
                                            if all(not is_wall[sr][sc + sgn2 * step] for step in range(1, abs(dc_t) + 1)):
                                                step2_dir = s2_dir_str
                                                step2_len = abs(dc_t)
                                        elif dc_t == 0 and 1 <= abs(dr_t) <= b_max_l:
                                            s2_dir_str = 'D' if dr_t > 0 else 'U'
                                            sgn2 = 1 if dr_t > 0 else -1
                                            if all(not is_wall[sr + sgn2 * step][sc] for step in range(1, abs(dr_t) + 1)):
                                                step2_dir = s2_dir_str
                                                step2_len = abs(dr_t)

                                        if step2_dir is not None and (new_h_tr + send_cnt <= 8):
                                            merged_h = new_h_tr + send_cnt
                                            merged_sc = top_sc + send_cnt
                                            merged_max_l = max(1, merged_h - merged_sc + 1)
                                            ops_after_merge = get_jump_dist((goal_nest_r, goal_nest_c), merged_max_l)[tr][tc]

                                            if ops_after_merge < INF:
                                                total_combo_cost = 3 + ops_after_merge
                                                if total_combo_cost < min_combo_cost:
                                                    min_combo_cost = total_combo_cost
                                                    best_combo = (
                                                        (cur_r, cur_c, split_k, d_str, l_val, tr, tc),
                                                        (cur_r, cur_c, rem_k, step1_dir, step1_len, sr, sc, send_cnt),
                                                        (sr, sc, b_k, step2_dir, step2_len, tr, tc, send_cnt)
                                                    )

        if best_combo is not None:
            act1, act2, act3 = best_combo
            # クールダウンの設定（15手以内は同マスでコンボを再発動しない）
            combo_cooldown[(cur_r, cur_c)] = len(ans) + 15
            combo_cooldown[(act1[5], act1[6])] = len(ans) + 15

            # 手順1: 上部射出
            c1_r, c1_c, k1, d1, l1, t1_r, t1_c = act1
            ans.append(f"{c1_r} {c1_c} {k1} {d1} {l1}")
            global_recent_moves.append(((c1_r, c1_c), (t1_r, t1_c)))
            mov1 = stacks[c1_r][c1_c][k1:]
            stacks[c1_r][c1_c] = stacks[c1_r][c1_c][:k1]
            stacks[t1_r][t1_c].extend(reversed(mov1))
            if is_nest[t1_r][t1_c] is not None:
                nc = is_nest[t1_r][t1_c]
                while stacks[t1_r][t1_c] and stacks[t1_r][t1_c][-1] == nc:
                    stacks[t1_r][t1_c].pop()
            update_cell(c1_r, c1_c)
            update_cell(t1_r, t1_c)

            # 手順2: 下部が踏み台へ
            c2_r, c2_c, k2, d2, l2, t2_r, t2_c, _ = act2
            ans.append(f"{c2_r} {c2_c} {k2} {d2} {l2}")
            global_recent_moves.append(((c2_r, c2_c), (t2_r, t2_c)))
            mov2 = stacks[c2_r][c2_c][k2:]
            stacks[c2_r][c2_c] = stacks[c2_r][c2_c][:k2]
            stacks[t2_r][t2_c].extend(reversed(mov2))
            update_cell(c2_r, c2_c)
            update_cell(t2_r, t2_c)

            # 手順3: 踏み台から目標地点へ合流
            c3_r, c3_c, k3, d3, l3, t3_r, t3_c, _ = act3
            ans.append(f"{c3_r} {c3_c} {k3} {d3} {l3}")
            global_recent_moves.append(((c3_r, c3_c), (t3_r, t3_c)))
            mov3 = stacks[c3_r][c3_c][k3:]
            stacks[c3_r][c3_c] = stacks[c3_r][c3_c][:k3]
            stacks[t3_r][t3_c].extend(reversed(mov3))
            if is_nest[t3_r][t3_c] is not None:
                nc = is_nest[t3_r][t3_c]
                while stacks[t3_r][t3_c] and stacks[t3_r][t3_c][-1] == nc:
                    stacks[t3_r][t3_c].pop()
            update_cell(c3_r, c3_c)
            update_cell(t3_r, t3_c)

            stuck_slimes.clear()
            skipped_slimes.clear()
            moved_any = True

            if (t3_r, t3_c) != (goal_nest_r, goal_nest_c) and stacks[t3_r][t3_c]:
                cur_r, cur_c = t3_r, t3_c
                recent_visited.append((cur_r, cur_c))
                is_height_8 = (len(stacks[t3_r][t3_c]) == 8)
            else:
                continue

        # =====================================================================
        # [SECTION 6-2: 単一スライムの移動先候補選定関数 (通常移動時)]
        # =====================================================================
        while len(ans) < MAX_OPS and step_limit > 0:
            step_limit -= 1
            if (cur_r, cur_c) == (goal_nest_r, goal_nest_c):
                break

            h = len(stacks[cur_r][cur_c])
            if h == 0:
                break

            same_count = 0
            for val in reversed(stacks[cur_r][cur_c]):
                if val == color:
                    same_count += 1
                else:
                    break

            m = same_count
            k = h - m
            max_l = k + 1

            best_move = None
            is_staged_merge = False
            stage_target_pos = None

            def find_best_move_for(target_coord, is_pick: bool):
                j_dist = get_jump_dist(target_coord, max_l)
                t_d_map = get_dist_map(target_coord)
                cur_ops = j_dist[cur_r][cur_c]
                if cur_ops >= INF:
                    return None

                best_m = None
                best_pri = (-INF, -INF, -INF, -INF)

                for d_str, dr, dc in DIRECTIONS:
                    for l in range(1, max_l + 1):
                        tr = cur_r + dr * l
                        tc = cur_c + dc * l

                        if not (0 <= tr < N and 0 <= tc < N):
                            break
                        if is_wall[tr][tc]:
                            break
                        if len(stacks[tr][tc]) + m > 8:
                            continue

                        # 巣に入る手は常に許可
                        is_to_goal = ((tr, tc) == (goal_nest_r, goal_nest_c))

                        # 局所履歴および大域履歴での往復・ピンポン排除
                        if not is_to_goal:
                            if (tr, tc) in recent_visited:
                                continue
                            if ((cur_r, cur_c), (tr, tc)) in global_recent_moves or ((tr, tc), (cur_r, cur_c)) in global_recent_moves:
                                continue

                        # 目的地（巣、または寄り道合流相手）への手数が真に減る「真の前進」のみを厳格に選定
                        cand_ops = j_dist[tr][tc]
                        if cand_ops >= cur_ops:
                            continue

                        bonus = 100000 if (tr, tc) == target_coord else 0
                        cand_real_d = t_d_map[tr][tc]

                        pri = (bonus, -cand_ops, -cand_real_d, -l)
                        if pri > best_pri:
                            best_pri = pri
                            best_m = (cur_r, cur_c, k, d_str, l, tr, tc, m)

                        if (tr, tc) == target_coord:
                            break

                return best_m

            # =================================================================
            # [SECTION 6-3: 最適合流スライムの比較選定 (直接合流 / 分割積載)]
            # =================================================================
            if not is_height_8:
                j_dist_goal = get_jump_dist((goal_nest_r, goal_nest_c), max_l)
                ops_to_goal = j_dist_goal[cur_r][cur_c]
                cur_d_map = get_dist_map((cur_r, cur_c))

                best_choice = None
                best_overall_benefit = 0

                if ops_to_goal > 1:
                    for nr, nc in slimes_by_color[color]:
                        if (nr, nc) == (cur_r, cur_c) or (nr, nc) == (goal_nest_r, goal_nest_c) or (nr, nc) in recent_visited:
                            continue
                        if ((cur_r, cur_c), (nr, nc)) in global_recent_moves or ((nr, nc), (cur_r, cur_c)) in global_recent_moves:
                            continue

                        h_target = len(stacks[nr][nc])
                        if h_target >= 8:
                            continue

                        d_val = cur_d_map[nr][nc]
                        if d_val > PHASE2_MAX_MERGE_DIST:
                            continue

                        partner_max_l = max(1, h_target)
                        partner_saved_ops = get_jump_dist((goal_nest_r, goal_nest_c), partner_max_l)[nr][nc]
                        if partner_saved_ops >= INF:
                            partner_saved_ops = 2

                        # パターン1: 合計高さ <= 8 (直接合流)
                        if h_target + m <= 8:
                            j_dist_t = get_jump_dist((nr, nc), max_l)
                            cost_detour = j_dist_t[cur_r][cur_c]
                            if cost_detour >= INF:
                                continue

                            new_h = h_target + m
                            new_max_l = max(max_l, new_h - 1 + 1)
                            ops_from_merge = get_jump_dist((goal_nest_r, goal_nest_c), new_max_l)[nr][nc]
                            if ops_from_merge >= INF:
                                continue

                            jump_gain = new_max_l - max_l
                            is_worthwhile = (
                                (jump_gain >= cost_detour) or
                                (cost_detour + ops_from_merge <= ops_to_goal) or
                                (cost_detour + ops_from_merge < ops_to_goal + partner_saved_ops)
                            )
                            if is_worthwhile:
                                net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + ops_from_merge) + jump_gain
                                if net_benefit > best_overall_benefit:
                                    test_m = find_best_move_for((nr, nc), is_pick=True)
                                    if test_m is not None:
                                        best_overall_benefit = net_benefit
                                        best_choice = ('direct', (nr, nc), test_m)

                        # パターン2: 合計高さ >= 9 (隣接マスからの分割積載)
                        else:
                            best_adj = None
                            min_adj_cost = INF
                            for _, adr, adc in DIRECTIONS:
                                ar, ac = nr + adr, nc + adc
                                if 0 <= ar < N and 0 <= ac < N and not is_wall[ar][ac]:
                                    if len(stacks[ar][ac]) + m <= 8:
                                        j_adj = get_jump_dist((ar, ac), max_l)
                                        c_adj = j_adj[cur_r][cur_c]
                                        if c_adj < min_adj_cost:
                                            min_adj_cost = c_adj
                                            best_adj = (ar, ac)

                            if best_adj is not None and min_adj_cost < INF:
                                cost_detour = min_adj_cost + 1
                                max_send = 8 - h_target
                                rem = m - max_send

                                ops_target_8 = get_jump_dist((goal_nest_r, goal_nest_c), 8)[nr][nc]
                                ops_rem = get_jump_dist((goal_nest_r, goal_nest_c), max(1, rem))[best_adj[0]][best_adj[1]]

                                if ops_target_8 < INF and ops_rem < INF:
                                    total_after = ops_target_8 + ops_rem
                                    net_benefit = (ops_to_goal + partner_saved_ops) - (cost_detour + total_after) + (8 - max_l)
                                    if net_benefit > best_overall_benefit:
                                        test_m = find_best_move_for(best_adj, is_pick=True)
                                        if test_m is not None:
                                            best_overall_benefit = net_benefit
                                            best_choice = ('staged', best_adj, (nr, nc), test_m)

                if best_choice is not None:
                    if best_choice[0] == 'direct':
                        best_move = best_choice[2]
                    elif best_choice[0] == 'staged':
                        best_move = best_choice[3]
                        is_staged_merge = True
                        stage_target_pos = best_choice[2]

            # =================================================================
            # [SECTION 6-4: 高さ8の直行ルーティング / 通常時の目標決定]
            # =================================================================
            if is_height_8:
                c_dist = dist[color][cur_r][cur_c]
                if c_dist < INF:
                    best_pri = (-INF, -INF, -INF)
                    for d_str, dr, dc in DIRECTIONS:
                        for l in range(1, max_l + 1):
                            tr = cur_r + dr * l
                            tc = cur_c + dc * l

                            if not (0 <= tr < N and 0 <= tc < N):
                                break
                            if is_wall[tr][tc]:
                                break
                            if len(stacks[tr][tc]) + m > 8:
                                continue
                            
                            is_to_goal = ((tr, tc) == (goal_nest_r, goal_nest_c))
                            if not is_to_goal:
                                if (tr, tc) in recent_visited:
                                    continue
                                if ((cur_r, cur_c), (tr, tc)) in global_recent_moves or ((tr, tc), (cur_r, cur_c)) in global_recent_moves:
                                    continue

                            cand_d = dist[color][tr][tc]
                            if cand_d >= c_dist:
                                continue

                            delta_d = c_dist - cand_d
                            pri = (delta_d, -cand_d, -l)
                            if pri > best_pri:
                                best_pri = pri
                                best_move = (cur_r, cur_c, k, d_str, l, tr, tc, m)

                            if is_to_goal:
                                break

                if best_move is None:
                    height8_pending[(cur_r, cur_c)] = len(ans) + 10
                    break
            else:
                if best_move is None:
                    best_move = find_best_move_for((goal_nest_r, goal_nest_c), is_pick=False)

                if best_move is None:
                    break

            # =================================================================
            # [SECTION 6-5: ジャンプ実行と盤面・巣の更新]
            # =================================================================
            _, _, k_val, d_str, l_val, tr, tc, m_val = best_move

            is_merging = ((tr, tc) != (goal_nest_r, goal_nest_c)) and bool(stacks[tr][tc] and stacks[tr][tc][-1] == color)

            ans.append(f"{cur_r} {cur_c} {k_val} {d_str} {l_val}")
            global_recent_moves.append(((cur_r, cur_c), (tr, tc)))
            moved_any = True
            recent_visited.append((cur_r, cur_c))

            moving = stacks[cur_r][cur_c][k_val:]
            stacks[cur_r][cur_c] = stacks[cur_r][cur_c][:k_val]
            stacks[tr][tc].extend(reversed(moving))

            if is_nest[tr][tc] is not None:
                nc = is_nest[tr][tc]
                while stacks[tr][tc] and stacks[tr][tc][-1] == nc:
                    stacks[tr][tc].pop()

            if is_nest[cur_r][cur_c] is not None:
                nc = is_nest[cur_r][cur_c]
                while stacks[cur_r][cur_c] and stacks[cur_r][cur_c][-1] == nc:
                    stacks[cur_r][cur_c].pop()

            update_cell(cur_r, cur_c)
            update_cell(tr, tc)

            # =================================================================
            # [SECTION 6-6: 隣接マスからの分割積載実行とループ状態更新]
            # =================================================================
            if is_staged_merge and (tr, tc) == best_choice[1]:
                tnr, tnc = stage_target_pos
                h_tgt = len(stacks[tnr][tnc])
                if h_tgt < 8 and len(stacks[tr][tc]) > 0:
                    max_send = min(8 - h_tgt, len(stacks[tr][tc]))
                    k_send = len(stacks[tr][tc]) - max_send

                    s_d_str = None
                    for cd_str, cdr, cdc in DIRECTIONS:
                        if tr + cdr == tnr and tc + cdc == tnc:
                            s_d_str = cd_str
                            break

                    if s_d_str is not None:
                        ans.append(f"{tr} {tc} {k_send} {s_d_str} 1")
                        global_recent_moves.append(((tr, tc), (tnr, tnc)))
                        st_moving = stacks[tr][tc][k_send:]
                        stacks[tr][tc] = stacks[tr][tc][:k_send]
                        stacks[tnr][tnc].extend(reversed(st_moving))

                        if is_nest[tnr][tnc] is not None:
                            nc = is_nest[tnr][tnc]
                            while stacks[tnr][tnc] and stacks[tnr][tnc][-1] == nc:
                                stacks[tnr][tnc].pop()

                        if is_nest[tr][tc] is not None:
                            nc = is_nest[tr][tc]
                            while stacks[tr][tc] and stacks[tr][tc][-1] == nc:
                                stacks[tr][tc].pop()

                        update_cell(tr, tc)
                        update_cell(tnr, tnc)
                        is_merging = True

            if (tr, tc) == (goal_nest_r, goal_nest_c):
                cur_r, cur_c = tr, tc
                break

            cur_r, cur_c = tr, tc

            # 合流が成立した場合は一旦終了し、より高くなった塔として再評価・最優先運搬
            if is_merging:
                break

        # 運搬終了後の更新
        if moved_any:
            # 合流が成立した場合は大成功（進捗あり）として絶対にスキップしない
            if is_merging:
                stuck_slimes.clear()
                skipped_slimes.clear()
            else:
                end_nest_dist = dist[color][cur_r][cur_c] if stacks[cur_r][cur_c] else 0
                # 単独移動で距離が縮まらなかった場合のみスキップ登録
                if end_nest_dist >= start_nest_dist:
                    skipped_slimes.add((cur_r, cur_c))
                else:
                    stuck_slimes.clear()
                    skipped_slimes.clear()
        else:
            stuck_slimes.add((cur_r, cur_c))

    # =========================================================================
    # [SECTION 7-1: 解の出力]
    # =========================================================================
    print(*ans, sep="\n")





















if __name__ == "__main__":
    main()
