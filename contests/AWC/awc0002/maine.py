# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from itertools import permutations, combinations, accumulate, product, chain
from functools import lru_cache, reduce
from typing import List, Tuple, Optional, Set, Dict, Callable, Union
from copy import deepcopy
import operator
import string

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> List[int]:
    return list(MAP())

def LISTS(n: int) -> List[List[int]]:
    return [LIST() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> List[str]:
    return [STR() for _ in range(n)]

def CHARS() -> List[str]:
    return list(STR())

def STRSL(n: int) -> List[List[str]]:
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


# ============================================================
# 数学・整数論（出題頻度：非常に高い）
# ============================================================

def is_prime(n:  int) -> bool:
    """素数判定 O(√n)"""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def prime_factors(n:  int) -> Dict[int, int]:
    """素因数分解 O(√n) → {素因数: 指数}"""
    factors = defaultdict(int)
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] += 1
            n //= d
        d += 1
    if n > 1:
        factors[n] += 1
    return dict(factors)

def divisors(n: int) -> List[int]:
    """約数列挙 O(√n) → ソート済みリスト"""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def sieve(n: int) -> Tuple[List[bool], List[int]]:
    """エラトステネスの篩 O(n log log n) → (is_prime配列, 素数リスト)"""
    is_prime_arr = [True] * (n + 1)
    if n >= 0:  is_prime_arr[0] = False
    if n >= 1: is_prime_arr[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if is_prime_arr[p]:
            for q in range(p * p, n + 1, p):
                is_prime_arr[q] = False
    primes = [i for i in range(2, n + 1) if is_prime_arr[i]]
    return is_prime_arr, primes

def gcd(a: int, b: int) -> int:
    """最大公約数"""
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """最小公倍数"""
    return a // gcd(a, b) * b

def ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """拡張ユークリッド互除法 → (gcd, x, y) where ax + by = gcd"""
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y

def pow_mod(x: int, n: int, mod:  int = MOD) -> int:
    """高速べき乗 O(log n)"""
    res = 1
    x %= mod
    while n > 0:
        if n & 1:
            res = res * x % mod
        x = x * x % mod
        n >>= 1
    return res

def mod_inverse(a:  int, mod: int = MOD) -> int:
    """逆元 (modが素数の場合) O(log mod)"""
    return pow_mod(a, mod - 2, mod)


# ============================================================
# 組み合わせ計算（出題頻度：非常に高い）
# ============================================================

class Combination:
    """組み合わせ計算 前処理O(n)、クエリO(1)
    
    使用例:
        comb = Combination(200000)
        print(comb.nCr(10, 3))  # 120
    """
    def __init__(self, n: int, mod: int = MOD):
        self.mod = mod
        self.fact = [1] * (n + 1)
        self.inv_fact = [1] * (n + 1)
        
        for i in range(1, n + 1):
            self.fact[i] = self.fact[i - 1] * i % mod
        
        self.inv_fact[n] = pow_mod(self. fact[n], mod - 2, mod)
        for i in range(n - 1, -1, -1):
            self.inv_fact[i] = self.inv_fact[i + 1] * (i + 1) % mod

    def nCr(self, n:  int, r: int) -> int:
        """組み合わせ nCr"""
        if r < 0 or r > n:  return 0
        return self.fact[n] * self. inv_fact[r] % self.mod * self.inv_fact[n - r] % self.mod

    def nPr(self, n: int, r:  int) -> int:
        """順列 nPr"""
        if r < 0 or r > n: return 0
        return self.fact[n] * self.inv_fact[n - r] % self.mod

    def nHr(self, n: int, r:  int) -> int:
        """重複組み合わせ nHr = C(n+r-1, r)"""
        return self.nCr(n + r - 1, r)

    def catalan(self, n: int) -> int:
        """カタラン数 C_n"""
        return self.nCr(2 * n, n) * pow_mod(n + 1, self.mod - 2, self.mod) % self.mod


# ============================================================
# 累積和（出題頻度：非常に高い）
# ============================================================

def prefix_sum(arr:  List[int]) -> List[int]:
    """1次元累積和 → ps[r] - ps[l] で [l, r) の和"""
    ps = [0]
    for x in arr:
        ps.append(ps[-1] + x)
    return ps

def prefix_sum_2d(grid: List[List[int]]) -> List[List[int]]:
    """2次元累積和"""
    H, W = len(grid), len(grid[0])
    ps = [[0] * (W + 1) for _ in range(H + 1)]
    for i in range(H):
        for j in range(W):
            ps[i + 1][j + 1] = ps[i][j + 1] + ps[i + 1][j] - ps[i][j] + grid[i][j]
    return ps

def range_sum_2d(ps: List[List[int]], y1: int, x1: int, y2: int, x2: int) -> int:
    """2次元累積和から [y1, y2) × [x1, x2) の和を取得"""
    return ps[y2][x2] - ps[y1][x2] - ps[y2][x1] + ps[y1][x1]


# ============================================================
# いもす法（出題頻度：高い）
# ============================================================

class Imos1D:
    """1次元いもす法
    
    使用例:
        imos = Imos1D(10)
        imos.add(2, 5, 1)   # [2, 5) に +1
        imos.add(3, 7, 2)   # [3, 7) に +2
        result = imos.build()
    """
    def __init__(self, n: int):
        self.n = n
        self.diff = [0] * (n + 1)

    def add(self, l: int, r:  int, x: int = 1) -> None:
        """[l, r) に x を加算"""
        self.diff[l] += x
        self.diff[r] -= x

    def build(self) -> List[int]:
        """累積和を計算して結果を返す"""
        result = [0] * self.n
        current = 0
        for i in range(self.n):
            current += self.diff[i]
            result[i] = current
        return result


class Imos2D:
    """2次元いもす法
    
    使用例:
        imos = Imos2D(H, W)
        imos.add(y1, x1, y2, x2, 1)  # [y1,y2) × [x1,x2) に +1
        result = imos.build()
    """
    def __init__(self, h: int, w:  int):
        self.h = h
        self. w = w
        self.diff = [[0] * (w + 1) for _ in range(h + 1)]

    def add(self, y1: int, x1: int, y2: int, x2: int, x: int = 1) -> None:
        """[y1, y2) × [x1, x2) に x を加算"""
        self.diff[y1][x1] += x
        self. diff[y1][x2] -= x
        self. diff[y2][x1] -= x
        self.diff[y2][x2] += x

    def build(self) -> List[List[int]]:
        """累積和を計算して結果を返す"""
        # 横方向
        for i in range(self. h):
            for j in range(self.w):
                self.diff[i][j + 1] += self.diff[i][j]
        # 縦方向
        for j in range(self. w):
            for i in range(self.h):
                self.diff[i + 1][j] += self.diff[i][j]
        return [row[:self.w] for row in self.diff[: self.h]]


# ============================================================
# Union-Find（出題頻度：非常に高い）
# ============================================================

class DSU:
    """Union-Find木（経路圧縮 + サイズ併合）
    
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

    def leader(self, x:  int) -> int:
        """根を取得"""
        if self.parent[x] != x:
            self.parent[x] = self. leader(self.parent[x])
        return self.parent[x]

    def merge(self, a: int, b:  int) -> bool:
        """併合（成功でTrue）"""
        a, b = self. leader(a), self.leader(b)
        if a == b:  return False
        if self.rank[a] < self.rank[b]: a, b = b, a
        self.parent[b] = a
        self.rank[a] += self.rank[b]
        self._group_count -= 1
        return True

    def same(self, a: int, b: int) -> bool:
        """同じグループか"""
        return self.leader(a) == self.leader(b)

    def size(self, x:  int) -> int:
        """xが属するグループのサイズ"""
        return self. rank[self.leader(x)]

    def group_count(self) -> int:
        """グループ数"""
        return self._group_count

    def groups(self) -> List[List[int]]:
        """全グループを取得"""
        result = defaultdict(list)
        for i in range(self.n):
            result[self.leader(i)].append(i)
        return list(result.values())


class WeightedDSU:
    """重み付きUnion-Find（ポテンシャル付き）
    
    weight(x) - weight(y) = w となるような重みを管理
    使用例:
        wuf = WeightedDSU(n)
        wuf.merge(x, y, w)  # weight[x] - weight[y] = w
        diff = wuf.diff(x, y)  # weight[x] - weight[y]
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [1] * n
        self. weight = [0] * n  # 親への重み

    def leader(self, x: int) -> int:
        if self.parent[x] == x:
            return x
        root = self.leader(self.parent[x])
        self.weight[x] += self.weight[self.parent[x]]
        self.parent[x] = root
        return root

    def get_weight(self, x: int) -> int:
        """xの重みを取得"""
        self.leader(x)
        return self.weight[x]

    def diff(self, x: int, y:  int) -> int:
        """weight[x] - weight[y] を返す"""
        return self.get_weight(x) - self.get_weight(y)

    def merge(self, x: int, y:  int, w: int) -> bool:
        """weight[x] - weight[y] = w となるよう併合"""
        w += self.get_weight(y) - self.get_weight(x)
        x, y = self. leader(x), self.leader(y)
        if x == y: return False
        if self.rank[x] < self.rank[y]:
            x, y = y, x
            w = -w
        self. parent[y] = x
        self. weight[y] = w
        self. rank[x] += self.rank[y]
        return True

    def same(self, x: int, y: int) -> bool:
        return self.leader(x) == self.leader(y)


# ============================================================
# グラフアルゴリズム（出題頻度：非常に高い）
# ============================================================

def build_graph(n:  int, edges: List[Tuple[int, int]], directed: bool = False) -> List[List[int]]:
    """隣接リスト構築（重みなし）"""
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a]. append(b)
        if not directed:
            g[b].append(a)
    return g

