# https://yukicoder.me/submissions/1172043 と似ていたので

import sys
import operator
from collections.abc import Callable

class SegTree:
    """概要:
        モノイド演算を扱う汎用 Segment Tree。

    メソッド:
        build(arr): 初期配列から構築する。
        set(i, v) / update(i, v): 1点更新を行う。
        get(i): 1点取得を行う。
        query(l, r): 区間 [l, r) の集約値を返す。
        max_right(l, f): [l, r) の集約が条件 f を満たす最大の r を返す。
        min_left(r, f): [l, r) の集約が条件 f を満たす最小の l を返す。
        all_query(): 全区間の集約値を返す。

    計算量:
        build は O(n)、set/update/get/query/max_right/min_left は O(logN)、all_query は O(1)。
    """
    def __init__(self, n: int, op: Callable = operator.add, e: int = 0):
        self.n = n
        self.op = op
        self.e = e
        self.size = 1
        while self.size < n: self.size <<= 1
        self.data = [e] * (2 * self.size)

    def build(self, arr: list[tuple]) -> None:
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def set(self, i: int, v: tuple) -> None:
        """a[i] = v"""
        i += self.size
        self.data[i] = v
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def get(self, i: int) -> tuple:
        """a[i]を取得"""
        return self.data[self.size + i]

    def query(self, l: int, r: int) -> tuple:
        """[l, r) の演算結果"""
        sml = self.e
        smr = self.e
        l += self.size
        r += self.size
        while l < r:
            if l & 1:
                sml = self.op(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op(sml, smr)

    def max_right(self, l: int, f: Callable[[tuple], bool]) -> int:
        if l == self.n:
            return self.n
        assert 0 <= l <= self.n
        assert f(self.e)

        l += self.size
        sm = self.e
        while True:
            while l % 2 == 0:
                l >>= 1
            nxt = self.op(sm, self.data[l])
            if not f(nxt):
                while l < self.size:
                    l <<= 1
                    nxt = self.op(sm, self.data[l])
                    if f(nxt):
                        sm = nxt
                        l += 1
                return l - self.size
            sm = nxt
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r: int, f: Callable[[tuple], bool]) -> int:
        if r == 0:
            return 0
        assert 0 <= r <= self.n
        assert f(self.e)

        r += self.size
        sm = self.e
        while True:
            r -= 1
            while r > 1 and r % 2:
                r >>= 1
            nxt = self.op(self.data[r], sm)
            if not f(nxt):
                while r < self.size:
                    r = (r << 1) | 1
                    nxt = self.op(self.data[r], sm)
                    if f(nxt):
                        sm = nxt
                        r -= 1
                return r + 1 - self.size
            sm = nxt
            if (r & -r) == r:
                break
        return 0

    def all_query(self) -> tuple:
        """全区間の演算結果"""
        return self.data[1]

    update = set  # エイリアス


def solve():
    # 入力をすべて取得して空白文字で分割 (Fast I/O)
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    N = int(input_data[0])
    S = input_data[1]
    Q = int(input_data[2])

    # カスタム演算子 (un_open, un_close, match)
    def op(left, right):
        lo, lc, lm = left
        ro, rc, rm = right
        # left の余った '(' と right の余った ')' が新しくペアになる
        new_match = lo if lo < rc else rc
        return (lo + ro - new_match, lc + rc - new_match, lm + rm + new_match)

    # 単位元
    e = (0, 0, 0)
    
    # セグメント木の初期化
    st = SegTree(N, op=op, e=e)
    
    # 状態の対応: '(' -> (1, 0, 0), ')' -> (0, 1, 0)
    val_open = (1, 0, 0)
    val_close = (0, 1, 0)

    # 文字列Sから初期配列生成と構築
    arr = [val_open if ch == 'A' else val_close for ch in S]
    st.build(arr)

    out = []
    idx = 3
    for _ in range(Q):
        q_type = int(input_data[idx])
        if q_type == 1:
            # クエリ1: 更新
            # 文字に変更
            x = int(input_data[idx+1]) - 1
            t = input_data[idx+2]
            
            if t == "A":
                st.set(x, val_open)
            else:
                st.set(x, val_close)
                
            idx += 3
        else:
            # クエリ2: 区間取得
            # 問題文の 1-indexed で [L, R] 閉区間
            # SegTreeは 0-indexed で [l, r) 半開区間なので L-1, R に変換
            L = int(input_data[idx+1]) - 1
            R = int(input_data[idx+2])
            
            res = st.query(L, R)
            
            # ABC473 条件に変更
            if res[1]:
                print("No")
            else:
                print("Yes")
            
            idx += 3

    """# 結果をまとめて出力
    if out:
        sys.stdout.write('\n'.join(out) + '\n')"""

if __name__ == '__main__':
    solve()