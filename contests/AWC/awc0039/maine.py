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

def main() -> None:
    # ここに解答を書く
    N, M, Q, K = MAP()
    SD = TUPLES(M)
    LRT = TUPLES(Q)
    TILR = sorted([(T, i, L, R) for i, (L, R, T) in en(LRT)])
    ans = [0] * Q
    DS = sorted([(d, s-1) for s, d in SD])
    bit = BIT(N)
    for i in range(Q):
        T, I, L, R = TILR.pop()
        while DS and DS[-1][0] >= T:
            _, i = DS.pop()
            bit.add(i, 1)
        ans[I] = max(0, bit.range_sum(L-1, R)-K)
    pr(*ans, sep="\n")





















if __name__ == "__main__":
    main()