# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys
from typing import List, Tuple, Optional, Set, Dict, Callable, Union

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

# ===== よく使う出力関数 =====
pr = print # ただのさぼり。
def Yes(): print("Yes")
def No(): print("No")
def yes(): print("yes")
def no(): print("no")
def YES(): print("YES")
def NO(): print("NO")

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
    A = STRS(N)
    s = set()
    for i in A:
        tmp = "_".join(i)
        #debug(tmp)
        s.add(tmp)
    print(len(s))









if __name__ == "__main__":
    main()