# coding: utf-8
# AtCoder Competition Template v2.1 ALL (PyPy 7.3.20 / Python 3.11)
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from itertools import permutations, combinations, accumulate, product, chain
from functools import lru_cache, reduce
from collections.abc import Callable
from copy import deepcopy
import operator
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


# ============================================================
# 数学・整数論
# ============================================================

def is_prime(n: int) -> bool:
    """概要:
        整数 n が素数かどうかを判定する。
    入力:
        n (int): 判定対象の整数。
    出力:
        bool: n が素数なら True、そうでなければ False。
    補足:
        計算量は O(√n)。n < 2 は素数ではない。
    """
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def prime_factors(n: int) -> dict[int, int]:
    """概要:
        整数 n を素因数分解し、素因数ごとの指数を返す。
    入力:
        n (int): 2 以上を想定した分解対象の整数。
    出力:
        dict[int, int]: {素因数: 指数} の辞書。
    補足:
        計算量は O(√n)。n <= 1 の場合は空辞書を返す。
    """
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

def divisors(n: int) -> list[int]:
    """概要:
        整数 n の正の約数を全列挙して昇順で返す。
    入力:
        n (int): 約数を求める対象の正整数。
    出力:
        list[int]: n の約数を昇順に並べたリスト。
    補足:
        計算量は O(√n)。
    """
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def sieve(n: int) -> tuple[list[bool], list[int]]:
    """概要:
        0..n の素数判定配列と素数一覧をエラトステネスの篩で構築する。
    入力:
        n (int): 上限値。
    出力:
        tuple[list[bool], list[int]]: (is_prime配列, 素数リスト)。
    補足:
        計算量は O(n log log n)。
    """
    is_prime_arr = [True] * (n + 1)
    if n >= 0: is_prime_arr[0] = False
    if n >= 1: is_prime_arr[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if is_prime_arr[p]:
            for q in range(p * p, n + 1, p):
                is_prime_arr[q] = False
    primes = [i for i in range(2, n + 1) if is_prime_arr[i]]
    return is_prime_arr, primes

def gcd(a: int, b: int) -> int:
    """概要:
        2整数 a, b の最大公約数を返す。
    入力:
        a (int), b (int): 対象整数。
    出力:
        int: gcd(a, b)。
    補足:
        ユークリッドの互除法を使用する。
    """
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """概要:
        2整数 a, b の最小公倍数を返す。
    入力:
        a (int), b (int): 対象整数。
    出力:
        int: lcm(a, b)。
    補足:
        gcd を使って a // gcd(a, b) * b で計算する。
    """
    return a // gcd(a, b) * b

def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """概要:
        拡張ユークリッド互除法で ax + by = gcd(a, b) を満たす係数を求める。
    入力:
        a (int), b (int): 対象整数。
    出力:
        tuple[int, int, int]: (g, x, y)。g = gcd(a, b)、ax + by = g。
    補足:
        逆元計算や一次不定方程式で利用できる。
    """
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y

def pow_fast(x: int, n: int) -> int:
    """概要:
        x^n を高速に計算する（繰り返し二乗法）。
    入力:
        x (int): 底。
        n (int): 非負整数の指数。
    出力:
        int: x^n。
    補足:
        二分累乗法（繰り返し二乗法）を用い、計算量は O(log n)。
    """
    res = 1
    while n > 0:
        if n & 1:
            res = res * x
        x = x * x
        n >>= 1
    return res

def pow_mod(x: int, n: int, mod: int = MOD) -> int:
    """概要:
        x^n を mod で割った余りを高速に計算する。
    入力:
        x (int): 底。
        n (int): 非負整数の指数。
        mod (int): 法。
    出力:
        int: x^n mod mod。
    補足:
        二分累乗法を用い、計算量は O(log n)。
    """
    res = 1
    x %= mod
    while n > 0:
        if n & 1:
            res = res * x % mod
        x = x * x % mod
        n >>= 1
    return res

def mod_inverse(a: int, mod: int = MOD) -> int:
    """概要:
        a の mod における乗法逆元を返す。
    入力:
        a (int): 逆元を求める値。
        mod (int): 法。
    出力:
        int: a^{-1} mod mod。
    補足:
        mod が素数で a と mod が互いに素である前提（フェルマーの小定理）。
    """
    return pow_mod(a, mod - 2, mod)


# ============================================================
# 組み合わせ計算
# ============================================================

class Combination:
    """概要:
        階乗・逆階乗を前計算して組み合わせ関連値を高速に返すクラス。

    メソッド:
        nCr(n, r): 組み合わせ数 C(n, r) を返す。
        nPr(n, r): 順列数 P(n, r) を返す。
        nHr(n, r): 重複組み合わせ数 H(n, r) を返す。
        catalan(n): n 番目のカタラン数を返す。

    計算量:
        初期化 O(n)、各クエリ O(1)。

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

        self.inv_fact[n] = pow_mod(self.fact[n], mod - 2, mod)
        for i in range(n - 1, -1, -1):
            self.inv_fact[i] = self.inv_fact[i + 1] * (i + 1) % mod

    def nCr(self, n: int, r: int) -> int:
        """組み合わせ nCr"""
        if r < 0 or r > n: return 0
        return self.fact[n] * self.inv_fact[r] % self.mod * self.inv_fact[n - r] % self.mod

    def nPr(self, n: int, r: int) -> int:
        """順列 nPr"""
        if r < 0 or r > n: return 0
        return self.fact[n] * self.inv_fact[n - r] % self.mod

    def nHr(self, n: int, r: int) -> int:
        """重複組み合わせ nHr = C(n+r-1, r)"""
        return self.nCr(n + r - 1, r)

    def catalan(self, n: int) -> int:
        """カタラン数 C_n"""
        return self.nCr(2 * n, n) * pow_mod(n + 1, self.mod - 2, self.mod) % self.mod


# ============================================================
# 累積和
# ============================================================

def prefix_sum(arr: list[int]) -> list[int]:
    """概要:
        1次元配列の累積和配列を構築する。
    入力:
        arr (list[int]): 元配列。
    出力:
        list[int]: 先頭に 0 を持つ累積和配列 ps。
    補足:
        区間和は ps[r] - ps[l]（半開区間 [l, r)）。
    """
    ps = [0]
    for x in arr:
        ps.append(ps[-1] + x)
    return ps

def prefix_sum_2d(grid: list[list[int]]) -> list[list[int]]:
    """概要:
        2次元配列の累積和テーブルを構築する。
    入力:
        grid (list[list[int]]): 数値グリッド。
    出力:
        list[list[int]]: (H+1)×(W+1) の2次元累積和。
    補足:
        矩形和は inclusion-exclusion で O(1) 取得できる。
    """
    H, W = len(grid), len(grid[0])
    ps = [[0] * (W + 1) for _ in range(H + 1)]
    for i in range(H):
        for j in range(W):
            ps[i + 1][j + 1] = ps[i][j + 1] + ps[i + 1][j] - ps[i][j] + grid[i][j]
    return ps

def range_sum_2d(ps: list[list[int]], y1: int, x1: int, y2: int, x2: int) -> int:
    """概要:
        2次元累積和から矩形 [y1, y2) × [x1, x2) の総和を返す。
    入力:
        ps (list[list[int]]): 2次元累積和テーブル。
        y1, x1, y2, x2 (int): 半開区間の境界。
    出力:
        int: 指定矩形の総和。
    補足:
        `prefix_sum_2d` の戻り値を前提とする。
    """
    return ps[y2][x2] - ps[y1][x2] - ps[y2][x1] + ps[y1][x1]


# ============================================================
# いもす法
# ============================================================

class Imos1D:
    """概要:
        1次元いもす法（差分配列）を扱うクラス。

    メソッド:
        add(l, r, x): 区間 [l, r) に x を加算予約する。
        build(): 全予約を反映した最終配列を返す。

    補足:
        複数区間更新をまとめて行い、最後に一度だけ累積して確定する。

    使用例:
        imos = Imos1D(10)
        imos.add(2, 5, 1)   # [2, 5) に +1
        imos.add(3, 7, 2)   # [3, 7) に +2
        result = imos.build()
    """
    def __init__(self, n: int):
        self.n = n
        self.diff = [0] * (n + 1)

    def add(self, l: int, r: int, x: int = 1) -> None:
        """[l, r) に x を加算"""
        self.diff[l] += x
        self.diff[r] -= x

    def build(self) -> list[int]:
        """累積和を計算して結果を返す"""
        result = [0] * self.n
        current = 0
        for i in range(self.n):
            current += self.diff[i]
            result[i] = current
        return result


class Imos2D:
    """概要:
        2次元いもす法（差分グリッド）を扱うクラス。

    メソッド:
        add(y1, x1, y2, x2, x): 矩形 [y1,y2)×[x1,x2) に x を加算予約する。
        build(): 全予約を反映した最終グリッドを返す。

    補足:
        多数の矩形更新をまとめて処理したいときに有効。

    使用例:
        imos = Imos2D(H, W)
        imos.add(y1, x1, y2, x2, 1)  # [y1,y2) × [x1,x2) に +1
        result = imos.build()
    """
    def __init__(self, h: int, w: int):
        self.h = h
        self.w = w
        self.diff = [[0] * (w + 1) for _ in range(h + 1)]

    def add(self, y1: int, x1: int, y2: int, x2: int, x: int = 1) -> None:
        """[y1, y2) × [x1, x2) に x を加算（0-indexed）"""
        self.diff[y1][x1] += x
        self.diff[y1][x2] -= x
        self.diff[y2][x1] -= x
        self.diff[y2][x2] += x

    def build(self) -> list[list[int]]:
        """累積和を計算して結果を返す"""
        # 横方向
        for i in range(self.h):
            for j in range(self.w):
                self.diff[i][j + 1] += self.diff[i][j]
        # 縦方向
        for j in range(self.w):
            for i in range(self.h):
                self.diff[i + 1][j] += self.diff[i][j]
        return [row[:self.w] for row in self.diff[:self.h]]


# ============================================================
# union-Find
# ============================================================

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


class WeightedDSU:
    """概要:
        ポテンシャル（重み差）付き Union-Find を提供するクラス。

    メソッド:
        merge(x, y, w): weight[x] - weight[y] = w を満たすように併合。
        diff(x, y): weight[x] - weight[y] を返す。
        same(x, y): 同一成分か判定する。
        leader(x), get_weight(x): 内部補助として重み情報を取得する。

    補足:
        差分制約の整合管理に使える。

    weight(x) - weight(y) = w となるような重みを管理
    使用例:
        wuf = WeightedDSU(n)
        wuf.merge(x, y, w)  # weight[x] - weight[y] = w
        diff = wuf.diff(x, y)  # weight[x] - weight[y]
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.weight = [0] * n  # 親への重み

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

    def diff(self, x: int, y: int) -> int:
        """weight[x] - weight[y] を返す"""
        return self.get_weight(x) - self.get_weight(y)

    def merge(self, x: int, y: int, w: int) -> bool:
        """weight[x] - weight[y] = w となるよう併合"""
        w += self.get_weight(y) - self.get_weight(x)
        x, y = self.leader(x), self.leader(y)
        if x == y: return False
        if self.rank[x] < self.rank[y]:
            x, y = y, x
            w = -w
        self.parent[y] = x
        self.weight[y] = -w
        self.rank[x] += self.rank[y]
        return True

    def same(self, x: int, y: int) -> bool:
        return self.leader(x) == self.leader(y)


# ============================================================
# グラフアルゴリズム
# ============================================================

def build_graph(n: int, edges: list[tuple[int, int]], directed: bool = False) -> list[list[int]]:
    """概要:
        辺集合から重みなしグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数（0-indexed を想定）。
        edges (list[tuple[int, int]]): 辺 (a, b) の配列。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[int]]: 隣接リスト。
    補足:
        無向時は両方向に辺を追加する。
    """
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a]. append(b)
        if not directed:
            g[b].append(a)
    return g

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

