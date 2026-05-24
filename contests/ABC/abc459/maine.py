# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
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

def topological_sort(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフをトポロジカルソートする。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: トポロジカル順序。閉路があれば None。
    補足:
        Kahn 法（入次数管理）を使用する。計算量は O(V+E)。
    """
    n = len(g)
    indeg = [0] * n
    for v in range(n):
        for to in g[v]:
            indeg[to] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    result = []
    while q:
        v = q.popleft()
        result.append(v)
        for to in g[v]:
            indeg[to] -= 1
            if indeg[to] == 0:
                q.append(to)
    return result if len(result) == n else None

def nCr(n, r, MOD=MOD):
    if n < r:
        return 0
    if n-r < r:
        r = n-r
    comb = 1
    for x in range(n-r+1, n+1):
        comb = (comb * x) % MOD
    d = 1
    for x in range(1, r+1):
        d = (d * x) % MOD
    comb *= pow(d, MOD-2, MOD)
    return comb % MOD

def main() -> None:
    # ここに解答を書く
    N = INT()
    P = LIST()
    C = LIST()
    D = LIST()
    g = [[] for i in range(N)]
    g1 = [0 for i in range(N)]
    for i, v in en(P, 1):
        g[i].append(v-1)
        g1[i] = v-1
    debug(g)
    """tree = tree_parent(g)
    #debug(tree)
    tree1 = tree_diameter(g)
    debug(tree1)"""
    T = topological_sort(g)
    debug(T)
    ans = []
    for t in T:
        C[t] -= D[t]
        if C[t] < 0:
            pr(0)
            return
        ans.append(nCr(C[t]+D[t], D[t]))
        C[g1[t]] += C[t]
    ans_num = 1
    for i in ans:
        ans_num *= i
        ans_num %= MOD
    pr(ans_num % MOD)




















if __name__ == "__main__":
    main()