def build_weighted_graph(n:  int, edges: List[Tuple[int, int, int]], directed: bool = False) -> List[List[Tuple[int, int]]]:
    """隣接リスト構築（重みあり）"""
    g = [[] for _ in range(n)]
    for a, b, c in edges:
        g[a].append((b, c))
        if not directed:
            g[b].append((a, c))
    return g

def bfs(g: List[List[int]], s: int) -> List[int]:
    """BFS最短距離（重みなし）→ 到達不能は-1"""
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

def bfs_grid(grid: List[List[str]], sy: int, sx:  int, wall: str = '#') -> List[List[int]]: 
    """グリッドBFS → 到達不能は-1"""
    H, W = len(grid), len(grid[0])
    dist = [[-1] * W for _ in range(H)]
    dist[sy][sx] = 0
    q = deque([(sy, sx)])
    while q:
        y, x = q.popleft()
        for dy, dx in DIR4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and dist[ny][nx] == -1 and grid[ny][nx] != wall:
                dist[ny][nx] = dist[y][x] + 1
                q.append((ny, nx))
    return dist

def dijkstra(g: List[List[Tuple[int, int]]], s: int) -> List[int]:
    """Dijkstra法 O((V+E)log V)"""
    dist = [INF] * len(g)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq. heappop(pq)
        if d > dist[v]:  continue
        for to, w in g[v]:
            if dist[v] + w < dist[to]:
                dist[to] = dist[v] + w
                heapq. heappush(pq, (dist[to], to))
    return dist