def multi_source_bfs(g: list[list[int]], sources: list[int]) -> list[int]:
    """概要:
        複数始点から同時に BFS を行い最短距離を求める。
    入力:
        g (list[list[int]]): 隣接リスト。
        sources (list[int]): 始点集合。
    出力:
        list[int]: 各頂点への最短距離。未到達は -1。
    補足:
        始点を距離0で同時投入することで最近始点への距離になる。
    """
    dist = [-1] * len(g)
    q = deque()
    for s in sources:
        if dist[s] == -1:
            dist[s] = 0
            q.append(s)
    while q:
        v = q.popleft()
        for to in g[v]:
            if dist[to] == -1:
                dist[to] = dist[v] + 1
                q.append(to)
    return dist

def bfs_grid(grid: list[list[str]], sy: int, sx: int, wall: str = '#') -> list[list[int]]:
    """概要:
        4近傍グリッド上で始点からの最短距離を BFS で求める。
    入力:
        grid (list[list[str]]): 盤面。
        sy, sx (int): 始点座標。
        wall (str): 通行不可セル文字。
    出力:
        list[list[int]]: 距離グリッド。未到達は -1。
    補足:
        `DIR4`（上下左右）を使用する。
    """
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

def zero_one_bfs(g: list[list[tuple[int, int]]], s: int) -> list[int]:
    """概要:
        辺重みが 0/1 のグラフで最短距離を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト（重みは0または1）。
        s (int): 始点。
    出力:
        list[int]: 各頂点への最短距離（未到達は INF）。
    補足:
        0重みは deque の前、1重みは後ろへ投入して O(V+E)。
    """
    dist = [INF] * len(g)
    dist[s] = 0
    q = deque([s])
    while q:
        v = q.popleft()
        for to, w in g[v]:
            nd = dist[v] + w
            if nd < dist[to]:
                dist[to] = nd
                if w == 0:
                    q.appendleft(to)
                else:
                    q.append(to)
    return dist

