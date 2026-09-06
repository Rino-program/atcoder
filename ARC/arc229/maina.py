# coding: utf-8
# AtCoder Competition Template v2.2 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py &template.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a

import sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
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

# ===== template.py =====

# ==============================================
# =================== main =====================
# ==============================================

def main(N: int) -> int:
    # ここに解答を書く
    if N == 0:
        print("A")
        return 1
    else:
        ans_li = []
        now = 0
        while N > now:
            ans_li.append(deque(["A", "R", "C"]))
            now += 1
            tmp = 3
            hukasa = 0
            while now+tmp <= N:
                now += tmp
                hukasa += 1
                tmp += 2
            for i in range(hukasa):
                ans_li[-1].appendleft("R")
                ans_li[-1].appendleft("A")
                ans_li[-1].append("R")
                ans_li[-1].append("C")
            for i in range((N-now)//(hukasa+1)):
                ans_li[-1].append("R")
                ans_li[-1].append("C")
                now += hukasa+1
    ans = []
    #debug(ans_li)
    for i in range(len(ans_li)):
        for j in range(len(ans_li[i])):
            ans.append(ans_li[i].popleft())
    S = "".join(ans)
    print("S:", S)
    # 判定
    A = 0
    while "ARC" in S:
        S = S.replace("ARC", "CRA", 1)
        A += 1
    print("回数:", A == N, "長さ:",  len(S) <= 100)
    print("回数:", A)
    print("A"*100, "長さ100の目安")
    return len(S)





















if __name__ == "__main__":
    """m = 600
    ma = 0
    tmp = 0
    for i in range(m+1):
        ans = main(i)
        if ma < ans:
            tmp = i
            ma = ans
    print(tmp, ma)"""
    N = INT()
    main(N)
    """now = 1
    hukasa = 0
    tmp = 3
    while now < 600:
        hukasa += 1
        now += tmp
        tmp += 2
    print(hukasa)"""
