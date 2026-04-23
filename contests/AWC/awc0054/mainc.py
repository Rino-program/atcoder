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

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    S = LIST()
    LRW = TUPLES(M)
    bit = BIT2(N)
    for l, r, w in LRW:
        bit.add_range(l-1, r, w)
    ans = 0
    for i, s in en(S):
        if s < bit.range_sum(i, i+1):
            ans += 1
    print(ans)





















if __name__ == "__main__":
    main()