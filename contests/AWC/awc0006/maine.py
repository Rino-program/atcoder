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

# ===== デバッグ =====

def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

def print_grid(grid:  list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))

def yn(cond: bool) -> None:
    """条件に応じてYes/No出力"""
    print("Yes" if cond else "No")


# ==============================================
# =================== main =====================
# ==============================================

class BIT:
    """Binary Indexed Tree (Fenwick Tree) 0-indexed
    
    使用例:
        bit = BIT(n)
        bit.add(i, x)        # a[i] += x
        bit. sum(i)           # a[0] + ...  + a[i]
        bit.range_sum(l, r)  # a[l] + ... + a[r-1]
    """
    def __init__(self, n:  int):
        self.n = n
        self.data = [0] * (n + 1)

    def add(self, i: int, x: int) -> None:
        i += 1
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i:  int) -> int:
        """a[0] + ... + a[i]"""
        s = 0
        i += 1
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """a[l] + ... + a[r-1]"""
        if l >= r:  return 0
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

# AIとの解説でAC
def main() -> None:
    N, Q = MAP()
    S = LIST()
    
    # BITの初期化
    bit = BIT(N)
    for i in range(N):
        bit.add(i, S[i])
        # その手があったか。
    for _ in range(Q):
        query = LIST()
        t = query[0]
        
        if t == 1:
            # タイプ 1：店舗番号 L 以上 R 以下の合計
            l, r = query[1], query[2]
            # 1-indexed [L, R] -> 0-indexed [L-1, R-1]
            # range_sum(L-1, R) はインデックス [L-1, R) の和を返す
            print(bit.range_sum(l - 1, r))
        else:
            # タイプ 2：店舗 X の売上を V に上書き
            x, v = query[1], query[2]
            idx = x - 1
            # BITは「加算」なので、(新しい値 - 現在の値) を足すことで「上書き」を実現する
            diff = v - S[idx]
            bit.add(idx, diff)
            # 現在の値を更新しておく
            S[idx] = v






















if __name__ == "__main__":
    main()