# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from copy import deepcopy
import string

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin.readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def TUPLE() -> tuple[int, ...]:
    return tuple(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def TUPLES(n: int) -> list[tuple[int, ...]]:
    return [TUPLE() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> list[str]:
    return [STR() for _ in range(n)]

def CHARS() -> list[str]:
    return list(STR())

def CHARSL(n: int) -> list[list[str]]:
    return [list(STR()) for _ in range(n)]

# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIR9 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
pr = print # ただのさぼり。
def Yes(): print("Yes")
def No(): print("No")
def yes(): print("yes")
def no(): print("no")
def YES(): print("YES")
def NO(): print("NO")
def yn(cond: bool) -> None:
    """条件に応じてYes/No出力"""
    print("Yes" if cond else "No")

# ===== デバッグ =====
def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def prefix_sum(arr: list[int]) -> list[int]:
    """概要:
        1次元配列の累積和配列を構築する。
    入力:
        arr (list[int]): 元配列。
    出力:
        list[int]: 先頭に 0 を持つ累積和配列 ps。
    補足:
        区間和は ps[r] - ps[l]（半開区間 [l, r)）。計算量は O(n)。
    """
    ps = [0]
    for x in arr:
        ps.append(ps[-1] + x)
    return ps

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

def main() -> None:
    # ここに解答を書く
    H, W, K = MAP()
    S = CHARSL(H)
    Sx = [[1 if S[i][j] == "x" else 0 for j in range(W)] for i in range(H)]
    Sd = [[1 if S[i][j] == "." else 0 for j in range(W)] for i in range(H)]
    Shx = [prefix_sum(row) for row in Sx]
    Shd = [prefix_sum(row) for row in Sd]
    for _ in range(3):
        Sx = rotate_90(Sx)
        Sd = rotate_90(Sd)
    Swx = [prefix_sum(row) for row in Sx]
    Swd = [prefix_sum(row) for row in Sd]
    ans = INF
    for i in range(H):
        for j in range(1, W+2-K):
            if Shx[i][j+K-1] - Shx[i][j-1] == 0:
                ans = min(ans, Shd[i][j+K-1] - Shd[i][j-1])
    """print_grid(Swx, sep='_')
    debug("----")
    print_grid(Swd, sep='_')"""
    for i in range(W):
        for j in range(1, H+2-K):
            if Swx[i][j+K-1] - Swx[i][j-1] == 0:
                ans = min(ans, Swd[i][j+K-1] - Swd[i][j-1])
    print(ans if ans != INF else -1)





















if __name__ == "__main__":
    main()