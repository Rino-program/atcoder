# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
from os import path
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
    H, W = MAP()
    S = STRS(H)
    start = (0, 0)
    idx_char = ["D", "R", "U", "L"]
    for i in range(H):
        for j in range(W):
            if S[i][j] == "S":
                start = (i, j)
            elif S[i][j] == "G":
                gorl = (i, j)

    def enc(x, y, d):  # d は -1〜3、+1して0〜4
        return (x * W + y) * 5 + (d + 1)

    N = H * W * 5
    visited = bytearray(N)          # ★ ネストリストよりはるかに高速
    prev_state = [-1] * N           # ★ 辞書→配列
    prev_move  = [-1] * N           # ★ 辞書→配列

    s0 = enc(start[0], start[1], -1)
    visited[s0] = 1
    q = deque([s0])

    while q:
        state = q.popleft()
        d1   = state % 5
        xy   = state // 5
        x, y = xy // W, xy % W
        last_dir = d1 - 1           # -1〜3 に戻す

        if S[x][y] == "G":
            path = []
            cur = state
            while prev_state[cur] != -1:
                path.append(idx_char[prev_move[cur]])
                cur = prev_state[cur]
            path.reverse()
            Yes()
            print("".join(path))
            return

        cell = S[x][y]
        for i, (dx, dy) in enumerate(DIR4):
            if cell == "o" and i != last_dir:
                continue
            if cell == "x" and i == last_dir:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < H and 0 <= ny < W and S[nx][ny] != "#":
                ns = enc(nx, ny, i)
                if not visited[ns]:
                    visited[ns] = 1
                    prev_state[ns] = state
                    prev_move[ns]  = i
                    q.append(ns)
    No()





















if __name__ == "__main__":
    main()