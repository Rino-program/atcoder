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

def main():
    N, Q = MAP()
    S = STR()
    rh = RollingHash(S)
    for _ in range(Q):
        a, b, c, d = MAP()
        a -= 1; b -= 1; c -= 1; d -= 1
        yn(rh.get(a, b + 1) == rh.get(c, d + 1))





















if __name__ == "__main__":
    main()