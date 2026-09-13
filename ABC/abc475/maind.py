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

import random
def is_prime(n: int, k_random: int = 15) -> bool:
    """
    整数 n が素数かどうかを判定する (ミラー-ラビン素数判定法)。

    対応範囲:
        - n < 2^64: 100% 決定論的判定 (反例が存在しない底を選択、完全AC保証)
        - n >= 2^64: 確率的判定 (固定12底 + ランダム k_random 底によるHack完全耐性)

    計算量:
        【時間計算量】(テストする基底の合計個数を K とする)
        - 最悪ケース (素数の場合):
            - n < 2^64  : O(K log n)  (K <= 7, 約450演算, 数μs〜数十μs)
            - n >= 2^64 : O(K log^3 n) [K = 12 + k_random, 2^1024 規模でも約 0.1 秒]
        - 平均ケース (合成数の場合):
            - 99.9% 以上の合成数は「最初の1基底」で脱出するため、素数の 1/5〜1/10 以下の時間で終了

        【空間計算量】
        - n < 2^64  : O(1)
        - n >= 2^64 : O(log n) (n のビット長を保持するメモリのみ)

    引数:
        n (int): 判定対象の整数
        k_random (int, optional):
            n >= 2^64 の場合に追加するランダム基底の個数 (デフォルト: 15)。
            最悪誤判定確率は ≦ (1/4)^k_random。(実際に使用する場合はさらに低くなります)
            [目安]
            5: 高速優先 (誤判定率 ≦ 10^-3, 約 80ms @ 2^1024)
            15: 競プロ推奨 (誤判定率 ≦ 10^-9, 約 124ms @ 2^1024, Hack完全防御)
            40: 暗号標準水準 (誤判定率 ≦ 10^-24, 約 270ms @ 2^1024)

    戻り値:
        bool: 素数なら True, 合成数または 1 以下なら False
    """
    if n < 2:
        return False

    # 1. 小さな素数の事前判定 (37以下の素数での試し割り)
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # 37^2 = 1369 未満の合成数は上記で全て弾かれているため素数確定
    if n < 1369:
        return True

    # 2. n - 1 = 2^s * d (d は奇数) の形に分解
    d = n - 1
    s = (d & -d).bit_length() - 1
    d >>= s

    # 3. サイズに応じた基底の選択
    if n < 4759123141:
        # 3基底で決定論的 (Jaeschke, 1993)
        bases = (2, 7, 61)
    elif n < 18446744073709551616:  # 2^64
        # 7基底で決定論的 (Jim Sinclair, 2011)
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    else:
        # 2^64 以上の場合は固定12底 + 指定個数のランダム底
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        bases += [random.randrange(41, n - 1) for _ in range(k_random)]

    # 4. ミラー-ラビン判定メインループ
    for a in bases:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True

# ==============================================
# =================== main =====================
# ==============================================

def main_isprime() -> None:
    # ここに解答を書く
    S = STR()
    se = set(list(S))
    for i in range(10**7):
        if not is_prime(i): continue
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


def main_sieve() -> None:
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
    # main_sieve()
    main_isprime()
