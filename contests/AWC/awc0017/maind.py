# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
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
    return sys.stdin.readline().rstrip()

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
        `for bit in bit_full_search(n):` で利用する。
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
    """
    return [i+1 if (bit >> i) & 1 else 0 for i in range(n)]

def main() -> None:
    # ここに解答を書く
    N, M, K = MAP()
    A = LIST()
    UVB = LISTS(M)
    d = defaultdict(int)
    ans = [-INF, None]
    for U, V, B in UVB:
        d[str(U)+"_"+str(V)] = B
    for bit in bit_full_search(N):
        tmp = [None, 0]
        tmp[0] = bit_indices(bit, N)
        if tmp[0].count(0) != N-K: continue
        for i in tmp[0]:
            if i: tmp[1] += A[i-1]
        for i in range(len(tmp[0])-1):
            if tmp[0][i] == 0: continue
            for j in range(i+1, len(tmp[0])):
                if tmp[0][j] == 0: continue
                if d[str(i+1)+"_"+str(j+1)] != 0:
                    tmp[1] -= d[str(i+1)+"_"+str(j+1)]
        if ans[0] <= tmp[1]:
            ans[1] = tmp[0]
        ans[0] = max(ans[0], tmp[1])
    print(ans[0])





















if __name__ == "__main__":
    main()