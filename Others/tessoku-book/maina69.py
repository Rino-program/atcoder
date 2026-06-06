# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from copy import deepcopy
import string

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> list[str]:
    return [STR() for _ in range(n)]

def CHARS() -> list[str]:
    return list(STR())

def STRSL(n: int) -> list[list[str]]:
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
def yn(cond: bool) -> None:
    """条件に応じてYes/No出力"""
    print("Yes" if cond else "No")

# ===== デバッグ =====
def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

def print_grid(grid:  list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def bipartite_matching(n: int, m: int, adj: list[list[int]]) -> int:
    """概要:
        二部グラフの最大マッチング数を増加路DFSで求める。
    入力:
        n   (int)            : 左側頂点数（例: 生徒数）。0-indexed。
        m   (int)            : 右側頂点数（例: 席数）。0-indexed。
        adj (list[list[int]]): adj[i] = 左i から行ける右頂点リスト。
    出力:
        int: 最大マッチング数。
    補足:
        計算量 O(V * E)。N≦数百程度なら十分高速。
        match_r[j] に最終的なマッチング結果が入る（右jに割り当てた左頂点）。
    使用例:
        adj = [[] for _ in range(N)]
        for i in range(N):
            for j in range(M):
                if ok[i][j]:
                    adj[i].append(j)
        ans = bipartite_matching(N, M, adj)
    """
    match_r = [-1] * m

    def dfs(i: int, visited: list[bool]) -> bool:
        for j in adj[i]:
            if visited[j]:
                continue
            visited[j] = True
            if match_r[j] == -1 or dfs(match_r[j], visited):
                match_r[j] = i
                return True
        return False

    ans = 0
    for i in range(n):
        visited = [False] * m
        if dfs(i, visited):
            ans += 1
    return ans

def main() -> None:
    # ここに解答を書く
    N = INT()
    C = STRS(N)
    adj = [[] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if C[i][j] == '#':
                adj[i].append(j)
    ans = bipartite_matching(N, N, adj)
    print(ans)





















if __name__ == "__main__":
    main()