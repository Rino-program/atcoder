# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
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
    grid = CHARSL(H)
    ans = 0
    s = set()
    d = [(0, 0)]
    grid = [[0 if grid[i][j] == "." else int(grid[i][j]) for j in range(W)] for i in range(H)]
    ne = set()
    gridn = deepcopy(grid)
    for i in range(H):
        for j in range(W):
            for dx, dy in DIR8:
                nx, ny = i + dx, j + dy
                if 0 <= nx < H and 0 <= ny < W:
                    if grid[i][j] > 0 and grid[nx][ny] <= 0:
                        gridn[i][j] -= 1
                        gridn[i][j] = max(gridn[i][j], 0)
                        if gridn[i][j] == 0:
                            ne.add((i, j))
    #debug(ne)
    #print_grid(gridn)
    grid = gridn
    d = deque()
    for x, y in ne:
        d.append((x, y, 0))
    while d:
        ans += 1
        while d and d[-1][2] != ans:
            x, y, t = d.pop()
            for dx, dy in DIR8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < H and 0 <= ny < W:
                    if grid[nx][ny] > 0:
                        grid[nx][ny] -= 1
                        if grid[nx][ny] == 0:
                            d.appendleft((nx, ny, t + 1))
    print(ans)





















if __name__ == "__main__":
    main()
