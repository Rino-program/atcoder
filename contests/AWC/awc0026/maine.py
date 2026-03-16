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

def count_subarrays_range_le(arr: list[int], limit: int) -> int:
    """概要:
        変動幅（max - min）が limit 以下の部分配列の個数を返す。
    入力:
        arr (list[int]): 対象配列（0-indexed）。
        limit (int): 変動幅の上限。負の場合は 0 を返す。
    出力:
        int: max(arr[l:r+1]) - min(arr[l:r+1]) <= limit を満たす (l, r) の個数。
    補足:
        単調デックを2本使ったスライディングウィンドウで O(N)。
        「変動幅がちょうど K の区間数」は
        count_subarrays_range_le(arr, K) - count_subarrays_range_le(arr, K-1) で求まる。
    使用例:
        A = [1, 3, 2, 4]
        print(count_subarrays_range_le(A, 2))  # 8
        print(count_subarrays_range_le(A, 2) - count_subarrays_range_le(A, 1))  # 変動幅ちょうど2の個数
    """
    if limit < 0:
        return 0
    n = len(arr)
    max_dq = deque()  # 単調減少（最大値管理）
    min_dq = deque()  # 単調増加（最小値管理）
    l = 0
    ans = 0
    for r in range(n):
        while max_dq and arr[max_dq[-1]] <= arr[r]:
            max_dq.pop()
        max_dq.append(r)
        while min_dq and arr[min_dq[-1]] >= arr[r]:
            min_dq.pop()
        min_dq.append(r)
        while arr[max_dq[0]] - arr[min_dq[0]] > limit:
            l += 1
            if max_dq[0] < l:
                max_dq.popleft()
            if min_dq[0] < l:
                min_dq.popleft()
        ans += r - l + 1
    return ans

def main() -> None:
    # ここに解答を書く
    N, K = MAP()
    A = LIST()
    print(count_subarrays_range_le(A, K) - count_subarrays_range_le(A, K-1))





















if __name__ == "__main__":
    main()