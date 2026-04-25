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

class LCA:
    """概要:
        ダブリング法で LCA（最小共通祖先）と頂点間距離を高速計算するクラス。

    メソッド:
        query(u, v): u と v の LCA を返す。
        dist(u, v): u-v 間の辺数距離を返す。

    計算量:
        初期化は O(NlogN)、query と dist は O(logN)。

    補足:
        初期化時に BFS と親テーブル構築を行い、クエリは O(logN)。

    使用例:
        lca = LCA(g, root=0)
        print(lca.query(u, v))
        print(lca.dist(u, v))
    """
    def __init__(self, g: list[list[int]], root: int = 0):
        self.n = len(g)
        self.log = max(1, (self.n - 1).bit_length())
        self.depth = [-1] * self.n
        self.parent = [[-1] * self.n for _ in range(self.log)]

        # BFSで深さと親を計算
        self.depth[root] = 0
        q = deque([root])
        while q:
            v = q.popleft()
            for to in g[v]:
                if self.depth[to] == -1:
                    self.depth[to] = self.depth[v] + 1
                    self.parent[0][to] = v
                    q.append(to)

        # ダブリングテーブル構築
        for k in range(1, self.log):
            for v in range(self.n):
                if self.parent[k-1][v] != -1:
                    self.parent[k][v] = self.parent[k-1][self.parent[k-1][v]]

    def query(self, u: int, v: int) -> int:
        """u, v のLCAを返す"""
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        # 深さを揃える
        diff = self.depth[v] - self.depth[u]
        for k in range(self.log):
            if (diff >> k) & 1:
                v = self.parent[k][v]
        if u == v: return u
        # 二分探索でLCAを求める
        for k in range(self.log - 1, -1, -1):
            if self.parent[k][u] != self.parent[k][v]:
                u = self.parent[k][u]
                v = self.parent[k][v]
        return self.parent[0][u]

    def dist(self, u: int, v: int) -> int:
        """u-v間の距離"""
        return self.depth[u] + self.depth[v] - 2 * self.depth[self.query(u, v)]

def main() -> None:
    # ここに解答を書く
    N, Q = MAP()
    CP = TUPLES(Q)
    g = dict()
    for i in range(N):
        g[i] = i
    for C, P in CP:
        C -= 1
        P -= 1
        g[C] = P
    li = [-1] * N
    for i in range(N):
        if g[i] == i:
            li[i] = i
    for i in range(N):
        if li[i] != -1: continue
        if li[i] == i: continue
        s = []
        now = i
        while li[now] == -1:
            s.append(now)
            now = g[now]
        for j in s:
            li[i] = li[now]
    d = dict(Counter(li))
    ans = []
    for i in range(N):
        ans.append(d.get(i, 0))
    print(*ans)





















if __name__ == "__main__":
    main()