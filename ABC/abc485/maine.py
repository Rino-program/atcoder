# AtCoder Competition Template v2.4.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/.template/main.py
# ALL: https://github.com/Rino-program/atcoder/blob/main/.template/template.py

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

# ===== JIT 設定・制限解除 =====
# 深い再帰のアンロールを無効化 (実測で約8.9倍高速 TLE/MLE防止)
try:
    import pypyjit
    pypyjit.set_param('max_unroll_recursion=-1')
except ImportError:
    pass
# 再帰深度の上限引き上げ
sys.setrecursionlimit(2*10**6)
# 巨大整数の文字列変換エラーを防止
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

# ===== 入力ヘルパ =====
input = lambda: sys.stdin.readline().rstrip("\n")
INT = lambda: int(input())
INT0 = lambda: int(input()) - 1
MAP = lambda: map(int, input().split())
MAP0 = lambda: (int(x) - 1 for x in input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: [int(x) - 1 for x in input().split()]
TUPLE = lambda: tuple(map(int, input().split()))
TUPLE0 = lambda: tuple(int(x) - 1 for x in input().split())
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
LISTS0 = lambda n: [[int(x) - 1 for x in input().split()] for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
TUPLES0 = lambda n: [tuple(int(x) - 1 for x in input().split()) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
LISTSI0 = lambda n: [int(input()) - 1 for _ in range(n)]
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
        """デバッグ出力 (標準エラー) """
        print("[DEBUG]", *args, sep=sep, end=end, file=sys.stderr, flush=flush)
else:
    def debug(*args, **kwargs) -> None:
        pass

# ===== template.py より引用コード =====

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    UVC = TUPLES(M)
    g = [set() for i in range(N)]
    for U, V, C in UVC:
        U -= 1; V -= 1
        g[U].add((V, C))
    d = deque([(0, 0, -1)])
    while d:
        ans, now, c = d.popleft()
        if now == N-1:
            print(ans)
            return
        z = []
        for j in g[now]:
            if j[1] != c:
                z.append(j)
                d.append((ans+1, *j))
        for i in z:
            g[now].remove(i)
    print(-1)


"""
#ABC485 A-E 5完
A: (A>0 and B>0)or(A<0 and B<0)
B: 何でペナるのかは分かんない
C: 切り替わるところからの距離を左右からサーっと見た最小値(初期値INF)
D: 右に残す最低左に残す最低、それぞれのラインLRを定めて、R-L+1-max(i番目からAが少なくとも1つ現れる場所,i番目からBが少なくとも1つ現れる場所,i番目からCが少なくとも1つ現れる場所)+1の合計
E: 条件付きのBFSやるだけに感じた。辺から頂点にいつ入っても先に行けるかどうかの結果は変わらないので一度通ったところは二度通る必要がない。setで管理しておくと辺削除が各O(1)で処理できる
F: 黄らしいしお気に入り全然解いてないので見てない
感想: 「「爆勝ち」」
"""















if __name__ == "__main__":
    main()
