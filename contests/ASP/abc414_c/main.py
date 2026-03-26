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
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def to_base(n: int, base: int) -> str:
    """概要:
        非負整数 n を base 進法表記の文字列に変換する。
    入力:
        n (int): 変換対象の非負整数。
        base (int): 基数（2以上）。
    出力:
        str: base 進法表記の文字列（0 なら "0"）。
    補足:
        計算量は O(log_base(n))。
    使用例:
        to_base(414, 8)  # "636"
        to_base(10, 2)   # "1010"
    """
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(str(n % base))
        n //= base
    return ''.join(reversed(digits))


def gen_palindromes_d_digits(d: int):
    """概要:
        d 桁の十進法回文数を昇順に生成するジェネレータ。
    入力:
        d (int): 桁数（1以上）。
    出力:
        Iterator[int]: d 桁の回文数を昇順に yield する。
    補足:
        前半部（⌈d/2⌉桁）を走査して回文を構成する。計算量は O(10^(d/2)) 個生成。
        d=1: 1〜9、d=2: 11,22,...,99、d=3: 101,111,...,999 など。
    使用例:
        for p in gen_palindromes_d_digits(3):
            print(p)  # 101, 111, 121, ..., 999
    """
    half = (d + 1) // 2
    start = 10 ** (half - 1)
    end   = 10 ** half
    for front in range(start, end):
        s = str(front)
        if d % 2 == 0:
            palindrome_str = s + s[::-1]
        else:
            palindrome_str = s + s[-2::-1]
        yield int(palindrome_str)

def main() -> None:
    # ここに解答を書く
    A = INT()
    N = INT()
    ans = 0
    for d in range(1, 14):
        found_any = False
        for num in gen_palindromes_d_digits(d):
            if num > N:
                break
            found_any = True
            t = to_base(num, A)
            if t == t[::-1]:
                ans += num
        if not found_any:
            break
    print(ans)





















if __name__ == "__main__":
    main()