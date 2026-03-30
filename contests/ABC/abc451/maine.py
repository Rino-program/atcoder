# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import dis
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

class DSU:
    """概要:
        Union-Find（Disjoint Set Union）を提供するクラス。

    メソッド:
        leader(x): x の属する連結成分の代表元を返す。
        merge(a, b): a と b の成分を併合する。
        same(a, b): 同一成分か判定する。
        size(x): x の成分サイズを返す。
        group_count(): 現在の成分数を返す。
        groups(): 全成分を頂点リストで返す。

    計算量:
        leader/merge/same/size は償却 O(α(N))、group_count は O(1)、groups は O(Nα(N))。

    補足:
        経路圧縮とサイズ併合でほぼ償却 O(α(N))。

    使用例:
        uf = DSU(n)
        uf.merge(0, 1)
        print(uf.same(0, 1))  # True
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.n = n
        self._group_count = n

    def leader(self, x: int) -> int:
        """根を取得"""
        if self.parent[x] != x:
            self.parent[x] = self.leader(self.parent[x])
        return self.parent[x]

    def merge(self, a: int, b: int) -> bool:
        """併合（成功でTrue）"""
        a, b = self.leader(a), self.leader(b)
        if a == b: return False
        if self.rank[a] < self.rank[b]: a, b = b, a
        self.parent[b] = a
        self.rank[a] += self.rank[b]
        self._group_count -= 1
        return True

    def same(self, a: int, b: int) -> bool:
        """同じグループか"""
        return self.leader(a) == self.leader(b)

    def size(self, x: int) -> int:
        """xが属するグループのサイズ"""
        return self.rank[self.leader(x)]

    def group_count(self) -> int:
        """グループ数"""
        return self._group_count

    def groups(self) -> list[list[int]]:
        """全グループを取得"""
        result = defaultdict(list)
        for i in range(self.n):
            result[self.leader(i)].append(i)
        return list(result.values())

def kruskal(n: int, edges: list[tuple[int, int, int]]) -> tuple[int, list[tuple[int, int, int]], bool]:
    """概要:
        Kruskal 法で最小全域木（または最小全域森）を構築する。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
    出力:
        tuple[int, list[tuple[int, int, int]], bool]:
            (総コスト, 採用辺リスト, グラフが連結でMST完成か)。
    補足:
        辺を重み昇順に処理し、DSUで閉路を回避する。計算量は O(ElogE)。
    """
    uf = DSU(n)
    cost = 0
    used = []
    for u, v, w in sorted(edges, key=lambda x: x[2]):
        if uf.merge(u, v):
            cost += w
            used.append((u, v, w))
    return cost, used, len(used) == n - 1

def get_dist(s: int, g: list[list[tuple[int, int]]], N: int) -> list[int]:
    dist = [INF] * N
    dist[s] = 0
    que = deque([s])
    while que:
        v = que.popleft()
        for w, c in g[v]:
            if dist[w] == INF:
                dist[w] = dist[v] + c
                que.append(w)
    return dist

def main() -> None:
    # ここに解答を書く
    N = INT()
    A = [[0] * N for _ in range(N)]
    edge = []
    for i in range(N):
        row = LIST()
        for k, v in enumerate(row):
            j = i + 1 + k
            A[i][j] = v
            A[j][i] = v
            edge.append((i, j, v))
    cost, used, is_connected = kruskal(N, edge)
    if not is_connected:
        No()
        return
    g: list[list[tuple[int, int]]] = [[] for _ in range(N)]
    for u, v, w in used:
        g[u].append((v, w))
        g[v].append((u, w))
    """par = -1
    for v in range(N):
        if v == 0: continue
        m = -1
        for u in range(N):
            if u != v and A[0][u] + A[u][v] == A[0][v]:
                if A[0][u] > m:
                    m = A[0][u]
                    par = u
        if par == -1 or m == -1 or (w := A[0][v] - A[0][par]) <= 0:
            No()
            return
        g[par].append((v, w))
        g[v].append((par, w))"""
    ok = True
    for s in range(N):
        dist = get_dist(s, g, N)
        for t in range(N):
            if dist[t] != A[s][t]:
                ok = False
                break
        if not ok:
            break
    yn(ok)





















if __name__ == "__main__":
    main()