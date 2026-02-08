# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from itertools import permutations, combinations, accumulate, product, chain
from functools import lru_cache, reduce
from typing import List, Tuple, Optional, Set, Dict, Callable, Union
from copy import deepcopy
import operator
import string

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> List[int]:
    return list(MAP())

def LISTS(n: int) -> List[List[int]]:
    return [LIST() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> List[str]:
    return [STR() for _ in range(n)]

def CHARS() -> List[str]:
    return list(STR())

def STRSL(n: int) -> List[List[str]]:
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

# ============================================================
# デバッグ
# ============================================================

def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

# ============================================================
# main
# ============================================================

def main() -> None:
    # ここに解答を書く
    #out = Output()
    N = INT()
    A = sorted(LIST())
    ans = set()
    f = 0
    if len(A) > 1 and A[-1] == A[-2]:
        if all(A[0] == i for i in A):
            ans.add(A[0])
            debug("0")
        if A[:len(A)//2] == A[len(A)//2:]:
            ans.add(A[-1])
            debug("1", A[-1])
            print(" ".join(map(str, sorted(list(ans)))))
            sys.exit()
        tmp = A[-1]
        Ad = deepcopy(A)
        """if len(A) % 2 == 0 and (A[len(A)//2-1] != A[len(A)//2]):
            ans.add(A[len(A)//2-1]+A[len(A)//2])
            debug(A)
            debug("1.5", A[len(A)//2-1]+A[len(A)//2])"""
        for i in reversed(Ad):
            if tmp == i:
                A.pop()
            else:
                break
        """if sum(A[:len(A)//2]) != sum(A[len(A)//2:]):
            print(" ".join(map(str, sorted(list(ans)))))
            sys.exit()"""
        if len(A) != 0 and len(A) % 2 == 0:
            ans.add(A[len(A)//2-1]+A[len(A)//2])
            debug(A)
            debug("2", A[len(A)//2-1]+A[len(A)//2])
    else:
        if len(A) == 1:
            print(A[0])
            sys.exit()
        if len(A) % 2 == 1:
            ans.add(A[-1])
            debug("3", A[-1])
            A.pop()
        ans.add(A[len(A)//2-1]+A[len(A)//2])
        debug("4", A[len(A)//2-1]+A[len(A)//2])
    print(" ".join(map(str, sorted(list(ans)))))







if __name__ == "__main__":
    main()