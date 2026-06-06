# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
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

class FastImplicitTreap:
    """概要:
        列に対する挿入、削除、区間反転、区間クエリを平均 O(log N) で高速に処理する平衡二分探索木。
        関数呼び出しをインライン化し、値ベースの高速分割を追加した定数倍最軽量版。

    メソッド:
        insert(pos, val): pos番目に値valを挿入する。
        insert_sorted(val): ソート状態を維持して値valを挿入する（超高速版）。
        erase(pos): pos番目の要素を削除する。
        query(l, r): 区間 [l, r) の和を取得する。
        reverse(l, r): 区間 [l, r) の要素の並びを反転させる。
        get(pos): pos番目の要素の値を返す。
        pop_max(): 最大値を削除して返す。
        rank(val): 値val未満の要素の個数を返す。

    入力:
        n_max (int): 挿入される最大要素数。

    計算量:
        時間計算量: 各操作について平均 O(log N) （定数倍が極めて軽い）
        空間計算量: O(n_max)
    """
    def __init__(self, n_max: int):
        self.left = [0] * (n_max + 1)
        self.right = [0] * (n_max + 1)
        self.val = [0] * (n_max + 1)
        self.sm = [0] * (n_max + 1)
        self.size = [0] * (n_max + 1)
        self.priority = [0] * (n_max + 1)
        self.rev = [False] * (n_max + 1)
        self.node_cnt = 0
        self.root = 0
        self._seed = 123456789

    def _rand(self) -> int:
        self._seed ^= (self._seed << 13) & 0xFFFFFFFF
        self._seed ^= (self._seed >> 17)
        self._seed ^= (self._seed << 5) & 0xFFFFFFFF
        return self._seed

    def _split(self, root: int, k: int) -> tuple[int, int]:
        l_root = r_root = l_ptr = r_ptr = 0
        l_path, r_path = [], []
        curr = root
        while curr:
            if self.rev[curr]:
                l, r = self.left[curr], self.right[curr]
                self.left[curr], self.right[curr] = r, l
                if l: self.rev[l] = not self.rev[l]
                if r: self.rev[r] = not self.rev[r]
                self.rev[curr] = False
            l_size = self.size[self.left[curr]]
            if k <= l_size:
                if not r_root: r_root = curr
                else: self.left[r_ptr] = curr
                r_ptr = curr
                r_path.append(curr)
                curr = self.left[curr]
            else:
                if not l_root: l_root = curr
                else: self.right[l_ptr] = curr
                l_ptr = curr
                l_path.append(curr)
                curr = self.right[curr]
                k -= l_size + 1
        if l_ptr: self.right[l_ptr] = 0
        if r_ptr: self.left[r_ptr] = 0
        while l_path:
            node = l_path.pop()
            self.size[node] = self.size[self.left[node]] + self.size[self.right[node]] + 1
            self.sm[node] = self.sm[self.left[node]] + self.sm[self.right[node]] + self.val[node]
        while r_path:
            node = r_path.pop()
            self.size[node] = self.size[self.left[node]] + self.size[self.right[node]] + 1
            self.sm[node] = self.sm[self.left[node]] + self.sm[self.right[node]] + self.val[node]
        return l_root, r_root

    def _split_by_val(self, root: int, val: int) -> tuple[int, int]:
        l_root = r_root = l_ptr = r_ptr = 0
        l_path, r_path = [], []
        curr = root
        while curr:
            if self.rev[curr]:
                l, r = self.left[curr], self.right[curr]
                self.left[curr], self.right[curr] = r, l
                if l: self.rev[l] = not self.rev[l]
                if r: self.rev[r] = not self.rev[r]
                self.rev[curr] = False
            if self.val[curr] >= val:
                if not r_root: r_root = curr
                else: self.left[r_ptr] = curr
                r_ptr = curr
                r_path.append(curr)
                curr = self.left[curr]
            else:
                if not l_root: l_root = curr
                else: self.right[l_ptr] = curr
                l_ptr = curr
                l_path.append(curr)
                curr = self.right[curr]
        if l_ptr: self.right[l_ptr] = 0
        if r_ptr: self.left[r_ptr] = 0
        while l_path:
            node = l_path.pop()
            self.size[node] = self.size[self.left[node]] + self.size[self.right[node]] + 1
            self.sm[node] = self.sm[self.left[node]] + self.sm[self.right[node]] + self.val[node]
        while r_path:
            node = r_path.pop()
            self.size[node] = self.size[self.left[node]] + self.size[self.right[node]] + 1
            self.sm[node] = self.sm[self.left[node]] + self.sm[self.right[node]] + self.val[node]
        return l_root, r_root

    def _merge(self, l: int, r: int) -> int:
        if not l: return r
        if not r: return l
        head = prev = is_left = 0
        curr_l, curr_r = l, r
        path = []
        while curr_l and curr_r:
            if self.priority[curr_l] > self.priority[curr_r]:
                if self.rev[curr_l]:
                    cl_l, cl_r = self.left[curr_l], self.right[curr_l]
                    self.left[curr_l], self.right[curr_l] = cl_r, cl_l
                    if cl_l: self.rev[cl_l] = not self.rev[cl_l]
                    if cl_r: self.rev[cl_r] = not self.rev[cl_r]
                    self.rev[curr_l] = False
                path.append(curr_l)
                if prev:
                    if is_left: self.left[prev] = curr_l
                    else: self.right[prev] = curr_l
                else: head = curr_l
                prev, curr_l, is_left = curr_l, self.right[curr_l], False
            else:
                if self.rev[curr_r]:
                    cr_l, cr_r = self.left[curr_r], self.right[curr_r]
                    self.left[curr_r], self.right[curr_r] = cr_r, cr_l
                    if cr_l: self.rev[cr_l] = not self.rev[cr_l]
                    if cr_r: self.rev[cr_r] = not self.rev[cr_r]
                    self.rev[curr_r] = False
                path.append(curr_r)
                if prev:
                    if is_left: self.left[prev] = curr_r
                    else: self.right[prev] = curr_r
                else: head = curr_r
                prev, curr_l_or_r, is_left = curr_r, self.left[curr_r], True
                curr_r = curr_l_or_r
        rem = curr_l if curr_l else curr_r
        if prev:
            if is_left: self.left[prev] = rem
            else: self.right[prev] = rem
        while path:
            node = path.pop()
            self.size[node] = self.size[self.left[node]] + self.size[self.right[node]] + 1
            self.sm[node] = self.sm[self.left[node]] + self.sm[self.right[node]] + self.val[node]
        return head

    def insert(self, pos: int, val: int) -> None:
        self.node_cnt += 1
        idx = self.node_cnt
        self.val[idx] = self.sm[idx] = val
        self.size[idx] = 1
        self.priority[idx] = self._rand()
        l, r = self._split(self.root, pos)
        self.root = self._merge(self._merge(l, idx), r)

    def insert_sorted(self, val: int) -> None:
        self.node_cnt += 1
        idx = self.node_cnt
        self.val[idx] = self.sm[idx] = val
        self.size[idx] = 1
        self.priority[idx] = self._rand()
        l, r = self._split_by_val(self.root, val)
        self.root = self._merge(self._merge(l, idx), r)

    def erase(self, pos: int) -> None:
        l, r = self._split(self.root, pos)
        m, r = self._split(r, 1)
        self.root = self._merge(l, r)

    def query(self, l: int, r: int) -> int:
        left, right = self._split(self.root, l)
        mid, right = self._split(right, r - l)
        res = self.sm[mid] if mid else 0
        self.root = self._merge(self._merge(left, mid), right)
        return res

    def reverse(self, l: int, r: int) -> None:
        left, right = self._split(self.root, l)
        mid, right = self._split(right, r - l)
        if mid: self.rev[mid] = not self.rev[mid]
        self.root = self._merge(self._merge(left, mid), right)

    def get(self, pos: int) -> int:
        curr = self.root
        while curr:
            if self.rev[curr]:
                l, r = self.left[curr], self.right[curr]
                self.left[curr], self.right[curr] = r, l
                if l: self.rev[l] = not self.rev[l]
                if r: self.rev[r] = not self.rev[r]
                self.rev[curr] = False
            l_size = self.size[self.left[curr]]
            if pos == l_size: return self.val[curr]
            elif pos < l_size: curr = self.left[curr]
            else:
                pos -= l_size + 1
                curr = self.right[curr]
        raise IndexError

    def pop_max(self) -> int:
        total = self.size[self.root]
        max_idx = total - 1
        max_val = self.get(max_idx)
        self.erase(max_idx)
        return max_val

    def rank(self, val: int) -> int:
        curr = self.root
        pos = 0
        while curr:
            if self.rev[curr]:
                l, r = self.left[curr], self.right[curr]
                self.left[curr], self.right[curr] = r, l
                if l: self.rev[l] = not self.rev[l]
                if r: self.rev[r] = not self.rev[r]
                self.rev[curr] = False
            if self.val[curr] >= val: curr = self.left[curr]
            else:
                pos += self.size[self.left[curr]] + 1
                curr = self.right[curr]
        return pos

def main() -> None:
    # ここに解答を書く
    X = INT()
    Q = INT()
    """l, r = [], []
    for _ in range(Q):
        A, B = MAP()
        if X > A:
            hepu(l, -A)
        else:
            hepu(r, A)
        if X > B:
            hepu(l, -B)
        else:
            hepu(r, B)
        if (tmp1 := len(l)) != (tmp2 := len(r)):
            if tmp2 > tmp1:
                tmp = hepo(r)
                hepu(l, -X)
                X = tmp
            else:
                tmp = -hepo(l)
                hepu(r, X)
                X = tmp
        print(X)"""
    
    li = FastImplicitTreap(1 + Q*2)
    li.insert(0, X)
    for _ in range(Q):
        A, B = MAP()
        li.insert_sorted(A)
        li.insert_sorted(B)
        print(li.get(li.size[li.root] // 2))





















if __name__ == "__main__":
    main()
