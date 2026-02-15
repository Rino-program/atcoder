# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys
from typing import List, Tuple, Optional, Set, Dict, Callable, Union

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

# ============================================================
# main
# ============================================================

def main() -> None:
    # ここに解答を書く
    #out = Output()
    N, Q = MAP()
    A = LIST()
    LR = LISTS(Q)
    tmp = 0
    Li = [(tmp := max(tmp, i)) for i in A]
    tmp = 0
    Ri = [(tmp := max(tmp, i)) for i in A[::-1]]
    Ri = Ri[::-1]
    for L, R in LR:
        print(min(Li[R-1], Ri[L-1]))









if __name__ == "__main__":
    main()