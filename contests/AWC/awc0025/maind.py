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

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def build_doubling(
    n: int,
    nxt: list[int],
    log: int = 30,
    weight: list[int] | None = None,
    op = None,
    e = None,
) -> tuple[list[list[int]], list[list[int]] | None]:
    """概要:
        関数的グラフに対してダブリングテーブルを構築する。
        オプションで「各ステップに付随する値（重み）」の累積テーブルも同時構築できる。

    入力:
        n      (int)            : 頂点数（0-indexed）。
        nxt    (list[int])      : nxt[v] = v から 1 ステップ先（0-indexed）。
        log    (int)            : テーブル段数。2^log >= クエリ最大ステップ数 を満たすこと。
        weight (list[int]|None) : weight[v] = v を出発した際に加算される値。None なら無効。
        op     (callable|None)  : 重みの結合演算（例: operator.add, max）。None なら加算。
        e      (any|None)       : 重みの単位元（例: 0, -INF）。None なら 0。

    出力:
        tuple:
            [0] doubling[k][v]     : v から 2^k ステップ後の頂点。
            [1] acc[k][v]          : v から 2^k ステップで累積した重み。weight=None なら None。

    計算量:
        O(N * log)

    使用例（頂点のみ）:
        nxt = [A[i] - 1 for i in range(N)]
        db, _ = build_doubling(N, nxt)
        v = doubling_query(db, X-1, Y)

    使用例（頂点 + 累積コスト）:
        nxt = [to_list[v] for v in range(N)]
        w   = [cost_list[v] for v in range(N)]
        db, ac = build_doubling(N, nxt, weight=w, op=operator.add, e=0)
        v, total_cost = doubling_query_with_weight(db, ac, operator.add, 0, X-1, Y)
    """
    if op is None:
        import operator
        op = operator.add
    if e is None:
        e = 0

    doubling = [[0] * n for _ in range(log)]
    doubling[0] = list(nxt)

    if weight is not None:
        acc = [[e] * n for _ in range(log)]
        acc[0] = list(weight)
    else:
        acc = None

    for k in range(1, log):
        for v in range(n):
            mid = doubling[k-1][v]
            doubling[k][v] = doubling[k-1][mid]
            if acc is not None:
                acc[k][v] = op(acc[k-1][v], acc[k-1][mid])

    return doubling, acc


def doubling_query(
    doubling: list[list[int]],
    v: int,
    y: int,
) -> int:
    """概要:
        ダブリングテーブルを用いて v から y ステップ後の頂点を返す。

    入力:
        doubling : build_doubling の戻り値 [0]。
        v        : 始点（0-indexed）。
        y        : ステップ数（0 以上）。

    出力:
        int: y ステップ後の頂点（0-indexed）。

    計算量:
        O(log y)
    """
    log = len(doubling)
    for k in range(log):
        if (y >> k) & 1:
            v = doubling[k][v]
    return v

def main() -> None:
    # ここに解答を書く
    N, S, Q = MAP()
    S -= 1
    X = LIST()
    now = X[S]
    Xidx = {x: i for i, x in enumerate(X)}
    Xold = deepcopy(X)
    X.sort()
    S = X.index(now)
    visited = [False] * N
    visited[S] = True
    zenkai = -1
    while 1:
        Q -= 1
        # ↓ タイブレークを元番号で正しく比較するよう修正
        left_d = abs(X[S] - X[S-1]) if S-1 >= 0 else INF
        right_d = abs(X[S] - X[S+1]) if S+1 < N else INF
        if left_d < right_d:
            now = S - 1
        elif right_d < left_d:
            now = S + 1
        else:  # 等距離 → 元の番号（0-indexed）が小さい方
            now = S - 1 if Xidx[X[S-1]] < Xidx[X[S+1]] else S + 1
        S = now
        if visited[S]:
            print(Xold.index(X[S])+1 if Q % 2 == 0 else Xold.index(X[zenkai])+1)
            return
        zenkai = S
        visited[S] = True
        if Q == 0:
            print(Xold.index(X[S])+1)
            return
        #debug(S)
















if __name__ == "__main__":
    main()