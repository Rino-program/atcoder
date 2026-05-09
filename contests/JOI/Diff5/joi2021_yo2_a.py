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

import random
def f(N: int) -> (int, str, int):
    li = ["X"] + [random.choice(["#", "."]) for _ in range(N)] + ["X"]
    s = random.randint(1, N-1)
    li[s] = "."
    limit = 1
    if li.count("#") <= limit:
        while li.count("#") <= limit:
            li = ["X"] + [random.choice(["#", "."]) for _ in range(N)] + ["X"]
            s = random.randint(1, N-1)
            li[s] = "."
    temp = li[:]
    # 愚直解
    now = s
    ans = 0
    muki = 0
    while "#" in li:
        ans += 1
        if muki == 0:
            now += 1
            if li[now] == "#" or li[now] == "X":
                if li[now] == "#":
                    li[now] = "."
                muki ^= 1
        else:
            now -= 1
            if li[now] == "#" or li[now] == "X":
                if li[now] == "#":
                    li[now] = "."
                muki ^= 1
    return ans, "".join(temp[1:-1]), s

def main() -> None:
    # ここに解答を書く
    N, A = MAP()
    S = STR()
    li = []
    for i in range(N):
        if S[i] == "#":
            li.append(i+1)
    lr = bil(li, A)
    lli, rli = li[:lr], li[lr:][::-1]
    f = 0
    now = A
    ans = 0
    while lli or rli:
        if f == 1:
            if lli:
                ans += abs(now - lli[-1])
                now = lli.pop()
            else:
                ans += now
                now = 0
            f = 0
        else:
            if rli:
                ans += abs(now - rli[-1])
                now = rli.pop()
            else:
                ans += N - now + 1
                now = N + 1
            f = 1
    print(ans)

    #return ans



















if __name__ == "__main__":
    main()
    """T = 10
    i = 0
    for _ in range(T):
        N = random.randint(2, 1000)
        ans, S, A = f(N)
        if ans != (tmp := main(N, A, S)):
            print(f"~ case {i} ~")
            print("長さN:", N)
            print("開始位置A:", A)
            print("文字列S:", S)
            print("答えans:", ans)
            print("実行結果tmp:", tmp)
            i += 1"""