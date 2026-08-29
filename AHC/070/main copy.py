# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
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

def main() -> None:
    # ここに解答を書く
    Debug = False
    
    input_data = sys.stdin.read().split()
    N, M = int(input_data[0]), int(input_data[1])
    Map = [0 for _ in range(N**2)]
    MapAB = [0 for _ in range(N**2)]
    AB = [tuple(map(lambda x:x-1, map(int, input_data[i:i+2]))) for i in range(2, len(input_data), 2)]
    s = set()
    isqrt = math.isqrt
    # 多頂点BFS的に減速させながら伝搬させる
    floor = math.floor
    for i, (A, B) in enumerate(AB):
        d = deque([(A, B, floor(i*1.2+5000))])
        f = set()
        f.add((A, B))
        while d:
            x, y, t = d.popleft()
            if t <= 0:
                continue
            MapAB[x * N + y] += t
            for dx, dy in DIR4:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in f:
                    f.add((nx, ny))
                    d.append((nx, ny, floor(t*(0.4))))
    if Debug:
        print_grid([MapAB[i * N:(i + 1) * N] for i in range(N)], sep="_")
    newMapAB = [0 for _ in range(N**2)]
    now = (0, 0)
    DIR = [(71, 43), (13, 37), (2, 11)]
    print(*[" ".join(map(str, DIR[i])) for i in range(3)], sep="\n", flush=True)
    ans = []
    for i in range(N ** 2):
        A, B = AB[i]
        nA1, nB1 = (now[0] + DIR[0][0]) % N, (now[1] + DIR[0][1]) % N
        nA2, nB2 = (now[0] + DIR[1][0]) % N, (now[1] + DIR[1][1]) % N
        nA3, nB3 = (now[0] + DIR[2][0]) % N, (now[1] + DIR[2][1]) % N
        n1 = (nA1, nB1)
        n2 = (nA2, nB2)
        n3 = (nA3, nB3)
        ne = max((0 if Map[n1[0] * N + n1[1]] == 1 else 1, MapAB[n1[0] * N + n1[1]], -(abs(A - n1[0]) + abs(B - n1[1])), 0), (0 if Map[n2[0] * N + n2[1]] == 1 else 1, MapAB[n2[0] * N + n2[1]], -(abs(A - n2[0]) + abs(B - n2[1])), 1), (0 if Map[n3[0] * N + n3[1]] == 1 else 1, MapAB[n3[0] * N + n3[1]], -(abs(A - n3[0]) + abs(B - n3[1])), 2))
        ans_now = None
        ne = ne[2:]
        ne = (-ne[0], ne[1])
        if ne[1] == 0:
            now = n1
            ans_now = 0
        elif ne[1] == 1:
            now = n2
            ans_now = 1
        else:
            now = n3
            ans_now = 2
        Map[now[0] * N + now[1]] = 1
        # 統治する(周りを減らす)
        d = deque([(now[0], now[1], MapAB[now[0] * N + now[1]])])
        f = set()
        f.add((now[0], now[1]))
        while d:
            x, y, t = d.popleft()
            if t <= 0:
                continue
            MapAB[x * N + y] -= t
            MapAB[x * N + y] = max(MapAB[x * N + y], 0)
            for dx, dy in DIR4:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in f:
                    f.add((nx, ny))
                    d.append((nx, ny, floor(t*(0.5))))
        ans.append(ans_now)
    if not Debug:
        print(*ans, sep="\n")
    if Debug:
        print_grid([MapAB[i * N:(i + 1) * N] for i in range(N)], sep="_")




















if __name__ == "__main__":
    main()
