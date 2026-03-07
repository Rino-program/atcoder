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
MOD = 10**9 + 7

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

def main() -> None:
    # ここに解答を書く
    H, W = MAP()
    c = Combination(H+W)
    print(c.nCr(H+W-2, H-1)%MOD)





















if __name__ == "__main__":
    main()