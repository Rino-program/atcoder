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

class Imos2D:
    """2次元いもす法（0-indexed 半開区間）

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

def main() -> None:
    # ここに解答を書く
    H, W, N = MAP()
    imos = Imos2D(H, W)
    for i in range(N):
        A, B, C, D = MAP()
        imos.add(A-1, B-1, C, D, 1)
    print_grid(imos.build(), sep=" ")
    # oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina09.py' -d input/a09





















if __name__ == "__main__":
    main()