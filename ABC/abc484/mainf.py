# AtCoder Competition Template v2.4.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/.template/main.py
# ALL: https://github.com/Rino-program/atcoder/blob/main/.template/template.py

import os, sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
from bisect import bisect_left, bisect_right
from copy import deepcopy
import operator
import heapq
import math
import string

# ===== JIT 設定・制限解除 =====
# 深い再帰のアンロールを無効化 (実測で約8.9倍高速 TLE/MLE防止)
try:
    import pypyjit
    pypyjit.set_param('max_unroll_recursion=-1')
except ImportError:
    pass
# 再帰深度の上限引き上げ
sys.setrecursionlimit(2*10**6)
# 巨大整数の文字列変換エラーを防止
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

# ===== 入力ヘルパ =====
input = lambda: sys.stdin.readline().rstrip("\n")
INT = lambda: int(input())
INT0 = lambda: int(input()) - 1
MAP = lambda: map(int, input().split())
MAP0 = lambda: (int(x) - 1 for x in input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: [int(x) - 1 for x in input().split()]
TUPLE = lambda: tuple(map(int, input().split()))
TUPLE0 = lambda: tuple(int(x) - 1 for x in input().split())
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
LISTS0 = lambda n: [[int(x) - 1 for x in input().split()] for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
TUPLES0 = lambda n: [tuple(int(x) - 1 for x in input().split()) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
LISTSI0 = lambda n: [int(input()) - 1 for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

# ===== 高速 print =====
def print(*args, sep=' ', end='\n', file=None, flush=False):
    file = file or sys.stdout
    sep = ' ' if sep is None else sep
    end = '\n' if end is None else end
    file.write(sep.join(map(str, args)) + end)
    flush and file.flush()

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

# ===== 方向ベクトル(上(負)から時計回り) =====
DIR4 = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIR8 = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
DIR9 = DIR8 + ((0, 0),) # 中央は最後

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
Yes = lambda **kwargs: print("Yes", **kwargs)
No = lambda **kwargs: print("No", **kwargs)
yes = lambda **kwargs: print("yes", **kwargs)
no = lambda **kwargs: print("no", **kwargs)
YES = lambda **kwargs: print("YES", **kwargs)
NO = lambda **kwargs: print("NO", **kwargs)

def yn(cond: bool, yes: str = "Yes", no: str = "No", **kwargs) -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no, **kwargs)

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    print('\n'.join(sep.join(map(str, row)) for row in grid))

# ===== デバッグ =====
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, sep=' ', end='\n', flush=False) -> None:
        """デバッグ出力 (標準エラー) """
        print("[DEBUG]", *args, sep=sep, end=end, file=sys.stderr, flush=flush)
else:
    def debug(*args, **kwargs) -> None:
        pass

# ===== template.py より引用コード =====
from collections.abc import Callable, Sequence
from typing import Any
import operator
class SegTree:
    """概要:
        モノイド演算を扱う汎用 Segment Tree。

    メソッド:
        build(arr): 初期配列から構築する。
        set(i, v) / update(i, v): 1点更新を行う。
        get(i): 1点取得を行う。
        query(l, r): 区間 [l, r) の集約値を返す。
        max_right(l, f): [l, r) の集約が条件 f を満たす最大の r を返す。
        min_left(r, f): [l, r) の集約が条件 f を満たす最小の l を返す。
        all_query(): 全区間の集約値を返す。

    計算量:
        初期化(配列指定)/build は O(N)、set/update/get/query/max_right/min_left は O(logN)、all_query は O(1)。

    補足:
        `op` は結合的、`e` は単位元を与える。

    使用例:
        # 配列から初期化
        arr = [1, 2, 3, 4, 5]
        st = SegTree(arr, op=operator.add, e=0)

        # 要素数から初期化
        st = SegTree(5, op=min, e=float("inf"))
    """

    def __init__(
        self,
        n_or_arr: int | Sequence[Any],
        op: Callable[[Any, Any], Any] = operator.add,
        e: Any = 0,
    ):
        self.op = op
        self.e = e

        if isinstance(n_or_arr, int):
            self.n = n_or_arr
            self.size = 1
            while self.size < self.n:
                self.size <<= 1
            self.data = [e] * (2 * self.size)
        else:
            self.n = len(n_or_arr)
            self.size = 1
            while self.size < self.n:
                self.size <<= 1
            self.data = [e] * (2 * self.size)
            self.build(n_or_arr)

    def build(self, arr: Sequence[Any]) -> None:
        """初期配列から構築する (O(N))"""
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def set(self, i: int, v: Any) -> None:
        """a[i] = v"""
        if not 0 <= i < self.n:
            raise IndexError("index out of range")
        i += self.size
        self.data[i] = v
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def get(self, i: int) -> Any:
        """a[i]を取得"""
        if not 0 <= i < self.n:
            raise IndexError("index out of range")
        return self.data[self.size + i]

    def query(self, l: int, r: int) -> Any:
        """[l, r) の演算結果"""
        if not (0 <= l <= r <= self.n):
            raise ValueError("query range out of bounds")
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

    def max_right(self, l: int, f: Callable[[Any], bool]) -> int:
        """最大の r を返す（f(query(l, r)) が True）"""
        if l == self.n:
            return self.n
        if not 0 <= l <= self.n:
            raise ValueError("index out of range")
        if not f(self.e):
            raise ValueError("predicate must accept the identity")

        l += self.size
        sm = self.e
        while True:
            while l % 2 == 0:
                l >>= 1
            nxt = self.op(sm, self.data[l])
            if not f(nxt):
                while l < self.size:
                    l <<= 1
                    nxt = self.op(sm, self.data[l])
                    if f(nxt):
                        sm = nxt
                        l += 1
                return l - self.size
            sm = nxt
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r: int, f: Callable[[Any], bool]) -> int:
        """最小の l を返す（f(query(l, r)) が True）"""
        if r == 0:
            return 0
        if not 0 <= r <= self.n:
            raise ValueError("index out of range")
        if not f(self.e):
            raise ValueError("predicate must accept the identity")

        r += self.size
        sm = self.e
        while True:
            r -= 1
            while r > 1 and r % 2:
                r >>= 1
            nxt = self.op(self.data[r], sm)
            if not f(nxt):
                while r < self.size:
                    r = (r << 1) | 1
                    nxt = self.op(self.data[r], sm)
                    if f(nxt):
                        sm = nxt
                        r -= 1
                return r + 1 - self.size
            sm = nxt
            if (r & -r) == r:
                break
        return 0

    def all_query(self) -> Any:
        """全区間の演算結果"""
        return self.data[1]

    update = set  # エイリアス
# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, Q = MAP()
    A = LIST()
    def op(X, Y):
        ans = -1
        if X == Y == -1:
            ans = -1
        elif X == -1:
            ans = Y
        elif Y == -1:
            ans = X
        elif X == Y:
            ans = X
        else:
            ans = INF
        return ans
    seg = SegTree(A, op=op, e=-1)
    ans = []
    for _ in range(Q):
        i, x, y = MAP()
        if i == 1:
            seg.set(x-1, y)
        else:
            #debug(seg.query(x-1, y))
            ans.append("Yes" if seg.query(x-1, y) != INF else "No")
    print(*ans)





















if __name__ == "__main__":
    main()
