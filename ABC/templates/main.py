import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from itertools import permutations, combinations, accumulate, product
from functools import lru_cache
from typing import List, Tuple, Optional

sys.setrecursionlimit(10 ** 7)  # PyPy での再帰制限緩和

# PyPy3 推奨: `pypy3 main.py < input.txt` の形式で入出力のみを扱います。

def input() -> str:
    return sys.stdin.readline().rstrip()


# ===== よく使うヘルパ =====
def INT() -> int: return int(input())
def MAP(): return map(int, input().split())
def LIST(): return list(MAP())
def STR() -> str: return input()

INF = 10 ** 18
MOD = 998244353  # AtCoderで最頻出、必要に応じて 10**9+7 に変更

DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def lcm(a: int, b: int) -> int:
    # Python 3.9+ では math.lcm(a, b) を使用可能
    return a // math.gcd(a, b) * b


def compress(arr):
    xs = sorted(set(arr))
    index = {x: i for i, x in enumerate(xs)}
    return index, xs


class DSU:
    def __init__(self, n: int = 0):
        self.init(n)

    def init(self, n: int) -> None:
        self.parent = list(range(n))
        self.size = [1] * n
        self.n = n

    def leader(self, x: int) -> int:
        if self.parent[x] == x:
            return x
        self.parent[x] = self.leader(self.parent[x])  # 経路圧縮
        return self.parent[x]

    def merge(self, a: int, b: int) -> bool:
        a = self.leader(a)
        b = self.leader(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return True

    def same(self, a: int, b: int) -> bool:
        return self.leader(a) == self.leader(b)

    def component_size(self, x: int) -> int:
        return self.size[self.leader(x)]
    
    def groups(self) -> List[List[int]]:
        groups = defaultdict(list)
        for i in range(self.n):
            groups[self.leader(i)].append(i)
        return list(groups.values())


def bfs_graph(g, s: int):
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


def dijkstra(g, s: int):
    dist = [INF] * len(g)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d != dist[v]:
            continue
        for to, w in g[v]:
            nd = d + w
            if nd < dist[to]:
                dist[to] = nd
                heapq.heappush(pq, (nd, to))
    return dist


def dfs_graph(g, s: int, visited=None):
    """グラフのDFS探索"""
    if visited is None:
        visited = [False] * len(g)
    visited[s] = True
    result = [s]
    for to in g[s]:
        if not visited[to]:
            result.extend(dfs_graph(g, to, visited))
    return result


def topological_sort(g):
    """トポロジカルソート (閉路がある場合はNone)"""
    n = len(g)
    in_degree = [0] * n
    for v in range(n):
        for to in g[v]:
            in_degree[to] += 1
    
    q = deque([i for i in range(n) if in_degree[i] == 0])
    result = []
    
    while q:
        v = q.popleft()
        result.append(v)
        for to in g[v]:
            in_degree[to] -= 1
            if in_degree[to] == 0:
                q.append(to)
    
    return result if len(result) == n else None

# ===== 定番構造 (必要なら使用) =====

class BIT:
    """Fenwick Tree (0-index) : 点加算 / 区間和"""
    def __init__(self, n: int):
        self.n = n
        self.bit = [0] * (n + 1)
    def add(self, i: int, x: int):
        i += 1
        while i <= self.n:
            self.bit[i] += x
            i += i & -i
    def sum(self, i: int) -> int:  # [0,i]
        s = 0
        i += 1
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s
    def range_sum(self, l: int, r: int) -> int:  # [l,r)
        if r <= l: return 0
        return self.sum(r - 1) - (self.sum(l - 1) if l else 0)

class SegTree:
    """Segment Tree (range sum, point update)"""
    def __init__(self, n: int):
        self.N = 1
        while self.N < n:
            self.N <<= 1
        self.seg = [0] * (2 * self.N)
    def build(self, arr):  # arr 長さ <= n
        for i, v in enumerate(arr):
            self.seg[self.N + i] = v
        for i in range(self.N - 1, 0, -1):
            self.seg[i] = self.seg[i << 1] + self.seg[i << 1 | 1]
    def update(self, i: int, v: int):  # a[i]=v
        p = self.N + i
        self.seg[p] = v
        p >>= 1
        while p:
            self.seg[p] = self.seg[p << 1] + self.seg[p << 1 | 1]
            p >>= 1
    def query(self, l: int, r: int) -> int:  # [l,r)
        res = 0
        l += self.N; r += self.N
        while l < r:
            if l & 1:
                res += self.seg[l]; l += 1
            if r & 1:
                r -= 1; res += self.seg[r]
            l >>= 1; r >>= 1
        return res


class RMQSegTree:
    """Range Minimum Query Segment Tree"""
    def __init__(self, n: int):
        self.N = 1
        while self.N < n:
            self.N <<= 1
        self.seg = [INF] * (2 * self.N)
    
    def build(self, arr):
        for i, v in enumerate(arr):
            self.seg[self.N + i] = v
        for i in range(self.N - 1, 0, -1):
            self.seg[i] = min(self.seg[i << 1], self.seg[i << 1 | 1])
    
    def update(self, i: int, v: int):
        p = self.N + i
        self.seg[p] = v
        p >>= 1
        while p:
            self.seg[p] = min(self.seg[p << 1], self.seg[p << 1 | 1])
            p >>= 1
    
    def query(self, l: int, r: int) -> int:  # [l,r)
        res = INF
        l += self.N; r += self.N
        while l < r:
            if l & 1:
                res = min(res, self.seg[l]); l += 1
            if r & 1:
                r -= 1; res = min(res, self.seg[r])
            l >>= 1; r >>= 1
        return res


class RollingHash:
    """ローリングハッシュ (文字列)"""
    MOD1 = 10**9 + 7
    MOD2 = 10**9 + 9
    BASE1 = 1007
    BASE2 = 2009
    
    def __init__(self, s: str):
        self.n = len(s)
        self.s = s
        self.hash1 = [0] * (self.n + 1)
        self.hash2 = [0] * (self.n + 1)
        self.pow1 = [1] * (self.n + 1)
        self.pow2 = [1] * (self.n + 1)
        
        for i in range(self.n):
            self.hash1[i + 1] = (self.hash1[i] * self.BASE1 + ord(s[i])) % self.MOD1
            self.hash2[i + 1] = (self.hash2[i] * self.BASE2 + ord(s[i])) % self.MOD2
            self.pow1[i + 1] = self.pow1[i] * self.BASE1 % self.MOD1
            self.pow2[i + 1] = self.pow2[i] * self.BASE2 % self.MOD2
    
    def get(self, l: int, r: int) -> Tuple[int, int]:  # [l, r)
        h1 = (self.hash1[r] - self.hash1[l] * self.pow1[r - l]) % self.MOD1
        h2 = (self.hash2[r] - self.hash2[l] * self.pow2[r - l]) % self.MOD2
        return (h1, h2)

def prefix_sum(arr):
    ps = [0]
    for x in arr: ps.append(ps[-1] + x)
    return ps  # ps[r]-ps[l] が [l,r) の和

def sieve(n: int):
    is_prime = [True] * (n + 1)
    if n >= 0: is_prime[0] = False
    if n >= 1: is_prime[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if is_prime[p]:
            step = p
            start = p * p
            for q in range(start, n + 1, step):
                is_prime[q] = False
    primes = [i for i in range(2, n + 1) if is_prime[i]]
    return is_prime, primes


# ===== 追加の実用関数 =====

def pow_mod(x: int, n: int, mod: int = MOD) -> int:
    """高速べき乗 (mod付き)"""
    res = 1
    x %= mod
    while n > 0:
        if n & 1:
            res = (res * x) % mod
        x = (x * x) % mod
        n >>= 1
    return res

def mod_inverse(a: int, mod: int = MOD) -> int:
    """逆元計算 (mod が素数の場合)"""
    return pow_mod(a, mod - 2, mod)

def factorials(n: int, mod: int = MOD) -> Tuple[List[int], List[int]]:
    """階乗とその逆元のテーブル作成"""
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = (fact[i-1] * i) % mod
    
    inv_fact = [1] * (n + 1)
    inv_fact[n] = mod_inverse(fact[n], mod)
    for i in range(n - 1, 0, -1):
        inv_fact[i] = (inv_fact[i + 1] * (i + 1)) % mod
    
    return fact, inv_fact

def nCr(n: int, r: int, fact: List[int], inv_fact: List[int], mod: int = MOD) -> int:
    """組み合わせ計算 (事前計算済みテーブル使用)"""
    if r < 0 or r > n:
        return 0
    return (fact[n] * inv_fact[r] % mod) * inv_fact[n-r] % mod

def binary_search(ok: int, ng: int, check) -> int:
    """二分探索: check(mid) が True になる最大値を返す"""
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok


# ===== デバッグ支援 =====
def debug(*args):
    """デバッグ用出力 (標準エラーに出力)"""
    import sys
    print(*args, file=sys.stderr)


def print_grid(grid):
    """2次元配列を見やすく表示"""
    for row in grid:
        print(''.join(map(str, row)))


def main() -> None:
    # N = INT()
    # A = LIST()
    # print(sum(A))
    pass


if __name__ == "__main__":
    main()