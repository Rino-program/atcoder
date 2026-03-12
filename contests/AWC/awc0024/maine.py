# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from copy import deepcopy
import string


# ===== 入出力ヘルパ =====

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

# ===== 定数 =====
INF = 10 ** 18

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, W = list(map(int, input().split()))
    LC: list[list[int]] = [list(map(int, input().split())) for _ in range(N)]
    dp: list[list[int]] = [[INF for _ in range(W+1)] for _ in range(N+1)]
    dp[0][0] = 0
    for i in range(N):
        L, C = LC[i]
        for j in range(W+1):
            if dp[i][j] != INF:
                tmp = -1 # 回数
                for k in range(j, W+1, L):
                    dp[i+1][k] = min(dp[i+1][k], dp[i][j] + tmp+1)
                    tmp += 1
                    if tmp == C:
                        break
    """for i in range(N+1):
        for j in range(W+1):
            if dp[i][j] == INF:
                print("o", end="_")
            else:
                print(dp[i][j], end="_")
        print()"""
    ans = INF
    for i in range(N+1):
        if dp[i][-1] != INF:
            ans = min(ans, dp[i][-1])
    print(ans if ans != INF else -1)


















if __name__ == "__main__":
    main()