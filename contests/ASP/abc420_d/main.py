# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from bisect import bisect_left, bisect_right
from copy import deepcopy
import operator
import heapq
import math
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

# ===== 関数短縮 =====
pr = print
en = enumerate
hepu = heapq.heappush
hepo = heapq.heappop
bil = bisect_left
bir = bisect_right
dedict = defaultdict

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIR9 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
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

def main() -> None:
    # ここに解答を書く
    H, W = MAP()
    A = CHARSL(H)
    for i in range(H):
        for j in range(W):
            if A[i][j] == 'S':
                s = (i, j)
                A[i][j] = "."
            elif A[i][j] == 'G':
                g = (i, j)
    #print_grid(A)
    d = deque()
    d.append((*s, 0, 0)) # (i, j, 回数, ドア)
    v = [[[1, 1] for _ in range(W)] for _ in range(H)]
    v[s[0]][s[1]][0] = 0
    while d:
        i, j, c, sz = d.popleft()
        if (i, j) == g:
            pr(c)
            return
        for x, y in DIR4:
            ni, nj = i+x, j+y
            if sz == 0:
                # 次元1
                if 0 <= ni < H and 0 <= nj < W:
                    if A[ni][nj] not in {"x", "#"}:
                        if A[ni][nj] == "?":
                            nsz = 1
                        else:
                            nsz = 0
                        if v[ni][nj][nsz]:
                            v[ni][nj][nsz] = 0
                            d.append((ni, nj, c+1, nsz))
            else:
                # 次元2
                if 0 <= ni < H and 0 <= nj < W:
                    if A[ni][nj] not in {"o", "#"}:
                        if A[ni][nj] == "?":
                            nsz = 0
                        else:
                            nsz = 1
                        if v[ni][nj][nsz]:
                            v[ni][nj][nsz] = 0
                            d.append((ni, nj, c+1, nsz))
    pr(-1)




















if __name__ == "__main__":
    main()