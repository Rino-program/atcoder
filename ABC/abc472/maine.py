# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
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


# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    T = INT()
    for _ in range(T):
        N, M = MAP()
        g = [[] for i in range(N)]
        for i in range(M):
            U, V = MAP()
            U -= 1; V -= 1
            g[U].append(V)
            g[V].append(U)
        l = [-2] * N
        for i in range(N):
            if l[i] != -2:
                continue
            li = [i]
            l[i] = 0
            hukasa = 1
            while li:
                stack = set()
                for now in li:
                    for to in g[now]:
                        if l[to] == hukasa - 1:
                            # 奇数閉路検出
                            A, B = now, to
                            to = hukasa - 2
                            Ali = [A+1]
                            Bli = [B+1]
                            for j in range(to, -1, -1):
                                if A == B:
                                    ans = Ali[::-1] + Bli[:-1]
                                    print(len(ans))
                                    print(" ".join(map(str, ans)))
                                    break
                                else:
                                    for ne in g[A]:
                                        if l[ne] == to:
                                            Ali.append(ne+1)
                                            A = ne
                                            break
                                    for ne in g[B]:
                                        if l[ne] == to:
                                            Bli.append(ne+1)
                                            B = ne
                                            break
                                    to -= 1
                            else:
                                if A == B:
                                    ans = Ali[::-1] + Bli[:-1]
                                    print(len(ans))
                                    print(" ".join(map(str, ans)))
                            break
                        elif l[to] == -2:
                            stack.add(to)
                        else:
                            pass
                    else:
                        continue
                    break
                else:
                    for to in stack:
                        l[to] = hukasa
                    hukasa += 1
                    li = list(stack)
                    continue
                break
            else:
                continue
            break
        else:
            pr(-1)





















if __name__ == "__main__":
    main()