def bellman_ford(n: int, edges:  List[Tuple[int, int, int]], s: int) -> Tuple[List[int], bool]:
    """Bellman-Ford法 O(VE) → (距離, 負閉路あり?)"""
    dist = [INF] * n
    dist[s] = 0
    for i in range(n):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated: break
        if i == n - 1:  return dist, True
    return dist, False

def warshall_floyd(n: int, edges: List[Tuple[int, int, int]]) -> List[List[int]]:
    """Warshall-Floyd法 O(V³) → 全点対最短距離"""
    dist = [[INF] * n for _ in range(n)]
    for i in range(n): dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist

def topological_sort(g: List[List[int]]) -> Optional[List[int]]:
    """トポロジカルソート → 閉路ありならNone"""
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
                q. append(to)
    return result if len(result) == n else None

def detect_cycle(g:  List[List[int]]) -> Optional[List[int]]:
    """有向グラフの閉路検出 → 閉路の頂点リスト or None"""
    n = len(g)
    color = [0] * n  # 0:未訪問, 1: 訪問中, 2:訪問済
    parent = [-1] * n
    cycle = []
    
    def dfs(v:  int) -> bool:
        color[v] = 1
        for to in g[v]:
            if color[to] == 1:  # 閉路発見
                cycle.append(to)
                u = v
                while u != to:
                    cycle.append(u)
                    u = parent[u]
                cycle.reverse()
                return True
            if color[to] == 0:
                parent[to] = v
                if dfs(to): return True
        color[v] = 2
        return False
    
    for i in range(n):
        if color[i] == 0:
            if dfs(i): return cycle
    return None


