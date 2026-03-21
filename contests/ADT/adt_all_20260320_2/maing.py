# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
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

def merge_intervals(intervals: list[tuple[int, int]], half_open: bool = True) -> list[tuple[int, int]]:
    """概要:
        区間のリストをマージして最小個数の区間リストを返す。
    入力:
        intervals (list[tuple[int, int]]): 区間 (L, R) のリスト。
        half_open (bool): True なら右半開区間 [L,R)、False なら閉区間 [L,R]。
    出力:
        list[tuple[int, int]]: マージ済みの区間リスト（Lで昇順ソート済み）。
    補足:
        右半開区間では [1,3) と [3,5) はマージされて [1,5) になる（L<=curR でマージ）。
        閉区間では [1,3] と [4,5] はマージされない（L<=curR+1 でマージ）。
        計算量は O(N log N)（ソートが支配的）。
    使用例:
        ivs = [(1,3),(2,5),(7,9)]
        print(merge_intervals(ivs))  # [(1,5),(7,9)]
    """
    if not intervals:
        return []
    intervals = sorted(intervals)
    curL, curR = intervals[0]
    result = []
    threshold = 0 if half_open else 1
    for L, R in intervals[1:]:
        if L <= curR + threshold:
            curR = max(curR, R)
        else:
            result.append((curL, curR))
            curL, curR = L, R
    result.append((curL, curR))
    return result

def main() -> None:
    # ここに解答を書く
    N = INT()
    LR = LISTS(N)
    ans = merge_intervals(LR)
    for L, R in ans:
        print(L, R)
    





















if __name__ == "__main__":
    main()