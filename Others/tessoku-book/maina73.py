# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from copy import deepcopy
import string

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

def STR() -> str:
    return input()

def STRS(n: int) -> list[str]:
    return [STR() for _ in range(n)]

def CHARS() -> list[str]:
    return list(STR())

def STRSL(n: int) -> list[list[str]]:
    return [list(STR()) for _ in range(n)]

# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIR9 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
pr = print # ただのさぼり。
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

def print_grid(grid:  list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def build_graph(n: int, edges: list[tuple[int, int, int, int]], directed: bool = False) -> list[list[tuple[int, int, int]]]:
    """概要:
        辺集合から重みなしグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数（0-indexed を想定）。
        edges (list[tuple[int, int, int, int]]): 辺 (a, b, c, d) の配列。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[tuple[int, int, int]]]: 隣接リスト。
    補足:
        無向時は両方向に辺を追加する。
    """
    g = [[] for _ in range(n)]
    for a, b, c, d in edges:
        g[a-1]. append((b-1, c, d))
        if not directed:
            g[b-1].append((a-1, c, d))
    return g

def dijkstra_multi(
    g: list[list[tuple]],
    s: int,
    n_criteria: int = 2,
    better: "Callable[[tuple, tuple], bool]" = None,
) -> list[tuple]:
    """概要:
        複数基準（主: 距離最小, 副: 任意）を持つダイクストラ法。

    入力:
        g (list[list[tuple]]): 隣接リスト。各要素は (to, *values) の形式。
            values[0] が主コスト（最小化）、残りは副基準。
        s (int): 始点。
        n_criteria (int): 基準数（デフォルト2: 距離+1つの副基準）。
        better (Callable): (新状態tuple, 旧状態tuple) -> bool。
            None の場合は「主: 最小, 副: 最大」をデフォルト適用。

    出力:
        list[tuple]: dist[v] = (主コスト, 副基準1, ...) の最良値タプル。
                     未到達は (INF, 0, 0, ...) 相当。

    補足:
        ヒープのキーは (primary, -secondary, ..., vertex) の形。
        better 関数を自分で定義すれば任意の多基準に対応可能。

    使用例（距離最小・木の数最大の2基準）:
        # g[v] = [(to, cost, tree_count), ...]
        dist = dijkstra_multi(g, 0)
        print(dist[N-1])  # (最短距離, 最大木の数)
    """
    INF_VAL = 10 ** 18
    n = len(g)
    init = tuple([INF_VAL] + [0] * (n_criteria - 1))
    dist = [init] * n
    start = tuple([0] * n_criteria)
    dist[s] = start

    def default_better(new_state: tuple, old_state: tuple) -> bool:
        """主: 小さいほど良い, 副: 大きいほど良い"""
        if new_state[0] < old_state[0]:
            return True
        if new_state[0] == old_state[0]:
            return new_state[1:] > old_state[1:]
        return False

    _better = better if better else default_better

    # ヒープキー: (primary, -secondary, vertex)
    def to_heap_key(state: tuple, v: int) -> tuple:
        return (state[0],) + tuple(-x for x in state[1:]) + (v,)

    pq = [to_heap_key(start, s)]

    while pq:
        entry = heapq.heappop(pq)
        v = entry[-1]
        cur_primary = entry[0]
        cur_rest = tuple(-x for x in entry[1:-1])
        cur_state = (cur_primary,) + cur_rest

        if not _better(cur_state, dist[v]) and cur_state != dist[v]:
            continue

        for edge in g[v]:
            to = edge[0]
            values = edge[1:]
            new_state = tuple(cur_state[i] + values[i] for i in range(n_criteria))
            if _better(new_state, dist[to]):
                dist[to] = new_state
                heapq.heappush(pq, to_heap_key(new_state, to))

    return dist

def TUPLE() -> tuple[int, ...]:
    return tuple(MAP())

def TUPLES(n: int) -> list[tuple[int, ...]]:
    return [TUPLE() for _ in range(n)]

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    ABCD = TUPLES(M)
    g = build_graph(N, ABCD)
    #debug(g)
    ans = dijkstra_multi(g, 0)
    pr(ans[N-1][0], ans[N-1][1])





















if __name__ == "__main__":
    main()