# ============================================================
# 木アルゴリズム（出題頻度：高い）
# ============================================================

def tree_diameter(g: List[List[int]]) -> Tuple[int, int, int]:
    """木の直径 → (直径, 端点1, 端点2)"""
    def bfs_farthest(s: int) -> Tuple[int, int]:
        dist = bfs(g, s)
        farthest = max(range(len(g)), key=lambda x: dist[x])
        return farthest, dist[farthest]
    
    u, _ = bfs_farthest(0)
    v, d = bfs_farthest(u)
    return d, u, v

def tree_depth(g: List[List[int]], root: int = 0) -> List[int]:
    """各頂点の深さを計算"""
    return bfs(g, root)

def tree_parent(g: List[List[int]], root: int = 0) -> List[int]:
    """各頂点の親を計算（根は-1）"""
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

def subtree_size(g: List[List[int]], root: int = 0) -> List[int]:
    """部分木のサイズを計算"""
    n = len(g)
    size = [1] * n
    parent = tree_parent(g, root)
    depth = tree_depth(g, root)
    order = sorted(range(n), key=lambda x:  -depth[x])
    for v in order:
        if parent[v] != -1:
            size[parent[v]] += size[v]
    return size


class LCA:
    """最小共通祖先（ダブリング）
    
    使用例:
        lca = LCA(g, root=0)
        print(lca.query(u, v))
        print(lca. dist(u, v))
    """
    def __init__(self, g: List[List[int]], root: int = 0):
        self.n = len(g)
        self.log = max(1, (self.n - 1).bit_length())
        self.depth = [-1] * self. n
        self. parent = [[-1] * self. n for _ in range(self.log)]
        
        # BFSで深さと親を計算
        self.depth[root] = 0
        q = deque([root])
        while q:
            v = q.popleft()
            for to in g[v]:
                if self. depth[to] == -1:
                    self.depth[to] = self. depth[v] + 1
                    self.parent[0][to] = v
                    q. append(to)
        
        # ダブリングテーブル構築
        for k in range(1, self.log):
            for v in range(self. n):
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
        if u == v:  return u
        # 二分探索でLCAを求める
        for k in range(self.log - 1, -1, -1):
            if self.parent[k][u] != self.parent[k][v]:
                u = self. parent[k][u]
                v = self.parent[k][v]
        return self.parent[0][u]

    def dist(self, u: int, v:  int) -> int:
        """u-v間の距離"""
        return self. depth[u] + self.depth[v] - 2 * self. depth[self.query(u, v)]


# ============================================================
# データ構造（出題頻度：高い）
# ============================================================

class BIT:
    """Binary Indexed Tree (Fenwick Tree) 0-indexed
    
    使用例:
        bit = BIT(n)
        bit.add(i, x)        # a[i] += x
        bit. sum(i)           # a[0] + ...  + a[i]
        bit.range_sum(l, r)  # a[l] + ... + a[r-1]
    """
    def __init__(self, n:  int):
        self.n = n
        self.data = [0] * (n + 1)

    def add(self, i: int, x: int) -> None:
        i += 1
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i:  int) -> int:
        """a[0] + ... + a[i]"""
        s = 0
        i += 1
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """a[l] + ... + a[r-1]"""
        if l >= r:  return 0
        return self.sum(r - 1) - (self.sum(l - 1) if l > 0 else 0)

    def lower_bound(self, w: int) -> int:
        """累積和が w 以上になる最小のインデックス"""
        if w <= 0: return 0
        x, k = 0, 1
        while k * 2 <= self.n: k *= 2
        while k > 0:
            if x + k <= self.n and self.data[x + k] < w:
                w -= self.data[x + k]
                x += k
            k //= 2
        return x


