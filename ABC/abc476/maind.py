# AtCoder Competition Template v2.3.0 SHORT (PyPy 7.3.20 / Python 3.11)
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
INF = float('inf')
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

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, M, K = MAP()
    X, Y = MAP()
    A = LIST()+[INF]
    B = LIST()+[INF]
    ans = 0

    # X
    A.sort(reverse=True)
    while X - A[-1] >= 0:
        X -= A.pop()
        ans += 1
    A[-1] -= X

    # Y
    z = 0
    now = 0
    A.reverse()
    B.sort(reverse=True)
    As = [0] + list(accumulate(A))
    As[-1] = 0
    while now < len(A) and K*Y >= B[-1] or K*Y >= A[now]:
        tmp = min(Y, (B[-1]+(K-1))//K)
        idx1 = bir(As, tmp*K + z + As[now]) - 1
        idx2 = bir(As, tmp*K - B[-1] + z + A[now]) - 1 + (1 if tmp*K - B[-1] >= 0 else 0)
        if idx1 == idx2 == -1:
            # もう買えないよ～
            print(ans)
            return
        if idx1 == idx2:
            # 同じ分だけ買えるから1ドルの多い方を
            idx2 -= 1
            tmp1 = K*tmp - (As[idx1] - z - As[now])
            tmp2 = K*tmp - B[-1] - As[idx2]
            if tmp1 < tmp2:
                ans += 1 + idx2 - now
                B.pop()
                z = tmp2
                now = idx2
            else:
                ans += idx1 - now
                now = idx1
        if idx1 < idx2:
            idx2 -= 1
            tmp2 = K*tmp - B[-1] - As[idx2]
            ans += 1 + idx2 - now
            B.pop()
            z = tmp2
            now = idx2
        else:
            tmp1 = K*tmp - (As[idx1] - z - As[now])
            ans += idx1 - now
            now = idx1
        Y -= tmp
    print(ans)





















if __name__ == "__main__":
    main()
