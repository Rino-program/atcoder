import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from itertools import permutations, combinations, accumulate, product, chain
from functools import lru_cache, reduce
from typing import List, Tuple, Optional, Set, Dict
import operator

sys.setrecursionlimit(10 ** 7)  # PyPy での再帰制限緩和

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin.readline().rstrip()

def INT() -> int:
    return int(input())

# ===== よく使う関数 =====
def Yes(): print("Yes")
def No(): print("No")


# ===== デバッグ支援 =====
def debug(*args):
    """デバッグ用出力 (標準エラーに出力)"""
    import sys
    print(*args, file=sys.stderr)

def main() -> None:
    Q = INT()
    
    li = []
    f = -1
    n = 0
    
    for i in range(Q):
        inp = input().split()
        if inp[0] == "1":
            tmp = inp[1]
            li.append(tmp)
            if tmp == "(":
                n += 1
            else:
                n -= 1
            if n < 0 and f == -1:
                f = len(li)
        else:
            tmp = li.pop()
            if tmp == "(":
                n -= 1
            else:
                n += 1
                if len(li) < f and f != -1:
                    f = -1
        if f == -1 and n == 0:
            Yes()
        else:
            No()

if __name__ == "__main__":
    main()