class SegTree:
    """汎用Segment Tree
    
    使用例:
        # 区間和
        st = SegTree(n, op=operator.add, e=0)
        # 区間最小
        st = SegTree(n, op=min, e=INF)
        # 区間最大
        st = SegTree(n, op=max, e=-INF)
        # 区間GCD
        st = SegTree(n, op=gcd, e=0)
    """
    def __init__(self, n: int, op: Callable = operator.add, e: int = 0):
        self.op = op
        self.e = e
        self.size = 1
        while self.size < n:  self.size <<= 1
        self.data = [e] * (2 * self.size)

    def build(self, arr:  List[int]) -> None:
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[i << 1], self. data[i << 1 | 1])

    def set(self, i:  int, v: int) -> None:
        """a[i] = v"""
        i += self.size
        self.data[i] = v
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def get(self, i: int) -> int:
        """a[i]を取得"""
        return self.data[self.size + i]

    def query(self, l:  int, r: int) -> int:
        """[l, r) の演算結果"""
        res = self.e
        l += self.size
        r += self. size
        while l < r:
            if l & 1:
                res = self.op(res, self. data[l])
                l += 1
            if r & 1:
                r -= 1
                res = self.op(res, self. data[r])
            l >>= 1
            r >>= 1
        return res

    def all_query(self) -> int:
        """全区間の演算結果"""
        return self.data[1]

    update = set  # エイリアス


class SortedMultiset:
    """平方分割によるMultiset（要素の重複OK）
    
    使用例:
        ms = SortedMultiset()
        ms.add(5)
        ms.add(3)
        ms.discard(5)
        print(ms[0])  # 最小値
        print(ms[-1]) # 最大値
    """
    BUCKET_RATIO = 50
    REBUILD_RATIO = 170

    def __init__(self, a: List[int] = []):
        a = list(a)
        if a:
            a.sort()
        self._build(a)

    def _build(self, a: List[int]) -> None:
        self.a = a
        self.size = len(a)
        if self.size == 0:
            self.buckets = []
        else:
            bucket_size = int(math.ceil(math.sqrt(self. size / self.BUCKET_RATIO)))
            self.buckets = [a[i:i + bucket_size] for i in range(0, self.size, bucket_size)]

    def __len__(self) -> int:
        return self.size

    def __contains__(self, x: int) -> bool:
        if not self.buckets:  return False
        for bucket in self.buckets:
            if bucket[0] <= x <= bucket[-1]:
                i = bisect_left(bucket, x)
                if i < len(bucket) and bucket[i] == x:
                    return True
        return False

    def add(self, x:  int) -> None:
        if not self.buckets:
            self. buckets = [[x]]
            self.size = 1
            return
        for i, bucket in enumerate(self.buckets):
            if x <= bucket[-1] or i == len(self. buckets) - 1:
                pos = bisect_right(bucket, x)
                bucket.insert(pos, x)
                self.size += 1
                if len(bucket) > len(self.buckets) * self.REBUILD_RATIO:
                    self._build(list(chain.from_iterable(self.buckets)))
                return

    def discard(self, x: int) -> bool:
        for bucket in self.buckets:
            if bucket[0] <= x <= bucket[-1]:
                i = bisect_left(bucket, x)
                if i < len(bucket) and bucket[i] == x:
                    bucket. pop(i)
                    self.size -= 1
                    if not bucket:
                        self. buckets. remove(bucket)
                    return True
        return False

    def __getitem__(self, i: int) -> int:
        if i < 0: i += self.size
        for bucket in self.buckets:
            if i < len(bucket):
                return bucket[i]
            i -= len(bucket)
        raise IndexError

    def index(self, x:  int) -> int:
        """x未満の要素数を返す"""
        cnt = 0
        for bucket in self. buckets:
            if x <= bucket[0]:
                return cnt
            if x > bucket[-1]:
                cnt += len(bucket)
            else:
                return cnt + bisect_left(bucket, x)
        return cnt

    def index_right(self, x:  int) -> int:
        """x以下の要素数を返す"""
        cnt = 0
        for bucket in self.buckets:
            if x < bucket[0]:
                return cnt
            if x >= bucket[-1]:
                cnt += len(bucket)
            else:
                return cnt + bisect_right(bucket, x)
        return cnt


