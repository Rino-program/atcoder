# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys
from typing import List, Tuple, Optional, Set, Dict, Callable, Union
from copy import deepcopy

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

def print_grid(grid:  List[List], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))

def print_yes_no(cond: bool) -> None:
    """条件に応じてYes/No出力"""
    print("Yes" if cond else "No")

# ============================================================
# main
# ============================================================

def main() -> None:
    #N: int, A: list
    # ここに解答を書く
    #out = Output()
    N = INT()
    A = LIST()
    """ans = 0
    for i, v1 in enumerate(A):
        for j, v2 in enumerate(A):
            if i != j:
                ans = max(ans, v1+v2)"""
    As = [(A[i]+A[i+1], i) for i in range(len(A)-1)]
    An = sorted(As)
    end = 0
    s = set()
    Aa = deepcopy(A)
    Ana = deepcopy(An)
    skip = 0
    #debug(An)
    while 1:
        n = 0
        for i, j in An:
            if n < skip:
                n += 1
                continue
            if j not in s and j+1 not in s and 2*N - len(s) > 0:
                s.add(j)
                s.add(j+1)
        ans = 0
        tmp = 0
        for i, v in enumerate(A):
            if i not in s:
                ans += v
                tmp += 1
        #debug(N, A, An, s)
        if tmp == 2:
            break
        else:
            A = Aa
            An = Ana
            s = set()
            skip += 1
    print(ans)









if __name__ == "__main__":
    """import random
    T = 10
    L = 5
    for i in range(T):
        li = [random.randint(1, 50) for _ in range(L*2+2)]
        main(L, li)"""
    main()