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
def topological_sort(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフをトポロジカルソートする。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: トポロジカル順序。閉路があれば None。
    補足:
        Kahn 法（入次数管理）を使用する。計算量は O(V+E)。
    """
    n = len(g)
    indeg = [0] * n
    for v in range(n):
        for to in g[v]:
            indeg[to] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    result = []
    while q:
        v = q.popleft()
        result.append(v)
        for to in g[v]:
            indeg[to] -= 1
            if indeg[to] == 0:
                q.append(to)
    return result if len(result) == n else None
# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, Q = MAP()
    tuv = TUPLES(Q)
    s = set()
    g = [[] for i in range(N)]
    for t, u, v in tuv:
        if t == 1:
            u -= 1; v -= 1
            g[u].append(v)
            if u == v:
                No()
                return
            s.add(u)
            s.add(v)
    T = topological_sort(g)
    g = [[] for i in range(N)]
    for t, u, v in tuv:
        if t == 0:
            u -= 1; v -= 1
            g[u].append(v)
    if T == None:
        No()
        return
    Yes()
    ans = [0] * N
    now = 0
    st = []
    for t in T:
        if t in s:
            now += 1
            st.append((t, now))
        ans[t] = now
    for i in range(N):
        if i not in s:
            ans[i] = -1
    for now in st:
        d = deque()
        d.append(now[0])
        n = now[1]
        while d:
            x = d.popleft()
            ans[x] = n
            for i in g[x]:
                if ans[i] == -1:
                    d.append(i)
    for i in range(N):
        if ans[i] == -1:
            ans[i] = 1
    print(*ans)





















if __name__ == "__main__":
    main()
