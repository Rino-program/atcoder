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

from collections.abc import Callable
def binary_search_min(ng: int, ok: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最小 x を整数二分探索で求める。
    入力:
        ng (int): 条件を満たさない側の初期値。
        ok (int): 条件を満たす側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最小の値。
    補足:
        境界の妥当性（ng 側False, ok 側True）を事前に満たすこと。
        計算量は O(log|ok-ng|) 回の判定関数呼び出し。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

from collections.abc import Callable
def binary_search_max(ok: int, ng: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最大 x を整数二分探索で求める。
    入力:
        ok (int): 条件を満たす側の初期値。
        ng (int): 条件を満たさない側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最大の値。
    補足:
        境界の妥当性（ok 側True, ng 側False）を事前に満たすこと。
        計算量は O(log|ok-ng|) 回の判定関数呼び出し。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

def main() -> None:
    # ここに解答を書く
    N, K = MAP()
    A = LIST()
    L = sum(A)
    def check(x: int) -> bool:
        now = 0
        pre = 0
        for i in range(N):
            if A[i] + pre > x:
                if A[i] > x:
                    return False
                now += 1
                pre = A[i]
            else:
                pre += A[i]
        return now <= K
    ans = binary_search_min(0, INF, check)
    print(ans)

    # 合ってる気はするんだけど、正しくならないという事は何かが間違ってるし、
    # しかも結構単純じゃなさそう
    # かなりミスってる希ガス
    # 典型90類題解けて無いのやばい
"""
[RESOLVED] Source file: mainc.py
[RESOLVED] Input directory: input/c

=========================================
Mode: tm | Contest: awc0036 | Problem: c
=========================================

=== TEST + SUBMIT MODE ===

[TEST] Executing:
  oj test -c "C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe mainc.py" -d "input/c"
[INFO] online-judge-tools 11.5.1 (+ online-judge-api-client 10.10.1)
[INFO] 5 cases found
[WARNING] GNU time is not available: time

[INFO] sample-1
[INFO] time: 0.220793 sec
[FAILURE] WA
input:
5_2
3_5_4_7_6

output:
1000000000000000000\r

expected:
11


[INFO] sample-2
[INFO] time: 0.167174 sec
[FAILURE] WA
input:
4_1
1_2_3_4

output:
1000000000000000000\r

expected:
6


[INFO] sample-3
[INFO] time: 0.186291 sec
[FAILURE] WA
input:
10_3
5_8_3_12_7_2_9_6_4_10

output:
1000000000000000000\r

expected:
19


[INFO] sample-4
[INFO] time: 0.173733 sec
[FAILURE] WA
input:
20_5
14_7_23_11_5_19_8_30_12_6_17_25_3_9_21_16_28_4_13_10

output:
1000000000000000000\r

expected:
55


[INFO] sample-5
[INFO] time: 0.197372 sec
[FAILURE] WA
input:
2_1
1000000000_1000000000

output:
1000000000000000000\r

expected:
1000000000


[INFO] slowest: 0.220793 sec  (for sample-1)
[FAILURE] test failed: 0 AC / 5 cases

1
[TEST FAILED] Skipping submit
PS C:\VSCode_program\atcoder\contests\ABC\awc0036> ojp tm c
[RESOLVED] Source file: mainc.py
[RESOLVED] Input directory: input/c

=========================================
Mode: tm | Contest: awc0036 | Problem: c
=========================================

=== TEST + SUBMIT MODE ===

[TEST] Executing:
  oj test -c "C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe mainc.py" -d "input/c"
[INFO] online-judge-tools 11.5.1 (+ online-judge-api-client 10.10.1)
[INFO] 5 cases found
[WARNING] GNU time is not available: time

[INFO] sample-1
[INFO] time: 0.216280 sec
[FAILURE] WA
input:
5_2
3_5_4_7_6

output:
2\r

expected:
11


[INFO] sample-2
[INFO] time: 0.191477 sec
[FAILURE] WA
input:
4_1
1_2_3_4

output:
0\r

expected:
6


[INFO] sample-3
[INFO] time: 0.193353 sec
[FAILURE] WA
input:
10_3
5_8_3_12_7_2_9_6_4_10

output:
3\r

expected:
19


[INFO] sample-4
[INFO] time: 0.260487 sec
[FAILURE] WA
input:
20_5
14_7_23_11_5_19_8_30_12_6_17_25_3_9_21_16_28_4_13_10

output:
5\r

expected:
55


[INFO] sample-5
[INFO] time: 0.201132 sec
[FAILURE] WA
input:
2_1
1000000000_1000000000

output:
999999999\r

expected:
1000000000


[INFO] slowest: 0.260487 sec  (for sample-4)
[FAILURE] test failed: 0 AC / 5 cases

1
[TEST FAILED] Skipping submit
PS C:\VSCode_program\atcoder\contests\ABC\awc0036> ojp tm c
[RESOLVED] Source file: mainc.py
[RESOLVED] Input directory: input/c

=========================================
Mode: tm | Contest: awc0036 | Problem: c
=========================================

=== TEST + SUBMIT MODE ===

[TEST] Executing:
  oj test -c "C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe mainc.py" -d "input/c"
[INFO] online-judge-tools 11.5.1 (+ online-judge-api-client 10.10.1)
[INFO] 5 cases found
[WARNING] GNU time is not available: time

[INFO] sample-1
[INFO] time: 0.205627 sec
[FAILURE] WA
input:
5_2
3_5_4_7_6

output:
3\r

expected:
11


[INFO] sample-2
[INFO] time: 0.193503 sec
[FAILURE] WA
input:
4_1
1_2_3_4

output:
1\r

expected:
6


[INFO] sample-3
[INFO] time: 0.189078 sec
[FAILURE] WA
input:
10_3
5_8_3_12_7_2_9_6_4_10

output:
4\r

expected:
19


[INFO] sample-4
[INFO] time: 0.234422 sec
[FAILURE] WA
input:
20_5
14_7_23_11_5_19_8_30_12_6_17_25_3_9_21_16_28_4_13_10

output:
5\r

expected:
55


[INFO] sample-5
[INFO] time: 0.377551 sec
[SUCCESS] AC

[INFO] slowest: 0.377551 sec  (for sample-5)
[FAILURE] test failed: 1 AC / 5 cases

1
[TEST FAILED] Skipping submit
"""




















if __name__ == "__main__":
    main()