# ============================================================
# 文字列アルゴリズム（出題頻度：中〜高）
# ============================================================

class RollingHash:
    """ローリングハッシュ（ダブルハッシュ版）
    
    使用例:
        rh = RollingHash("abcabc")
        print(rh.get(0, 3) == rh.get(3, 6))  # True ("abc" == "abc")
    """
    MOD1, MOD2 = 10**9 + 7, 10**9 + 9
    BASE1, BASE2 = 1007, 2009

    def __init__(self, s: str):
        self.n = len(s)
        self.hash1 = [0] * (self.n + 1)
        self.hash2 = [0] * (self.n + 1)
        self.pow1 = [1] * (self. n + 1)
        self.pow2 = [1] * (self. n + 1)
        for i in range(self.n):
            self.hash1[i + 1] = (self.hash1[i] * self.BASE1 + ord(s[i])) % self.MOD1
            self.hash2[i + 1] = (self. hash2[i] * self.BASE2 + ord(s[i])) % self.MOD2
            self.pow1[i + 1] = self.pow1[i] * self.BASE1 % self. MOD1
            self.pow2[i + 1] = self.pow2[i] * self.BASE2 % self.MOD2

    def get(self, l: int, r: int) -> Tuple[int, int]:
        """[l, r) のハッシュ"""
        h1 = (self.hash1[r] - self.hash1[l] * self.pow1[r - l]) % self.MOD1
        h2 = (self.hash2[r] - self.hash2[l] * self. pow2[r - l]) % self.MOD2
        return (h1, h2)

    def lcp(self, i: int, j:  int) -> int:
        """位置i, jから始まる最長共通接頭辞の長さ"""
        ok, ng = 0, min(self.n - i, self.n - j) + 1
        while ng - ok > 1:
            mid = (ok + ng) // 2
            if self.get(i, i + mid) == self.get(j, j + mid):
                ok = mid
            else:
                ng = mid
        return ok


def z_algorithm(s: str) -> List[int]:
    """Z-algorithm:  z[i] = s と s[i: ] の最長共通接頭辞の長さ"""
    n = len(s)
    z = [0] * n
    z[0] = n
    i, j = 1, 0
    while i < n:
        while i + j < n and s[j] == s[i + j]:
            j += 1
        z[i] = j
        if j == 0:
            i += 1
            continue
        k = 1
        while k < j and k + z[k] < j:
            z[i + k] = z[k]
            k += 1
        i += k
        j -= k
    return z


def run_length_encode(s: Union[str, List]) -> List[Tuple]:
    """ランレングス圧縮 → [(文字, 連続数), ...]"""
    if not s:  return []
    result = []
    current, count = s[0], 1
    for i in range(1, len(s)):
        if s[i] == current:
            count += 1
        else:
            result.append((current, count))
            current, count = s[i], 1
    result.append((current, count))
    return result


# ============================================================
# 二分探索（出題頻度：非常に高い）
# ============================================================

def binary_search_min(ng: int, ok: int, check: Callable[[int], bool]) -> int:
    """条件を満たす最小値を探す
    
    check(x) = True となる最小の x を返す
    ng: 条件を満たさない値, ok: 条件を満たす値
    
    例:  x >= 5 となる最小のx → binary_search_min(0, 10, lambda x: x >= 5)
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

def binary_search_max(ok: int, ng:  int, check:  Callable[[int], bool]) -> int:
    """条件を満たす最大値を探す
    
    check(x) = True となる最大の x を返す
    ok: 条件を満たす値, ng: 条件を満たさない値
    
    例: x <= 5 となる最大のx → binary_search_max(0, 10, lambda x: x <= 5)
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

