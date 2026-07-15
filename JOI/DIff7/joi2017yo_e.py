# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin.readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    H, W = MAP()
    M = LISTS(H)
    g = [[] for _ in range(H * W)]
    for i in range(H):
        for j in range(W):
            for x, y in DIR4:
                ni, nj = i + x, j + y
                if 0 <= ni < H and 0 <= nj < W and M[i][j] <= M[ni][nj]:
                    g[ni*W + nj].append(i*W + j)
    t = [-1] * (H * W)
    for i in range(H):
        for j in range(W):
            t[M[i][j]-1] = i*W + j
    ans_li = [0] * (H * W)
    for v in t:
        tmp = 0
        for to in g[v]:
            if tmp != 0 and ans_li[to] != tmp:
                ans_li[v] = -1
                break
            else:
                tmp = ans_li[to]
        else:
            ans_li[v] = tmp
        if not g[v]:
            ans_li[v] = v+1
    ans = 0
    for i in ans_li:
        if i == -1:
            ans += 1
    print(ans)





















if __name__ == "__main__":
    main()