def bellman_ford(n: int, edges: list[tuple[int, int, int]], s: int) -> tuple[list[int], bool]:
    """概要:
        Bellman-Ford 法で最短距離と負閉路有無を求める。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
        s (int): 始点。
    出力:
        tuple[list[int], bool]: (距離配列, 負閉路が検出されたか)。
    補足:
        計算量は O(VE)。
    """
    dist = [INF] * n
    dist[s] = 0
    for i in range(n):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated: break
        if i == n - 1: return dist, True
    return dist, False

def warshall_floyd(n: int, edges: list[tuple[int, int, int]]) -> list[list[int]]:
    """概要:
        Warshall-Floyd 法で全点対最短距離を求める。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
    出力:
        list[list[int]]: dist[i][j] = i から j への最短距離。
    補足:
        計算量は O(V^3)。頂点数が小さいケース向け。
    """
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

def topological_sort(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフをトポロジカルソートする。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: トポロジカル順序。閉路があれば None。
    補足:
        Kahn 法（入次数管理）を使用する。
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

def detect_cycle(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフで1つの閉路を DFS により検出する。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: 閉路を構成する頂点列。なければ None。
    補足:
        色管理（未訪問/訪問中/訪問済）で後退辺を検出する。
    """
    n = len(g)
    color = [0] * n  # 0:未訪問, 1: 訪問中, 2:訪問済
    parent = [-1] * n
    cycle = []

    def dfs(v: int) -> bool:
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

def bipartite_coloring(g: list[list[int]]) -> tuple[bool, list[int]]:
    """概要:
        グラフが二部グラフか判定し、可能なら2彩色を返す。
    入力:
        g (list[list[int]]): 無向グラフの隣接リスト。
    出力:
        tuple[bool, list[int]]: (二部グラフか, 色配列)。
    補足:
        非連結グラフにも対応し、各連結成分を BFS で処理する。
    """
    n = len(g)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for to in g[v]:
                if color[to] == -1:
                    color[to] = color[v] ^ 1
                    q.append(to)
                elif color[to] == color[v]:
                    return False, color
    return True, color

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
        辺を重み昇順に処理し、DSUで閉路を回避する。
    """
    uf = DSU(n)
    cost = 0
    used = []
    for u, v, w in sorted(edges, key=lambda x: x[2]):
        if uf.merge(u, v):
            cost += w
            used.append((u, v, w))
    return cost, used, len(used) == n - 1


# ============================================================
# 木アルゴリズム
# ============================================================

def tree_diameter(g: list[list[int]]) -> tuple[int, int, int]:
    """概要:
        木の直径長とその端点2つを返す。
    入力:
        g (list[list[int]]): 木の隣接リスト。
    出力:
        tuple[int, int, int]: (直径長, 端点u, 端点v)。
    補足:
        BFS を2回行う定番手法を用いる。
    """
    def bfs_farthest(s: int) -> tuple[int, int]:
        dist = bfs(g, s)
        farthest = max(range(len(g)), key=lambda x: dist[x])
        return farthest, dist[farthest]

    u, _ = bfs_farthest(0)
    v, d = bfs_farthest(u)
    return d, u, v

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

def subtree_size(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木の各頂点について部分木サイズを求める。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: size[v] = v を根とする部分木サイズ。
    補足:
        深い頂点から親へサイズを集約する。
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


class LCA:
    """概要:
        ダブリング法で LCA（最小共通祖先）と頂点間距離を高速計算するクラス。

    メソッド:
        query(u, v): u と v の LCA を返す。
        dist(u, v): u-v 間の辺数距離を返す。

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


# ============================================================
# データ構造
# ============================================================

class BIT:
    """概要:
        1次元 Binary Indexed Tree（Fenwick Tree）を提供するクラス。

    メソッド:
        add(i, x): a[i] に x を加算する。
        sum(i): 区間 [0, i] の和を返す。
        range_sum(l, r): 区間 [l, r) の和を返す。
        lower_bound(w): 累積和が w 以上になる最小インデックスを返す。

    補足:
        すべて 0-indexed インターフェース。各操作は O(logN)。

    使用例:
        bit = BIT(n)
        bit.add(i, x)        # a[i] += x
        bit.sum(i)           # a[0] + ...  + a[i]
        bit.range_sum(l, r)  # a[l] + ... + a[r-1]
    """
    def __init__(self, n: int):
        self.n = n
        self.data = [0] * (n + 1)

    def add(self, i: int, x: int) -> None:
        i += 1
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i: int) -> int:
        """a[0] + ... + a[i]"""
        s = 0
        i += 1
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """a[l] + ... + a[r-1]"""
        if l >= r: return 0
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
    """概要:
        モノイド演算を扱う汎用 Segment Tree。

    メソッド:
        build(arr): 初期配列から構築する。
        set(i, v) / update(i, v): 1点更新を行う。
        get(i): 1点取得を行う。
        query(l, r): 区間 [l, r) の集約値を返す。
        all_query(): 全区間の集約値を返す。

    補足:
        `op` は結合的、`e` は単位元を与える。

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
        while self.size < n: self.size <<= 1
        self.data = [e] * (2 * self.size)

    def build(self, arr: list[int]) -> None:
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def set(self, i: int, v: int) -> None:
        """a[i] = v"""
        i += self.size
        self.data[i] = v
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def get(self, i: int) -> int:
        """a[i]を取得"""
        return self.data[self.size + i]

    def query(self, l: int, r: int) -> int:
        """[l, r) の演算結果"""
        sml = self.e
        smr = self.e
        l += self.size
        r += self.size
        while l < r:
            if l & 1:
                sml = self.op(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op(sml, smr)

    def all_query(self) -> int:
        """全区間の演算結果"""
        return self.data[1]

    update = set  # エイリアス


class LazySegTree:
    """概要:
        作用付きモノイドを扱う汎用遅延セグメント木（ACL風インターフェース）。

    メソッド:
        build(arr): 初期配列から木を構築する。
        set(p, x): 1点代入を行う。
        get(p): 1点値を取得する（必要な遅延伝播込み）。
        query(l, r): 区間 [l, r) の集約値を返す。
        apply(l, r, f): 区間 [l, r) に作用 f を適用する。

    補足:
        `op/e` は値側モノイド、`mapping/composition/identity` は作用側定義。
        区間更新・区間取得の典型問題を1つの器で実装できる。

    使用例（区間加算・点取得）:
        n = 10
        op = operator.add
        e = 0
        mapping = lambda f, x: x + f
        composition = lambda f, g: f + g
        identity = 0
        lst = LazySegTree(n, op, e, mapping, composition, identity)

    注意:
        上記の `mapping = lambda f, x: x + f` は「要素値」に作用を適用する形。
        区間和を持たせる場合は、値に区間長を含めるなどして
        `mapping` 側で長さ分を反映する設計にすること。
    """
    def __init__(
        self,
        n: int,
        op: Callable,
        e,
        mapping: Callable,
        composition: Callable,
        identity,
    ):
        self.n = n
        self.op = op
        self.e = e
        self.mapping = mapping
        self.composition = composition
        self.identity = identity
        self.log = max(1, (n - 1).bit_length())
        self.size = 1 << self.log
        self.data = [e] * (2 * self.size)
        self.lazy = [identity] * self.size

    def build(self, arr: list) -> None:
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self._update(i)

    def _update(self, k: int) -> None:
        self.data[k] = self.op(self.data[k << 1], self.data[k << 1 | 1])

    def _all_apply(self, k: int, f) -> None:
        self.data[k] = self.mapping(f, self.data[k])
        if k < self.size:
            self.lazy[k] = self.composition(f, self.lazy[k])

    def _push(self, k: int) -> None:
        if self.lazy[k] != self.identity:
            self._all_apply(k << 1, self.lazy[k])
            self._all_apply(k << 1 | 1, self.lazy[k])
            self.lazy[k] = self.identity

    def set(self, p: int, x) -> None:
        p += self.size
        for i in range(self.log, 0, -1):
            self._push(p >> i)
        self.data[p] = x
        for i in range(1, self.log + 1):
            self._update(p >> i)

    def get(self, p: int):
        p += self.size
        for i in range(self.log, 0, -1):
            self._push(p >> i)
        return self.data[p]

    def query(self, l: int, r: int):
        """[l, r) の演算結果"""
        if l >= r:
            return self.e
        l += self.size
        r += self.size
        for i in range(self.log, 0, -1):
            if ((l >> i) << i) != l:
                self._push(l >> i)
            if ((r >> i) << i) != r:
                self._push((r - 1) >> i)
        sml = self.e
        smr = self.e
        while l < r:
            if l & 1:
                sml = self.op(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op(sml, smr)

    def apply(self, l: int, r: int, f) -> None:
        """[l, r) に作用fを適用"""
        if l >= r:
            return
        l += self.size
        r += self.size
        l2, r2 = l, r
        for i in range(self.log, 0, -1):
            if ((l2 >> i) << i) != l2:
                self._push(l2 >> i)
            if ((r2 >> i) << i) != r2:
                self._push((r2 - 1) >> i)
        while l < r:
            if l & 1:
                self._all_apply(l, f)
                l += 1
            if r & 1:
                r -= 1
                self._all_apply(r, f)
            l >>= 1
            r >>= 1
        l, r = l2, r2
        for i in range(1, self.log + 1):
            if ((l >> i) << i) != l:
                self._update(l >> i)
            if ((r >> i) << i) != r:
                self._update((r - 1) >> i)


class BIT2:
    """概要:
        BITを2本使って「区間加算・区間和」を処理するクラス。

    メソッド:
        add_range(l, r, x): 区間 [l, r) へ x を加算する。
        range_sum(l, r): 区間 [l, r) の総和を返す。

    補足:
        内部的に一次関数係数を2本のBITで管理し、各操作 O(logN)。

    使用例:
        bit2 = BIT2(n)
        bit2.add_range(l, r, x)  # [l, r) に +x
        total = bit2.range_sum(l, r)
    """
    def __init__(self, n: int):
        self.n = n
        self.bit1 = [0] * (n + 1)
        self.bit2 = [0] * (n + 1)

    def _add(self, bit: list[int], i: int, x: int) -> None:
        while i <= self.n:
            bit[i] += x
            i += i & -i

    def _sum(self, bit: list[int], i: int) -> int:
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s

    def _prefix_sum(self, r: int) -> int:
        """[0, r) の和"""
        return self._sum(self.bit1, r) * r + self._sum(self.bit2, r)

    def add_range(self, l: int, r: int, x: int) -> None:
        """[l, r) に x を加算"""
        l += 1
        r += 1
        self._add(self.bit1, l, x)
        self._add(self.bit1, r, -x)
        self._add(self.bit2, l, -x * (l - 1))
        self._add(self.bit2, r, x * (r - 1))

    def range_sum(self, l: int, r: int) -> int:
        """[l, r) の和"""
        return self._prefix_sum(r) - self._prefix_sum(l)


class BIT2D:
    """概要:
        2次元 Binary Indexed Tree（2D Fenwick Tree）を提供するクラス。

    メソッド:
        add(y, x, v): 1点 (y, x) に v を加算する。
        range_sum(y1, x1, y2, x2): 矩形 [y1,y2)×[x1,x2) の和を返す。

    補足:
        各操作は O(logH * logW)。0-indexed の半開区間で扱う。

    使用例:
        bit = BIT2D(H, W)
        bit.add(y, x, v)                  # A[y][x] += v
        s = bit.range_sum(y1, x1, y2, x2) # [y1,y2) × [x1,x2)
    """
    def __init__(self, h: int, w: int):
        self.h = h
        self.w = w
        self.data = [[0] * (w + 1) for _ in range(h + 1)]

    def add(self, y: int, x: int, v: int) -> None:
        y += 1
        while y <= self.h:
            xx = x + 1
            while xx <= self.w:
                self.data[y][xx] += v
                xx += xx & -xx
            y += y & -y

    def _sum(self, y: int, x: int) -> int:
        """[0, y) × [0, x) の和"""
        s = 0
        yy = y
        while yy > 0:
            xx = x
            while xx > 0:
                s += self.data[yy][xx]
                xx -= xx & -xx
            yy -= yy & -yy
        return s

    def range_sum(self, y1: int, x1: int, y2: int, x2: int) -> int:
        """[y1, y2) × [x1, x2) の和"""
        return self._sum(y2, x2) - self._sum(y1, x2) - self._sum(y2, x1) + self._sum(y1, x1)


class SortedMultiset:
    """概要:
        平方分割で実装した順序付き重複集合クラス。

    メソッド:
        add(x), discard(x): 挿入・削除。
        __contains__(x): 存在判定。
        __getitem__(i): i 番目要素取得（負インデックス対応）。
        index(x), index_right(x): 順位取得（<x, <=x の個数）。

    補足:
        平均的に各操作は O(√N) 程度。標準ライブラリのみで運用可能。

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

    def __init__(self, a: list[int] = []):
        a = list(a)
        if a:
            a.sort()
        self._build(a)

    def _build(self, a: list[int]) -> None:
        self.a = a
        self.size = len(a)
        if self.size == 0:
            self.buckets = []
        else:
            bucket_size = int(math.ceil(math.sqrt(self.size / self.BUCKET_RATIO)))
            self.buckets = [a[i:i + bucket_size] for i in range(0, self.size, bucket_size)]

    def __len__(self) -> int:
        return self.size

    def __contains__(self, x: int) -> bool:
        if not self.buckets: return False
        for bucket in self.buckets:
            if bucket[0] <= x <= bucket[-1]:
                i = bisect_left(bucket, x)
                if i < len(bucket) and bucket[i] == x:
                    return True
        return False

    def add(self, x: int) -> None:
        if not self.buckets:
            self.buckets = [[x]]
            self.size = 1
            return
        for i, bucket in enumerate(self.buckets):
            if x <= bucket[-1] or i == len(self.buckets) - 1:
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
                    bucket.pop(i)
                    self.size -= 1
                    if not bucket:
                        self.buckets.remove(bucket)
                    return True
        return False

    def __getitem__(self, i: int) -> int:
        if i < 0: i += self.size
        for bucket in self.buckets:
            if i < len(bucket):
                return bucket[i]
            i -= len(bucket)
        raise IndexError

    def index(self, x: int) -> int:
        """x未満の要素数を返す"""
        cnt = 0
        for bucket in self.buckets:
            if x <= bucket[0]:
                return cnt
            if x > bucket[-1]:
                cnt += len(bucket)
            else:
                return cnt + bisect_left(bucket, x)
        return cnt

    def index_right(self, x: int) -> int:
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
# 文字列アルゴリズム
# ============================================================

class RollingHash:
    """概要:
        文字列の部分文字列比較を高速化するダブルローリングハッシュ。

    メソッド:
        get(l, r): 部分文字列 s[l:r] のハッシュ値ペアを返す。
        lcp(i, j): 位置 i, j からの最長共通接頭辞長を返す。

    補足:
        2つの法を使って衝突確率を低減している。

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
        self.pow1 = [1] * (self.n + 1)
        self.pow2 = [1] * (self.n + 1)
        for i in range(self.n):
            self.hash1[i + 1] = (self.hash1[i] * self.BASE1 + ord(s[i])) % self.MOD1
            self.hash2[i + 1] = (self.hash2[i] * self.BASE2 + ord(s[i])) % self.MOD2
            self.pow1[i + 1] = self.pow1[i] * self.BASE1 % self.MOD1
            self.pow2[i + 1] = self.pow2[i] * self.BASE2 % self.MOD2

    def get(self, l: int, r: int) -> tuple[int, int]:
        """[l, r) のハッシュ"""
        h1 = (self.hash1[r] - self.hash1[l] * self.pow1[r - l]) % self.MOD1
        h2 = (self.hash2[r] - self.hash2[l] * self.pow2[r - l]) % self.MOD2
        return (h1, h2)

    def lcp(self, i: int, j: int) -> int:
        """位置i, jから始まる最長共通接頭辞の長さ"""
        ok, ng = 0, min(self.n - i, self.n - j) + 1
        while ng - ok > 1:
            mid = (ok + ng) // 2
            if self.get(i, i + mid) == self.get(j, j + mid):
                ok = mid
            else:
                ng = mid
        return ok


def z_algorithm(s: str) -> list[int]:
    """概要:
        文字列 s の Z 配列を構築する。
    入力:
        s (str): 対象文字列。
    出力:
        list[int]: z[i] = s と s[i:] の最長共通接頭辞長。
    補足:
        文字列照合やパターン探索の前処理として O(|s|) で有効。
    """
    n = len(s)
    if n == 0:
        return []
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


def run_length_encode(s: str | list) -> list[tuple]:
    """概要:
        連続要素を (値, 連続数) に圧縮する。
    入力:
        s (str | list): 圧縮対象シーケンス。
    出力:
        list[tuple]: [(値, 連続数), ...]。
    補足:
        空入力は空配列を返す。
    """
    if not s: return []
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


class Trie:
    """概要:
        文字列集合を前方一致ベースで管理する Trie 木。

    内部クラス:
        Node: Trie の1ノードを表す。

    メソッド:
        insert(s): 文字列 s を登録する。
        search(s): 文字列 s が完全一致で登録済みか判定する。
        starts_with(prefix): 接頭辞 prefix を持つ語が存在するか判定する。
        count_prefix(prefix): 接頭辞 prefix を持つ登録語数を返す。
    """
    class Node:
        """概要:
            Trie の1ノードを表す内部クラス。

        属性:
            next (dict[str, Trie.Node]): 文字 -> 次ノードの辞書。
            end (int): このノードで終端となる単語数。
            cnt (int): このノードを通過する単語数。
        """
        __slots__ = ("next", "end", "cnt")

        def __init__(self):
            self.next: dict[str, "Trie.Node"] = {}
            self.end: int = 0
            self.cnt: int = 0

    def __init__(self):
        self.root = Trie.Node()

    def insert(self, s: str) -> None:
        node = self.root
        node.cnt += 1
        for ch in s:
            if ch not in node.next:
                node.next[ch] = Trie.Node()
            node = node.next[ch]
            node.cnt += 1
        node.end += 1

    def search(self, s: str) -> bool:
        node = self.root
        for ch in s:
            if ch not in node.next:
                return False
            node = node.next[ch]
        return node.end > 0

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.next:
                return False
            node = node.next[ch]
        return True

    def count_prefix(self, prefix: str) -> int:
        """prefixで始まる登録文字列数"""
        node = self.root
        for ch in prefix:
            if ch not in node.next:
                return 0
            node = node.next[ch]
        return node.cnt


def kmp_table(pattern: str) -> list[int]:
    """概要:
        KMP 法で使う prefix function（部分一致テーブル）を構築する。
    入力:
        pattern (str): パターン文字列。
    出力:
        list[int]: pi[i] = pattern[:i+1] の最長 proper prefix/suffix 長。
    補足:
        `kmp_search` の前処理として利用する。
    """
    n = len(pattern)
    pi = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            pi[i] = j
    return pi


def kmp_search(text: str, pattern: str) -> list[int]:
    """概要:
        KMP 法で text 内の pattern 出現開始位置を列挙する。
    入力:
        text (str): 検索対象文字列。
        pattern (str): 検索パターン。
    出力:
        list[int]: 出現開始インデックス一覧。
    補足:
        計算量は O(|text| + |pattern|)。空パターンは全位置一致として扱う。
    """
    if not pattern:
        return list(range(len(text) + 1))
    pi = kmp_table(pattern)
    res = []
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = pi[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            res.append(i - len(pattern) + 1)
            j = pi[j - 1]
    return res


def levenshtein_distance(s: str, t: str) -> int:
    """概要:
        文字列 s と t の編集距離（レーベンシュタイン距離）を求める。
    入力:
        s (str): 文字列1。
        t (str): 文字列2。
    出力:
        int: 挿入・削除・置換（各コスト1）で s を t に変換する最小操作回数。
    補足:
        計算量は O(|s|*|t|)、メモリは O(min(|s|,|t|))。
    """
    if len(s) < len(t):
        s, t = t, s
    n, m = len(s), len(t)
    if m == 0:
        return n

    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        si = s[i - 1]
        for j in range(1, m + 1):
            cost = 0 if si == t[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + cost,
            )
        prev = curr
    return prev[m]


# ============================================================
# 動的計画法（DP）
# ============================================================

def interval_dp_min(n: int, merge_cost: Callable[[int, int, int], int], base: int = 0, inf: int = INF) -> list[list[int]]:
    """概要:
        区間 DP（最小化）を行うための汎用テンプレート。
    入力:
        n (int): 要素数（区間 [0, n-1] を扱う）。
        merge_cost (Callable[[int, int, int], int]):
            遷移で区間 [l, r] を分割点 k で結合するときの追加コストを返す関数。
            値は `merge_cost(l, k, r)` で受け取る。
        base (int): 長さ1区間 dp[i][i] の初期値。
        inf (int): 十分大きい初期値。
    出力:
        list[list[int]]: dp テーブル。
            dp[l][r] = 区間 [l, r] を最適化した最小値（0 <= l <= r < n）。
    補足:
        遷移式は
            dp[l][r] = min(dp[l][k] + dp[k+1][r] + merge_cost(l, k, r))
        （l <= k < r）。
        計算量は O(n^3)（`merge_cost` を O(1) とした場合）。

    使用例:
        # 区間和をマージコストにする典型例
        # A の prefix sum を先に作っておく
        # ps = prefix_sum(A)
        # cost = lambda l, k, r: ps[r + 1] - ps[l]
        # dp = interval_dp_min(len(A), cost)
        # ans = dp[0][len(A) - 1]
    """
    if n <= 0:
        return []

    dp = [[inf] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = base

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            best = inf
            for k in range(l, r):
                cand = dp[l][k] + dp[k + 1][r] + merge_cost(l, k, r)
                if cand < best:
                    best = cand
            dp[l][r] = best
    return dp


# ============================================================
# 二分探索
# ============================================================

def binary_search_min(ng: int, ok: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最小 x を整数二分探索で求める。
    入力:
        ng (int): 条件を満たさない側の初期値。
        ok (int): 条件を満たす側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最小の値。
    補足:
        境界の妥当性（ng 側False, ok 側True）を事前に満たすこと。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

def binary_search_max(ok: int, ng: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最大 x を整数二分探索で求める。
    入力:
        ok (int): 条件を満たす側の初期値。
        ng (int): 条件を満たさない側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最大の値。
    補足:
        境界の妥当性（ok 側True, ng 側False）を事前に満たすこと。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

def binary_search_float(ok: float, ng: float, check: Callable[[float], bool], iterations: int = 100) -> float:
    """概要:
        実数領域で二分探索を反復回数固定で行う。
    入力:
        ok (float): 条件を満たす側の初期値。
        ng (float): 条件を満たさない側の初期値。
        check (Callable[[float], bool]): 判定関数（単調）。
        iterations (int): 反復回数。
    出力:
        float: 探索結果（近似解）。
    補足:
        精度は反復回数で調整する。
    """
    for _ in range(iterations):
        mid = (ok + ng) / 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok


def lis(arr: list[int], strict: bool = True) -> int:
    """概要:
        配列の最長増加部分列（LIS）の長さを求める。
    入力:
        arr (list[int]): 対象配列。
        strict (bool): True なら狭義増加、False なら広義増加。
    出力:
        int: LIS の長さ。
    補足:
        計算量は O(n log n)。復元は行わず長さのみ返す。
    """
    dp = []
    for x in arr:
        i = bisect_left(dp, x) if strict else bisect_right(dp, x)
        if i == len(dp):
            dp.append(x)
        else:
            dp[i] = x
    return len(dp)


# ============================================================
# 座標圧縮
# ============================================================

def compress(arr: list[int]) -> tuple[dict[int, int], list[int]]:
    """概要:
        配列値を連番インデックスへ写像する座標圧縮を行う。
    入力:
        arr (list[int]): 圧縮対象配列。
    出力:
        tuple[dict[int, int], list[int]]: (値→index辞書, 昇順ユニーク値リスト)。
    補足:
        元値への逆引きは第2戻り値を使う。
    """
    xs = sorted(set(arr))
    mp = {x: i for i, x in enumerate(xs)}
    return mp, xs

def compress_list(arr: list[int]) -> list[int]:
    """概要:
        配列を座標圧縮した後のインデックス配列を返す。
    入力:
        arr (list[int]): 圧縮対象配列。
    出力:
        list[int]: arr の各要素を圧縮インデックスへ変換した配列。
    補足:
        `compress` を内部利用する。
    """
    mp, _ = compress(arr)
    return [mp[x] for x in arr]


def inversion_count(arr: list[int]) -> int:
    """概要:
        配列の転倒数（i<j かつ arr[i]>arr[j] の組数）を求める。
    入力:
        arr (list[int]): 対象配列。
    出力:
        int: 転倒数。
    補足:
        座標圧縮 + BIT で O(n log n)。重複値にも対応。
    """
    if not arr:
        return 0
    c = compress_list(arr)
    n = len(c)
    bit = BIT(max(c) + 1)
    inv = 0
    for i, x in enumerate(c):
        leq = bit.sum(x)
        inv += i - leq
        bit.add(x, 1)
    return inv


# ============================================================
# ユーティリティ
# ============================================================

def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    """概要:
        2点間のマンハッタン距離を返す。
    入力:
        x1, y1, x2, y2 (int): 2点座標。
    出力:
        int: |x1-x2| + |y1-y2|。
    """
    return abs(x1 - x2) + abs(y1 - y2)

def chebyshev(x1: int, y1: int, x2: int, y2: int) -> int:
    """概要:
        2点間のチェビシェフ距離を返す。
    入力:
        x1, y1, x2, y2 (int): 2点座標。
    出力:
        int: max(|x1-x2|, |y1-y2|)。
    """
    return max(abs(x1 - x2), abs(y1 - y2))

def rank_data(arr: list, reverse: bool = False, competition: bool = True) -> list[int]:
    """概要:
        配列の各要素の順位を返す。
    入力:
        arr (list): 順位付けする配列。
        reverse (bool): True なら大きい順、False なら小さい順。
        competition (bool): True なら重複時に同順位（1, 2, 2, 4）、False なら（1, 2, 2, 3）。
    出力:
        list[int]: 各要素の順位（1-indexed）。
    補足:
        デフォルトは小さい順・重複同順位（競技順位）。
    """
    n = len(arr)
    if n == 0: return []
    
    # 元のインデックスと値を保持してソート
    indexed_arr = sorted(enumerate(arr), key=lambda x: x[1], reverse=reverse)
    
    ranks = [0] * n
    curr_rank = 1
    for i in range(n):
        if i > 0:
            if indexed_arr[i][1] == indexed_arr[i-1][1]:
                # 同値の場合
                if competition:
                    # 競技順位（1, 2, 2, 4）: そのまま
                    pass
                else:
                    # 密な順位（1, 2, 2, 3）: 前の順位を維持（更新しない）
                    pass
            else:
                # 異なる値の場合
                if competition:
                    curr_rank = i + 1
                else:
                    curr_rank += 1
        
        ranks[indexed_arr[i][0]] = curr_rank
        
    return ranks

def ceil_div(a: int, b: int) -> int:
    """概要:
        正整数同士の切り上げ除算を返す。
    入力:
        a (int): 被除数。
        b (int): 除数（正）。
    出力:
        int: ceil(a / b)。
    補足:
        想定は a, b > 0。
    """
    return (a + b - 1) // b

def floor_sum(n: int, m: int, a: int, b: int) -> int:
    """概要:
        Σ_{i=0}^{n-1} floor((a*i + b) / m) を高速に計算する。
    入力:
        n, m, a, b (int): 式のパラメータ。
    出力:
        int: 総和値。
    補足:
        ACL由来の再帰的変形を使い O(log m + log a) 程度で処理する。
    """
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

def rotate_90(grid: list[list]) -> list[list]:
    """概要:
        2次元配列を時計回りに90度回転して返す。
    入力:
        grid (list[list]): 元グリッド。
    出力:
        list[list]: 回転後グリッド。
    """
    H, W = len(grid), len(grid[0])
    return [[grid[H - 1 - j][i] for j in range(H)] for i in range(W)]

def transpose(grid: list[list]) -> list[list]:
    """概要:
        2次元配列の転置を返す。
    入力:
        grid (list[list]): 元グリッド。
    出力:
        list[list]: 転置後グリッド。
    """
    return [list(row) for row in zip(*grid)]


def bit_full_search(n: int):
    """概要:
        n 要素集合の部分集合をビットマスクで全列挙するジェネレータ。
    入力:
        n (int): 要素数。
    出力:
        Iterator[int]: 0 から (1<<n)-1 のビットマスク。
    補足:
        `for bit in bit_full_search(n):` で利用する。
    """
    for bit in range(1 << n):
        yield bit


def bit_indices(bit: int, n: int) -> list[int]:
    """概要:
        ビットマスクで立っているビット位置を列挙する。
    入力:
        bit (int): ビットマスク。
        n (int): 判定するビット長。
    出力:
        list[int]: 立っている位置（0-indexed）の配列。
    """
    return [i for i in range(n) if (bit >> i) & 1]


def submasks(mask: int):
    """概要:
        与えたマスクの全部分マスクを降順で列挙するジェネレータ。
    入力:
        mask (int): 元マスク。
    出力:
        Iterator[int]: mask, ..., 0 の順で全部分マスク。
    補足:
        `s = (s - 1) & mask` の定番テクニックを使用する。
    """
    s = mask
    while True:
        yield s
        if s == 0:
            break
        s = (s - 1) & mask

# ============================================================
# 記録して出力
# ============================================================

class Output:
    """概要:
        出力文字列をバッファリングして最後にまとめて出力する補助クラス。

    メソッド:
        add(*args, sep=' '): 1行分を追加する。
        extend(iterable): 要素列を複数行として追加する。
        grid(grid, sep=' '): 2次元配列を行単位で追加する。
        yes(cond, yes='Yes', no='No'): 条件に応じた文字列を追加する。
        flush(...): まとめて出力しバッファをクリアする。
        get(sep='\n'): 現在バッファを文字列として取得する。

    補足:
        大量出力時の `print` 連打を避けたいときに有効。
    """
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

    def grid(self, grid: list[list], sep: str = ' ') -> None:
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

def print_grid(grid: list[list], sep: str = '') -> None:
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
    N = INT()
    print(ans)


if __name__ == "__main__":
    main()