def binary_search_float(ok: float, ng: float, check: Callable[[float], bool], iterations: int = 100) -> float:
    """実数二分探索"""
    for _ in range(iterations):
        mid = (ok + ng) / 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok


# ============================================================
# 座標圧縮（出題頻度：高い）
# ============================================================

def compress(arr: List[int]) -> Tuple[Dict[int, int], List[int]]:
    """座標圧縮 → (値→index辞書, ソート済み元値リスト)"""
    xs = sorted(set(arr))
    mp = {x: i for i, x in enumerate(xs)}
    return mp, xs

def compress_list(arr: List[int]) -> List[int]:
    """座標圧縮 → 圧縮後の配列"""
    mp, _ = compress(arr)
    return [mp[x] for x in arr]


# ============================================================
# ユーティリティ（出題頻度：高い）
# ============================================================

def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    """マンハッタン距離"""
    return abs(x1 - x2) + abs(y1 - y2)

def chebyshev(x1: int, y1: int, x2: int, y2: int) -> int:
    """チェビシェフ距離"""
    return max(abs(x1 - x2), abs(y1 - y2))

def ceil_div(a: int, b:  int) -> int:
    """切り上げ除算 (a, b > 0)"""
    return (a + b - 1) // b

def floor_sum(n: int, m: int, a: int, b:  int) -> int:
    """Σ_{i=0}^{n-1} floor((a*i + b) / m)"""
    ans = 0
    if a >= m:
        ans += (n - 1) * n * (a // m) // 2
        a %= m
    if b >= m:
        ans += n * (b // m)
        b %= m
    y_max = (a * n + b) // m
    x_max = y_max * m - b
    if y_max == 0:
        return ans
    ans += (n - (x_max + a - 1) // a) * y_max
    ans += floor_sum(y_max, a, m, (a - x_max % a) % a)
    return ans

def rotate_90(grid: List[List]) -> List[List]:
    """グリッドを時計回りに90度回転"""
    H, W = len(grid), len(grid[0])
    return [[grid[H - 1 - j][i] for j in range(H)] for i in range(W)]

def transpose(grid: List[List]) -> List[List]:
    """グリッドの転置"""
    return [list(row) for row in zip(*grid)]

# ============================================================
# 記録して出力
# ============================================================

class Output:
    """データを記録してまとめて出力するためのクラス"""
    def __init__(self):
        self.buffer = []

    def add(self, *args, sep: str = ' ') -> None:
        """引数を一つの行(文字列)として結合して記録"""
        self.buffer.append(sep.join(map(str, args)))

    def extend(self, iterable) -> None:
        """イテラブルの各要素をそれぞれ一行として記録"""
        for item in iterable:
            if isinstance(item, (list, tuple, range)):
                self.add(*item)
            else:
                self.add(item)

    def grid(self, grid: List[List], sep: str = ' ') -> None:
        """2次元配列を各行を空白区切りなどで記録"""
        for row in grid:
            self.add(*row, sep=sep)

    def yes(self, cond: bool, yes: str = "Yes", no: str = "No") -> None:
        """条件に応じてYes/Noを記録"""
        self.add(yes if cond else no)

    def flush(self, sep: str = '\n', end: str = '\n', file=sys.stdout) -> None:
        """記録した内容を結合して出力し、バッファを空にする"""
        if self.buffer:
            file.write(sep.join(self.buffer) + end)
            self.buffer = []

    def get(self, sep: str = '\n') -> str:
        """記録した内容を結合した文字列を返す"""
        return sep.join(self.buffer)

    def __len__(self) -> int:
        return len(self.buffer)

# ============================================================
# デバッグ
# ============================================================

def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

def print_grid(grid:  List[List], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))

def yn(cond: bool) -> None:
    """条件に応じてYes/No出力"""
    print("Yes" if cond else "No")

# ============================================================
# main
# ============================================================

def main() -> None:
    # ここに解答を書く
    #out = Output()
    pass










if __name__ == "__main__":
    main()