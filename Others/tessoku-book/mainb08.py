# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
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
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> list[str]:
    return [STR() for _ in range(n)]

def CHARS() -> list[str]:
    return list(STR())

def STRSL(n: int) -> list[list[str]]:
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

def print_grid(grid:  list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def rotate_90(grid: list[list]) -> list[list]:
    """グリッドを時計回りに90度回転"""
    H, W = len(grid), len(grid[0])
    return [[grid[H - 1 - j][i] for j in range(H)] for i in range(W)]

def main() -> None:
    # ここに解答を書く
    N = INT()
    XY = LISTS(N)
    m = [[0 for i in range(1502)]]
    m += [[0 for i in range(1502)] for j in range(1501)]

    for x, y in XY:
        m[x][y] += 1

    M = []
    for i in m:
        tmp = []
        s = 0
        for j in i:
            tmp.append((s := s + j))
        M.append(tmp)

    Mn = [[0 for i in range(1502)] for j in range(1502)]
    for j in range(1502):
        s = 0
        for i in range(1502):
            s += M[i][j]
            Mn[i][j] = s

    """for i in range(7):
        tmp = []
        for j in range(7):
            tmp.append(Mn[i][j])
        print("_".join(map(str, tmp)))"""

    Q = INT()
    for i in range(Q):
        a, b, c, d = MAP()
        #debug(Mn[c][d], Mn[a-1][b-1], Mn[a-1][d-1], Mn[c][b-1])
        print(Mn[c][d]+Mn[a-1][b-1]-Mn[a-1][d]-Mn[c][b-1])





















if __name__ == "__main__":
    main()