# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
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
        print(sep.join(map(str, map(lambda x: f"{x:02}" if isinstance(x, int) else x, row))))


# ==============================================
# =================== main =====================
# ==============================================

def bfs_path(g: list[list[int]], s: int, t: int) -> list[int] | None:
    """概要:
        重みなしグラフで s から t への最短経路を BFS で求めて返す。
    入力:
        g (list[list[int]]): 隣接リスト。
        s (int): 始点。
        t (int): 終点。
    出力:
        list[int] | None: s から t への頂点列。到達不能なら None。
    補足:
        計算量は O(V+E)。経路が複数ある場合は最短の1つを返す。
    """
    n = len(g)
    parent = [-1] * n
    visited = [False] * n
    visited[s] = True
    q = deque([s])
    while q:
        v = q.popleft()
        if v == t:
            break
        for to in g[v]:
            if not visited[to]:
                visited[to] = True
                parent[to] = v
                q.append(to)
    if not visited[t]:
        return None
    path = []
    v = t
    while v != -1:
        path.append(v)
        v = parent[v]
    path.reverse()
    return path

def main() -> None:
    # ここに解答を書く
    N, M = 20, 100
    MAP()
    Map = [["__"] * N for _ in range(N)]
    li = []
    start = None
    for num in range(M):
        i, j = MAP()
        if num == 0:start = (i, j)
        else:
            Map[i][j] = num
        li.append((i, j))
    # 磨きを入れる場所リスト (i % 2 != 0 and j % 2 != 0)
    polishing_points = set([(i, j) for i in range(N) for j in range(N) if i % 2 != 0 and j % 2 != 0])
    #debug("Polishing points:", polishing_points)
    g = [[] for _ in range(N * N)]
    # 4方向に移動するためのグラフを構築
    for i in range(N):
        for j in range(N):
            for di, dj in DIR4:
                ni, nj = i + di, j + dj
                if 0 <= ni < N and 0 <= nj < N:
                    g[i * N + j].append((ni * N + nj))
    # main
    ans = []
    if start in polishing_points:
        ans.append('P')
        for j, (di, dj) in enumerate(DIR4):
            ni, nj = li[0][0] + di, li[0][1] + dj
            if 0 <= ni < N and 0 <= nj < N:
                g[ni * N + nj].remove(start[0] * N + start[1])
            if (0 <= ni < N and 0 <= nj < N) and (0 <= ni-DIR4[j][0]*2 < N and 0 <= nj-DIR4[j][1]*2 < N):
                g[(ni-DIR4[j][0]*2) * N + (nj-DIR4[j][1]*2)].append(ni * N + nj)
    for i in range(M-1):
        # 次の数字までの最短経路を求める
        start_idx = li[i][0] * N + li[i][1]
        target_idx = li[i+1][0] * N + li[i+1][1]
        path = bfs_path(g, start_idx, target_idx)
        # Noneになる事はない。
        # 経路を文字列に変換
        # ここで、磨きマスがある事に注意。
        # 磨き済みマスは出力なしに直進通過するので出力を通る磨き済みマス分だけ減らす。
        moves = []
        for k in range(1, len(path)):
            prev = path[k-1]
            curr = path[k]
            di, dj = (curr // N) - (prev // N), (curr % N) - (prev % N)
            if di < 0:
                moves.append('U')
            elif di > 0:
                moves.append('D')
            elif dj < 0:
                moves.append('L')
            elif dj > 0:
                moves.append('R')
        # 目的地が磨き候補マスであったらをPで磨く(磨き済みマスにする)
        if (li[i+1][0], li[i+1][1]) in polishing_points:
            #debug(f"Polishing at: {li[i+1]}")
            moves.append('P')
            # 磨いたマスは滑る,つまり辺を伸ばす感じ
            for j, (di, dj) in enumerate(DIR4):
                ni, nj = li[i+1][0] + di, li[i+1][1] + dj
                if 0 <= ni < N and 0 <= nj < N:
                    g[ni * N + nj].remove(target_idx)
                if (0 <= ni < N and 0 <= nj < N) and (0 <= ni-DIR4[j][0]*2 < N and 0 <= nj-DIR4[j][1]*2 < N):
                    g[(ni-DIR4[j][0]*2) * N + (nj-DIR4[j][1]*2)].append(ni * N + nj)
        for m in moves:
            ans.append(m)
    """with open("output.txt", "w") as f:
        f.write('\n'.join(ans))"""
    print('\n'.join(ans))




















if __name__ == "__main__":
    main()
