# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
from re import M
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

class MaxFlow:
    """概要:
        Dinic 法による最大流を提供するクラス。

    メソッド:
        add_edge(u, v, cap): u→v に容量 cap の辺を追加する。
        max_flow(s, t): s→t の最大流量を返す。

    補足:
        計算量は O(V²E)。頂点数・辺数が数百程度なら十分高速。
        逆辺を自動管理するため、無向辺は add_edge を双方向で呼ぶか
        cap を同じ値で両方向に追加すること。

    使用例:
        mf = MaxFlow(n)
        mf.add_edge(0, 1, 10)
        mf.add_edge(1, 2, 5)
        print(mf.max_flow(0, 2))  # 5
    """
    def __init__(self, n: int):
        self.n = n
        self.graph = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        """u→v に容量 cap の有向辺を追加（逆辺も自動追加）"""
        self.graph[u].append([v, cap, len(self.graph[v])])
        self.graph[v].append([u, 0, len(self.graph[u]) - 1])

    def _bfs(self, s: int) -> list[int]:
        """BFS でレベルグラフを構築"""
        level = [-1] * self.n
        level[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for to, cap, _ in self.graph[v]:
                if cap > 0 and level[to] == -1:
                    level[to] = level[v] + 1
                    q.append(to)
        return level

    def _dfs(self, v: int, t: int, f: int, level: list[int], it: list[int]) -> int:
        """DFS でブロッキングフローを流す"""
        if v == t:
            return f
        while it[v] < len(self.graph[v]):
            e = self.graph[v][it[v]]
            to, cap, rev = e
            if cap > 0 and level[v] < level[to]:
                d = self._dfs(to, t, min(f, cap), level, it)
                if d > 0:
                    e[1] -= d
                    self.graph[to][rev][1] += d
                    return d
            it[v] += 1
        return 0

    def max_flow(self, s: int, t: int) -> int:
        """s→t の最大流量を返す"""
        flow = 0
        while True:
            level = self._bfs(s)
            if level[t] == -1:
                return flow
            it = [0] * self.n
            while True:
                f = self._dfs(s, t, INF, level, it)
                if f == 0:
                    break
                flow += f

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    mf = MaxFlow(N)
    for _ in range(M):
        u, v, w = MAP()
        mf.add_edge(u-1, v-1, w)
    print(mf.max_flow(0, N-1))





















if __name__ == "__main__":
    main()