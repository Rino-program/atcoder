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

def bit_full_search(n: int):
    """概要:
        n 要素集合の部分集合をビットマスクで全列挙するジェネレータ。
    入力:
        n (int): 要素数。
    出力:
        Iterator[int]: 0 から (1<<n)-1 のビットマスク。
    補足:
        `for bit in bit_full_search(n):` で利用する。全列挙の計算量は O(2^n)。
    """
    for bit in range(1 << n):
        yield bit


def bit_indices(bit: int, n: int) -> list[int]:
    """概要:
        ビットマスクで立っているビット位置を列挙する。
    入力:
        bit (int): ビットマスク。
        n (int): 判定するビット長。
    出力:
        list[int]: 立っている位置（0-indexed）の配列。
    補足:
        計算量は O(n)。
    """
    return [i for i in range(n) if (bit >> i) & 1]

def f(now: int, to: int):
    if now < 0:
        if to > 0:
            return 1
        else:
            return 0
    else:
        if to < 0:
            return 1
        else:
            return 0

def main() -> None:
    # ここに解答を書く
    N = INT()
    L = LIST()
    ans = 0
    for bit in bit_full_search(N):
        now = 0.5
        bit = set(bit_indices(bit, N))
        anstmp = 0
        for i in range(N):
            if i in bit:
                anstmp += f(now, now + L[i])
                now += L[i]
            else:
                anstmp += f(now, now - L[i])
                now -= L[i]
        ans = max(ans, anstmp)
    print(ans)





















if __name__ == "__main__":
    main()