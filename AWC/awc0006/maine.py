# AtCoder Competition Template v2.3.1 SHORT (PyPy 7.3.20 / Python 3.11)
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
MAP0 = lambda: (int(x) - 1 for x in input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: [int(x) - 1 for x in input().split()]
TUPLE = lambda: tuple(map(int, input().split()))
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

# ===== 高速 print =====
def print(*args, sep=' ', end='\n', file=None, flush=False):
    file = file or sys.stdout
    sep = ' ' if sep is None else sep
    end = '\n' if end is None else end
    file.write(sep.join(map(str, args)) + end)
    flush and file.flush()

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
Yes = lambda **kwargs: print("Yes", **kwargs)
No = lambda **kwargs: print("No", **kwargs)
yes = lambda **kwargs: print("yes", **kwargs)
no = lambda **kwargs: print("no", **kwargs)
YES = lambda **kwargs: print("YES", **kwargs)
NO = lambda **kwargs: print("NO", **kwargs)

def yn(cond: bool, yes: str = "Yes", no: str = "No", **kwargs) -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no, **kwargs)

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    print('\n'.join(sep.join(map(str, row)) for row in grid))

# ===== デバッグ =====
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, sep=' ', end='\n', flush=False) -> None:
        """デバッグ出力（標準エラー）"""
        print("[DEBUG]", *args, sep=sep, end=end, file=sys.stderr, flush=flush)
else:
    def debug(*args, **kwargs) -> None:
        pass

# ===== template.py =====
from typing import List, Sequence, Union
class BIT:
    """概要:
        1次元 Binary Indexed Tree（Fenwick Tree）を提供するクラス。

    メソッド:
        build(a): 配列 a から O(N) で木を再構築する。
        add(i, x): a[i] に x を加算する。
        sum(i): 区間 [0, i] の和を返す。
        range_sum(l, r): 区間 [l, r) の和を返す。
        lower_bound(w): 累積和が w 以上になる最小インデックスを返す (各要素が非負の場合)。

    補足:
        すべて 0-indexed インターフェース。
        初期化および build は O(N)。
        add, sum, range_sum, lower_bound は O(log N)。
    """
    def __init__(self, arg: Union[int, Sequence[int]]):
        """
        引数に整数 n を渡した場合は要素数 n (初期値 0) で初期化する。
        引数に配列などのシーケンスを渡した場合は、その要素で O(N) で初期化する。
        """
        if isinstance(arg, int):
            self.n = arg
            self.data = [0] * (self.n + 1)
        else:
            self.n = len(arg)
            self.data = [0] * (self.n + 1)
            self.build(arg)

    def build(self, a: Sequence[int]) -> None:
        """与えられたシーケンス a に基づいて O(N) で木を構築する。"""
        self.n = len(a)
        # 1-indexed に合わせるため先頭に 0 を配置
        self.data = [0] + list(a)
        for i in range(1, self.n + 1):
            parent = i + (i & -i)
            if parent <= self.n:
                self.data[parent] += self.data[i]

    def add(self, i: int, x: int) -> None:
        """a[i] に x を加算する (0-indexed)。"""
        i += 1
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i: int) -> int:
        """区間 [0, i] の総和 (a[0] + ... + a[i]) を返す (0-indexed)。"""
        s = 0
        i += 1
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """区間 [l, r) の総和 (a[l] + ... + a[r-1]) を返す (0-indexed)。"""
        if l >= r:
            return 0
        return self.sum(r - 1) - (self.sum(l - 1) if l > 0 else 0)

    def lower_bound(self, w: int) -> int:
        """累積和が w 以上になる最小のインデックスを返す (0-indexed)。
        ※配列の全要素が非負であることが前提条件。
        """
        if w <= 0:
            return 0
        if self.n == 0:
            return 0
        x, k = 0, 1 << (self.n.bit_length() - 1)
        while k > 0:
            if x + k <= self.n and self.data[x + k] < w:
                w -= self.data[x + k]
                x += k
            k //= 2
        return x
# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, Q = MAP()
    S = LIST()
    bit = BIT(S)
    ans = []
    for _ in range(Q):
        t, x, y = MAP()
        if t == 2:
            tmp = S[x-1]
            S[x-1] = y
            bit.add(x-1, y - tmp)
        else:
            debug(bit.range_sum(x-1, y))
            ans.append(bit.range_sum(x-1, y))
    
    print(*ans)





















if __name__ == "__main__":
    main()
