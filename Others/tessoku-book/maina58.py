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

class SegTree:
    from collections.abc import Callable
    import operator
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

def main() -> None:
    # ここに解答を書く
    N, Q = MAP()
    st = SegTree(N, op=max, e=-INF)
    li = [0] * N
    st.build(li)
    for _ in range(Q):
        t, pos, x = MAP()
        if t == 1:
            st.set(pos - 1, x)
        else:
            print(st.query(pos - 1, x - 1))





















if __name__ == "__main__":
    main()