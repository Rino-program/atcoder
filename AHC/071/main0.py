# AtCoder Competition Template v2.2.2 SHORT (PyPy 7.3.20 / Python 3.11)
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
MAP0 = lambda: map(lambda x: int(x) - 1, input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: list(map(lambda x: int(x) - 1, input().split()))
TUPLE = lambda: tuple(map(int, input().split()))
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

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
Yes = lambda: print("Yes")
No = lambda: print("No")
yes = lambda: print("yes")
no = lambda: print("no")
YES = lambda: print("YES")
NO = lambda: print("NO")
def yn(cond: bool, yes: str = "Yes", no: str = "No") -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no)

# ===== デバッグ =====
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, **kwargs) -> None:
        """デバッグ出力（標準エラー）"""
        print("[DEBUG]", *args, **kwargs, file=sys.stderr)
else:
    def debug(*args, **kwargs) -> None:
        pass

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))

# ===== template.py =====
def rotate_90(grid: list[list]) -> list[list]:
    """概要:
        2次元配列を時計回りに90度回転して返す。
    入力:
        grid (list[list]): 元グリッド。
    出力:
        list[list]: 回転後グリッド。
    補足:
        計算量は O(HW)。
    """
    H, W = len(grid), len(grid[0])
    return [[grid[H - 1 - j][i] for j in range(H)] for i in range(W)]
# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    W, H, K = MAP()
    c1, c3, c5, c7, c9 = MAP()
    # 穴あき記録
    f = [-1 for i in range(W)]
    dot = [[0 for _ in range(W)] for _ in range(H)]
    for i in range(K):
        A, B = MAP()
        f[A] = max(B, f[A])
        dot[B][A] = 1
    # 最高点をマーク
    ans = []
    for i, h in en(f):
        for j in range(h+1):
            ans.append((i, j, 1))
    ans_set = set(ans)
    Map = [[0 for _ in range(H)] for _ in range(W)]
    for i, j, k in ans:
        Map[i][j] = 1
    # 右回転
    Map = rotate_90(Map)
    # 左右反転
    Map = [row[::-1] for row in Map]
    #print_grid(Map)
    # 1つを3つにまとめる
    """ans_now = []
    i = 0
    j = 0
    while i < H:
        while j < W:
            if j < W-2 and Map[i][j] == 1 and Map[i][j+1] == 1 and Map[i][j+2] == 1:
                ans_now.append((j, i, 3))
                j += 3
            elif j < W-2 and Map[i][j+1] == 1 and (Map[i][j] == 1):
                ans_now.append((j, i, 3))
                j += 3
            else:
                if Map[i][j] == 1:
                    ans_now.append((j, i, 1))
                j += 1
        i += 1
        j = 0"""
    ans_now = ans[:]
    # 3でなくてもいい所を1にする
    ans = []
    Map = [[0 for _ in range(W)] for _ in range(H)]
    for i, j, k in ans_now:
        if k == 1:
            ans.append((i, j, 1))
        else:
            Map[j][i] = 1
    #print_grid(Map)
    i = 0
    j = 0
    while i < H-1:
        while j < W-1:
            if Map[i][j] == 1 and Map[i+1][j] == 1 and dot[i][j] == 0 and dot[i][j+2] == 0:
                Map[i][j] = 0
                ans.append((j+1, i, 1))
            if Map[i][j] == 1:
                j += 1
            j += 1
        i += 1
        j = 0
    for i in range(H):
        for j in range(W):
            if Map[i][j] == 1:
                ans.append((j, i, 3))
    ans_now = ans[:]
    ans = []
    Map = [[0 for _ in range(W)] for _ in range(H)]
    for i, j, k in ans_now:
        if k == 1: Map[j][i] = 1
        else:
            Map[j][i] = 3
            Map[j][i+1] = INF
            Map[j][i+2] = INF
    Map = Map[::-1]
    #print_grid(Map)
    # 必要のない1を消す
    # 床についてる物について
    d = deque()
    for i in range(W):
        if Map[H-1][i] == 1:
            d.append((H-1, i))
    while d:
        y, x = d.popleft()
        if y == 0:
            if dot[H-1-y][x] == 0:
                while y < H and Map[y][x] == 1 and dot[H-1-y][x] == 0:
                    Map[y][x] = 0
                    y += 1
            continue
        if Map[y-1][x] in {1, 100}:
            d.append((y-1, x))
        else:
            if dot[H-1-y][x] == 0:
                while y < H and Map[y][x] == 1 and dot[H-1-y][x] == 0:
                    Map[y][x] = 0
                    y += 1
    del d
    # 長いやつを設置してまとめる
    """# まずは3つのやつに何個乗ってるかを調べる
    Map3 = [[0 for _ in range(W)] for _ in range(H)]
    for i in range(H):
        for j in range(W):
            if Map[i][j] == 3:
                tmp = 0
                for k in range(3):
                    if Map[i][j+k] in {3, 4}:
                        tmp += 1
                        break
                    if Map[i][j+k] == 1:
                        tmp += 1
                Map3[i][j] = tmp
                Map3[i][j+1] = tmp
                Map3[i][j+2] = tmp"""
    #print_grid(Map)
    # 15 と 45 に寄るような走査順を作成
    # (0->14, 29->15, 30->44, 59->45 の順に内側へ寄せていく)
    b_order = []
    b_order += list(range(0, 15))
    b_order += list(range(29, 14, -1))
    b_order += list(range(30, 45))
    b_order += list(range(59, 44, -1))

    line = [i for i in range(1, H)][::-1]
    for l in line:
        for b in b_order:
            z = b
            f = 0
            tmp = 0
            left = INF
            right = -1
            ma = 0
            for j in range(9):
                pos = j + z
                if pos >= W: break
                if Map[H-1-l][pos] not in {0, 1}:
                    f = 1
                if Map[H-1-l][pos] == 1:
                    tmp += 1
                    left = min(left, pos)
                    right = max(right, pos)
                ma = max(ma, pos)

            # 奇数長に調整するとき、近い方の目標(15 or 45)に center が近づく側へ伸ばす
            if right != -1 and left != INF and ((right - left + 1) % 2 == 0):
                cur_center = (left + right) / 2
                target = 15 if cur_center < 30 else 45
                
                # target より左なら右へ伸ばし、target より右なら左へ伸ばす
                if cur_center < target:
                    if right + 1 < W and Map[H-1-l][right + 1] in {0, 1}:
                        right += 1
                    elif left - 1 >= 0 and Map[H-1-l][left - 1] in {0, 1}:
                        left -= 1
                    else:
                        f = 1
                else:
                    if left - 1 >= 0 and Map[H-1-l][left - 1] in {0, 1}:
                        left -= 1
                    elif right + 1 < W and Map[H-1-l][right + 1] in {0, 1}:
                        right += 1
                    else:
                        f = 1

            if f == 0 and tmp > 1:
                # 削除と設置
                for col in range(left, right + 1):
                    Map[H-1-l][col] = INF
                Map[H-1-l][left] = right - left + 1

                # 下側についてる1の削除・柱の追加
                center = (left + right) // 2  # 中央の座標
                for col in range(left, right + 1):
                    if col == center:
                        x, y = col, H-1-(l-1)
                        while y < H and Map[y][x] == 0:
                            Map[y][x] = 1
                            y += 1
                        continue

                    if Map[H-1-(l-1)][col] == 1:
                        x, y = col, H-1-(l-1)
                        while y < H and Map[y][x] == 1 and dot[H-1-y][x] == 0:
                            Map[y][x] = 0
                            y += 1
    Map = Map[::-1]
    ans = []
    for i in range(H):
        for j in range(W):
            if Map[i][j] not in {0, 100, INF}:
                ans.append((j, i, Map[i][j]))
    print(len(ans))
    for i in ans:
        print(*i)





















if __name__ == "__main__":
    main()
