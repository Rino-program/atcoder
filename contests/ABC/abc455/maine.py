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

class Mo:
    """概要:
        Mo's Algorithm（オフライン区間クエリ高速処理）クラス。
        区間 [l, r) に対するクエリをまとめて O((N+Q)√N) で処理する。

    使い方:
        1. Mo(n, queries) でインスタンス化（queries は (l, r) のリスト）
        2. add_left / add_right / remove_left / remove_right を実装して渡すか、
           外部変数を使うクロージャで定義する。
        3. mo.run(add_left, add_right, remove_left, remove_right, query_func)
           を呼ぶと、クエリ順に query_func の結果が返る。

    計算量:
        O((N + Q) * sqrt(N)) × 各操作コスト

    制約:
        オフライン処理のみ（クエリを事前に全部受け取れる場合のみ使用可能）。
        追加・削除が逆操作可能な場合にのみ正確に動く。

    使用例:
        # 区間内の異なる要素数を数える例
        from collections import defaultdict
        cnt = defaultdict(int)
        distinct = [0]

        def add(i):
            if cnt[A[i]] == 0:
                distinct[0] += 1
            cnt[A[i]] += 1

        def remove(i):
            cnt[A[i]] -= 1
            if cnt[A[i]] == 0:
                distinct[0] -= 1

        mo = Mo(N, queries)
        answers = mo.run(add, add, remove, remove, lambda: distinct[0])
    """

    def __init__(self, n: int, queries: list[tuple[int, int]]):
        """
        入力:
            n (int): 配列長
            queries (list[tuple[int, int]]): (l, r) のクエリリスト（半開区間 [l, r)）
        """
        self.n = n
        self.queries = queries
        self.q = len(queries)
        self.block = max(1, int(n ** 0.5))

    def _order(self) -> list[int]:
        """ヒルベルト曲線順でクエリをソートしたインデックスを返す（定数倍改善）"""
        def hilbert_order(x: int, y: int, pow_: int, rotate: int) -> int:
            if pow_ == 0:
                return 0
            half = 1 << (pow_ - 1)
            rx = 1 if (x & half) else 0
            ry = 1 if (y & half) else 0
            result = hilbert_order(
                x if ry == 1 else (half - 1 - x if rx == 1 else x),
                y if ry == 1 else (half - 1 - y if rx == 1 else y),
                pow_ - 1,
                (rotate + 2 * (1 - rx) * (1 - ry) + 3 * rx * (1 - ry) + rx * ry) % 4
            )
            if rx == 1:
                x, y = half - 1 - y, half - 1 - x
            elif ry == 0:
                x, y = half - 1 - x, half - 1 - y
            if rx == 0 and ry == 0:
                x, y = y, x
            return result + half * half * (rx + 2 * ry)

        # ヒルベルト順が重い場合は通常のブロックソートに切り替え可
        # return sorted(range(self.q), key=lambda i: (
        #     self.queries[i][0] // self.block,
        #     self.queries[i][1] if (self.queries[i][0] // self.block) % 2 == 0 else -self.queries[i][1]
        # ))

        LOG = max(1, self.n.bit_length())
        return sorted(
            range(self.q),
            key=lambda i: hilbert_order(self.queries[i][0], self.queries[i][1], LOG, 0)
        )

    def run(
        self,
        add_left,    # add_left(i)  : 区間左端に index i を追加
        add_right,   # add_right(i) : 区間右端に index i を追加
        rem_left,    # rem_left(i)  : 区間左端から index i を削除
        rem_right,   # rem_right(i) : 区間右端から index i を削除
        query_func,  # query_func() : 現在の区間の答えを返す
    ) -> list:
        """
        概要:
            クエリをソート順に処理し、各クエリの答えをリストで返す。
        入力:
            add_left(i)   : 左端を1つ広げるとき（l を l-1 に）呼ばれる
            add_right(i)  : 右端を1つ広げるとき（r を r+1 に）呼ばれる
            rem_left(i)   : 左端を1つ縮めるとき（l を l+1 に）呼ばれる
            rem_right(i)  : 右端を1つ縮めるとき（r を r-1 に）呼ばれる
            query_func()  : 現在の区間 [cur_l, cur_r) の答えを返す
        出力:
            list: answers[i] = i番目のクエリの答え
        補足:
            [l, r) の半開区間で管理。
            cur_r は「現在含まれている最大インデックス + 1」。
        """
        order = self._order()
        answers = [None] * self.q

        cur_l, cur_r = 0, 0  # 現在の区間 [cur_l, cur_r)（初期は空）

        for qi in order:
            l, r = self.queries[qi]
            # r を広げる（右端を追加）
            while cur_r < r:
                add_right(cur_r)
                cur_r += 1
            # l を狭める（左端を削除）
            while cur_l > l:
                cur_l -= 1
                add_left(cur_l)
            # r を縮める（右端を削除）
            while cur_r > r:
                cur_r -= 1
                rem_right(cur_r)
            # l を広げる（左端を削除）
            while cur_l < l:
                rem_left(cur_l)
                cur_l += 1

            answers[qi] = query_func()

        return answers

def main() -> None:
    # ここに解答を書く
    N = INT()
    S = STR()
    from collections import defaultdict
    cnt = defaultdict(int)
    distinct = [0]

    def add(i):
        if cnt[A[i]] == 0:
            distinct[0] += 1
        cnt[A[i]] += 1

    def remove(i):
        cnt[A[i]] -= 1
        if cnt[A[i]] == 0:
            distinct[0] -= 1

    mo = Mo(N, queries)
    answers = mo.run(add, add, remove, remove, lambda: distinct[0])
    for i in answers:
        if 
    print(ans)





















if __name__ == "__main__":
    main()