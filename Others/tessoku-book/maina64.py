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

def build_weighted_graph(n: int, edges: list[tuple[int, int, int]], directed: bool = False) -> list[list[tuple[int, int]]]:
    """概要:
        辺集合から重み付きグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (a, b, cost) の配列。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[tuple[int, int]]]: 隣接リスト（要素は (to, cost)）。
    補足:
        無向時は両方向に辺を追加する。
    """
    g = [[] for _ in range(n)]
    for a, b, c in edges:
        g[a].append((b, c))
        if not directed:
            g[b].append((a, c))
    return g

def dijkstra_path(g: list[list[tuple[int, int]]], s: int, t: int) -> tuple[int, list[int] | None]:
    """概要:
        非負重みグラフで s から t への最短距離と経路を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト（要素は (to, cost)）。
        s (int): 始点。
        t (int): 終点。
    出力:
        tuple[int, list[int] | None]:
            (最短距離, s から t への頂点列)。
            到達不能なら (INF, None)。
    補足:
        計算量は O((V+E)logV)。負辺は非対応。
        経路が複数ある場合は最短の1つを返す。
    """
    n = len(g)
    dist = [INF] * n
    parent = [-1] * n
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]:
            continue
        for to, w in g[v]:
            if dist[v] + w < dist[to]:
                dist[to] = dist[v] + w
                parent[to] = v
                heapq.heappush(pq, (dist[to], to))

    if dist[t] == INF:
        return INF, None

    path = []
    v = t
    while v != -1:
        path.append(v)
        v = parent[v]
    path.reverse()
    return dist[t], path

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    ABC = LISTS(M)
    g = build_weighted_graph(N, [(a-1, b-1, c) for a, b, c in ABC], directed=False)
    ans = dijkstra_path(g, 0, N - 1)[1]
    for i in range(len(ans)):
        ans[i] += 1
    print(*ans, sep=' ')





















if __name__ == "__main__":
    main()