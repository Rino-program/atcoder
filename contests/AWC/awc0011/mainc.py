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

def main() -> None:
    # ここに解答を書く
    N, K = MAP()
    A = LIST()
    s1 = set()
    s2 = set()
    s3 = set()
    A1 = A[:N//3]
    A2 = A[N//3:(N//3)*2+1]
    A3 = A[(N//3)*2+1:]
    debug(A1, A2, A3)
    N1 = len(A1)
    for i in range(2**N1):
        tmp = 0
        for j in range(N1):
            if ((i>>j)&1):
                tmp |= A1[j]
        s1.add(tmp)
    #print(s1)
    s2 = set()
    N2 = len(A2)
    for i in range(2**N2):
        tmp = 0
        for j in range(N2):
            if ((i>>j)&1):
                tmp |= A2[j]
        s2.add(tmp)
    s3 = set()
    N3 = len(A3)
    for i in range(2**N3):
        tmp = 0
        for j in range(N3):
            if ((i>>j)&1):
                tmp |= A3[j]
        s3.add(tmp)
    """print(A1, s1)
    print(A2, s2)
    print(A3, s3)"""
    s1, s2, s3 = list(s1), list(s2), list(s3)
    ans = []
    for i in s1:
        for j in s2:
            for k in s3:
                if i|j|k == K:
                    ans.append((i, j, k))
    debug(ans)





















if __name__ == "__main__":
    main()