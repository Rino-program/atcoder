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

# ===== 変数 =====
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

def prefix_sum_3d(A: list[list[list[int]]], N: int) -> list[list[list[int]]]:
    """概要:
        3次元配列の累積和テーブルを構築する。
    入力:
        A (list[list[list[int]]]): 1-indexed の数値グリッド A[1..N][1..N][1..N]。
                                   インデックス 0 はダミー（0 で埋める）。
        N (int): 各次元の大きさ（1-indexed）。
    出力:
        list[list[list[int]]]: (N+2)^3 サイズの3次元累積和テーブル（1-indexed）。
    補足:
        構築計算量は O(N^3)。
        矩形和は range_sum_3d で O(1) 取得できる。
    使用例:
        P = prefix_sum_3d(A, N)
        s = range_sum_3d(P, lx, ly, lz, rx, ry, rz)
    """
    P = [[[0] * (N + 2) for _ in range(N + 2)] for _ in range(N + 2)]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for z in range(1, N + 1):
                P[x][y][z] = A[x][y][z]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for z in range(1, N + 1):
                P[x][y][z] += P[x-1][y][z]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for z in range(1, N + 1):
                P[x][y][z] += P[x][y-1][z]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            for z in range(1, N + 1):
                P[x][y][z] += P[x][y][z-1]
    return P

def range_sum_3d(
    P: list[list[list[int]]],
    lx: int, ly: int, lz: int,
    rx: int, ry: int, rz: int,
) -> int:
    """概要:
        3次元累積和から直方体 [lx,rx]×[ly,ry]×[lz,rz] の総和を返す（閉区間・1-indexed）。
    入力:
        P (list[list[list[int]]]): prefix_sum_3d の戻り値。
        lx, ly, lz, rx, ry, rz (int): 閉区間の境界（1-indexed）。
    出力:
        int: 指定直方体の総和。
    補足:
        3次元包除原理（8項）を用いる。計算量は O(1)。
    """
    x0, y0, z0 = lx - 1, ly - 1, lz - 1
    return (
        P[rx][ry][rz]
        - P[x0][ry][rz] - P[rx][y0][rz] - P[rx][ry][z0]
        + P[x0][y0][rz] + P[x0][ry][z0] + P[rx][y0][z0]
        - P[x0][y0][z0]
    )

def main() -> None:
    # ここに解答を書く
    N = INT()
    A = [[[0] * (N + 1) for _ in range(N + 1)] for _ in range(N + 1)]
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            row = LIST()
            for z in range(1, N + 1):
                A[x][y][z] = row[z - 1]
    P = prefix_sum_3d(A, N)
    Q = INT()
    ans = []
    for _ in range(Q):
        lx, rx, ly, ry, lz, rz = MAP()
        s = range_sum_3d(P, lx, ly, lz, rx, ry, rz)
        ans.append(s)
    print(*ans, sep='\n')





















if __name__ == "__main__":
    main()