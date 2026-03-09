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
        実装は `bfs` を利用している。
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
        BFS で訪問順に親を設定する。
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

def subtree_height(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木の各頂点について部分木の高さ（階級）を求める。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: height[v] = v を根とする部分木の高さ。
                   葉は 0、それ以外は直属の子の高さの最大値 + 1。
    補足:
        深い頂点から親へ max(子の高さ) + 1 を伝播する。
    """
    n = len(g)
    height = [0] * n
    parent = tree_parent(g, root)
    depth = tree_depth(g, root)
    order = sorted(range(n), key=lambda x: -depth[x])
    for v in order:
        if parent[v] != -1:
            height[parent[v]] = max(height[parent[v]], height[v] + 1)
    return height

def main() -> None:
    # ここに解答を書く
    N, T = MAP()
    g = [[] for _ in range(N)]
    for _ in range(N-1):
        A, B = MAP()
        g[A-1].append(B-1)
        g[B-1].append(A-1)
    g = subtree_height(g, root=T-1)
    print(*g, sep=" ")





















if __name__ == "__main__":
    main()