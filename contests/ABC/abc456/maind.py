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

def run_length_encode(s: str | list) -> list[tuple]:
    """概要:
        連続要素を (値, 連続数) に圧縮する。
    入力:
        s (str | list): 圧縮対象シーケンス。
    出力:
        list[tuple]: [(値, 連続数), ...]。
    補足:
        空入力は空配列を返す。計算量は O(n)。
    """
    if not s: return []
    result = []
    current, count = s[0], 1
    for i in range(1, len(s)):
        if s[i] == current:
            count += 1
        else:
            result.append((current, count))
            current, count = s[i], 1
    result.append((current, count))
    return result

def main() -> None:
    # ここに解答を書く
    S = STR()
    """Sr = run_length_encode(S)
    now = 1
    for i in Sr:
        now *= i[1]+1
    num = now
    idx = 0
    now = Sr[idx][1]
    ans = 0
    num //= Sr[idx][1]+1
    debug(num)
    for i in range(len(S)):
        if now == 0:
            idx += 1
            num //= Sr[idx][1]+1
            try: now = Sr[idx][1]
            except: break
        now -= 1
        ans += num
    now = 0
    if [i for i, _ in Sr].count("a") >= 2:
        now = 1
        for i in Sr:
            if i[0] == "a":
                now *= i[1]
    ans -= now
    debug(now)
    now = 0
    if [i for i, _ in Sr].count("b") >= 2:
        now = 1
        for i in Sr:
            if i[0] == "b":
                now *= i[1]
    ans -= now
    debug(now)
    now = 0
    if [i for i, _ in Sr].count("b") >= 2:
        now = 1
        for i in Sr:
            if i[0] == "a":
                now *= i[1]
    ans -= now
    debug(now)"""
    di = {"a": 0, "b": 0, "c": 0}
    for i in S:
        di[i] = (di["a"] + di["b"] + di["c"] + 1) % MOD
    print(sum(di.values()) % MOD)




















if __name__ == "__main__":
    main()