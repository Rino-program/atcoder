# AtCoder Competition Template v2.2.2 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/.template/main.py &template.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a

import os, sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
from bisect import bisect_left, bisect_right
from copy import deepcopy
import operator
import heapq
import math
import string

# ===== 設定・制限解除 =====
sys.setrecursionlimit(2*10**6)

# ===== 入力ヘルパ =====
input = lambda: sys.stdin.readline().rstrip()
INT = lambda: int(input())
INT0 = lambda: int(input()) - 1
MAP = lambda: map(int, input().split())
MAP0 = lambda: map(lambda x: int(x) - 1, input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: list(map(lambda x: int(x) - 1, input().split()))
TUPLE = lambda: tuple(map(int, input().split()))
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

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

# ===== 方向ベクトル(上(負)から時計回り) =====
DIR4 = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIR8 = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
DIR9 = DIR8 + ((0, 0),) # 中央は最後

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
Yes = lambda: print("Yes")
No = lambda: print("No")
yes = lambda: print("yes")
no = lambda: print("no")
YES = lambda: print("YES")
NO = lambda: print("NO")
def yn(cond: bool, yes: str = "Yes", no: str = "No") -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no)

# ===== デバッグ =====
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, **kwargs) -> None:
        """デバッグ出力（標準エラー）"""
        print("[DEBUG]", *args, **kwargs, file=sys.stderr)
else:
    def debug(*args, **kwargs) -> None:
        pass

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))

# ===== template.py =====

def sieve(n: int) -> tuple[list[bool], list[int]]:
    """概要:
        0..n の素数判定配列と素数一覧をエラトステネスの篩で構築する。
    入力:
        n (int): 上限値。
    出力:
        tuple[list[bool], list[int]]: (is_prime配列, 素数リスト)。
    補足:
        計算量は O(n log log n)。
    """
    is_prime_arr = [True] * (n + 1)
    if n >= 0: is_prime_arr[0] = False
    if n >= 1: is_prime_arr[1] = False
    for p in range(2, math.isqrt(n) + 1):
        if is_prime_arr[p]:
            is_prime_arr[p * p : n + 1 : p] = [False] * (((n - p * p) // p) + 1)
    primes = [i for i in range(2, n + 1) if is_prime_arr[i]]
    return is_prime_arr, primes

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    S = STR()
    se = set(list(S))
    sie = sieve(10**7)[1]
    for i in sie:
        T = str(i)
        if len(T) != len(S):
            continue
        f = 0
        di = dedict(set)
        se2 = set()
        for i, t in en(T):
            di[S[i]].add(t)
            se2.add(t)
        for i in di.values():
            if len(i) > 1:
                f = 1
        if f == 0 and len(se2) == len(se):
            print(T)
            return
    print(-1)





















if __name__ == "__main__":
    main()
