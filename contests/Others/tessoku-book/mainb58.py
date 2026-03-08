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

class LazySegTree:
    from collections.abc import Callable
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

def main() -> None:
    # ここに解答を書く
    N, L, R = MAP()
    X = LIST()
    seg = LazySegTree(N, min, INF, lambda f, x: min(x, f), lambda f, g: min(f, g), INF)
    seg.set(0, 0)
    for i in range(N):
        l = bisect_left(X, X[i] - R)
        r = bisect_right(X, X[i] - L)
        if l < r:
            best = seg.query(l, r)
            if best != INF:
                seg.set(i, best + 1)
    print(seg.get(N - 1))

















if __name__ == "__main__":
    main()