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

def build_graph(n: int, edges: list[tuple[int, int]], idx: bool = True, directed: bool = False) -> list[list[int]]:
    """概要:
        辺集合から重みなしグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数（0-indexed を想定）。
        edges (list[tuple[int, int]]): 辺 (a, b) の配列。
        idx (bool): True なら頂点番号を0-indexedに調整する。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[int]]: 隣接リスト。
    補足:
        無向時は両方向に辺を追加する。計算量は O(n + m)（m は辺数）。
    """
    g = [[] for _ in range(n)]
    for a, b in edges:
        if idx:
            a -= 1
            b -= 1
        g[a]. append(b)
        if not directed:
            g[b].append(a)
    return g

def bfs(g: list[list[int]], s: int) -> list[int]:
    """概要:
        重みなしグラフで始点 s からの最短距離を BFS で求める。
    入力:
        g (list[list[int]]): 隣接リスト。
        s (int): 始点。
    出力:
        list[int]: 各頂点への距離。未到達は -1。
    補足:
        計算量は O(V+E)。
    """
    dist = [-1] * len(g)
    dist[s] = 0
    q = deque([s])
    while q:
        v = q.popleft()
        for to in g[v]:
            if dist[to] == -1:
                dist[to] = dist[v] + 1
                q.append(to)
    return dist

def tree_depth(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根 root からの深さ（距離）を返す。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: 各頂点の深さ配列。
    補足:
        実装は `bfs` を利用している。計算量は O(V)。
    """
    return bfs(g, root)

def tree_parent(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木における各頂点の親配列を構築する。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: parent[v]（根は -1）。
    補足:
        BFS で訪問順に親を設定する。計算量は O(V)。
    """
    n = len(g)
    parent = [-1] * n
    visited = [False] * n
    visited[root] = True
    q = deque([root])
    while q:
        v = q.popleft()
        for to in g[v]:
            if not visited[to]:
                visited[to] = True
                parent[to] = v
                q.append(to)
    return parent

def subtree_size(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木の各頂点について部分木サイズを求める。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: size[v] = v を根とする部分木サイズ。
    補足:
        深い頂点から親へサイズを集約する。計算量は O(VlogV)。
    """
    n = len(g)
    size = [1] * n
    parent = tree_parent(g, root)
    depth = tree_depth(g, root)
    order = sorted(range(n), key=lambda x: -depth[x])
    for v in order:
        if parent[v] != -1:
            size[parent[v]] += size[v]
    return size

def main() -> None:
    # ここに解答を書く
    N = INT()
    edges = TUPLES(N-1)
    g = build_graph(N, edges)
    if N == 1:
        pr(1)
        return
    size = subtree_size(g)
    print(N - max(size[i] for i in g[0]))





















if __name__ == "__main__":
    main()