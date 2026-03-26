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

def build_weighted_graph(n: int, edges: list[tuple[int, int, int]], idx: int = True, directed: bool = False) -> list[list[tuple[int, int]]]:
    """概要:
        辺集合から重み付きグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (a, b, cost) の配列。
        idx (bool): True なら頂点番号を0-indexedに調整する。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[tuple[int, int]]]: 隣接リスト（要素は (to, cost)）。
    補足:
        無向時は両方向に辺を追加する。計算量は O(n + m)（m は辺数）。
    """
    g = [[] for _ in range(n)]
    for a, b, c in edges:
        if idx:
            a -= 1
            b -= 1
        g[a].append((b, c))
        if not directed:
            g[b].append((a, c))
    return g

def dijkstra(g: list[list[tuple[int, int]]], s: int) -> list[int]:
    """概要:
        非負重みグラフで始点 s からの最短距離を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト。
        s (int): 始点。
    出力:
        list[int]: 各頂点への最短距離（未到達は INF）。
    補足:
        計算量は O((V+E)logV)。負辺は非対応。
    """
    dist = [INF] * len(g)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]: continue
        for to, w in g[v]:
            if dist[v] + w < dist[to]:
                dist[to] = dist[v] + w
                heapq.heappush(pq, (dist[to], to))
    return dist

def main() -> None:
    # ここに解答を書く
    N, M, K = MAP()
    edges = TUPLES(M)
    g = build_weighted_graph(N, edges)
    dist = dijkstra(g, 0)
    print(dist[-1] if dist[-1] <= K else -1)





















if __name__ == "__main__":
    main()