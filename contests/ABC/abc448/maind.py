# coding: utf-8
# AtCoder Competition Template v2 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
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
    return sys.stdin.readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())

def TUPLE() -> tuple[int, int]:
    return tuple(MAP())

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def TUPLES(n: int) -> list[tuple[int, int]]:
    return [TUPLE() for _ in range(n)]

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

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    for row in grid:
        print(sep.join(map(str, row)))


# ==============================================
# =================== main =====================
# ==============================================

def build_graph(n: int, edges, directed: bool = False) -> list[list[int]]:
    """概要:
        辺集合から重みなしグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数（0-indexed を想定）。
        edges (list[tuple[int, int]]): 辺 (a, b) の配列。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[int]]: 隣接リスト。
    補足:
        無向時は両方向に辺を追加する。
    """
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a-1]. append(b-1)
        if not directed:
            g[b-1].append(a-1)
    return g

def main() -> None:
    # ここに解答を書く
    N = INT()
    A = LIST()
    UV = LISTS(N-1)
    g = build_graph(N, UV)
    seisu = defaultdict(int)
    seisu[A[0]] = 1
    rirekilist = []
    rirekilist.append(0)
    flag = [False] * N
    dup_count = 0  # 重複している値の種類数
    next_idx = [0] * N  # 各ノードで次に探索すべき隣接ノードのインデックス
    now = 0
    end = 0
    now = g[now][0]
    Allrireki = [False] * N
    Allrireki[0] = True
    visited_count = 1  # 訪問済みノード数
    just_backtracked = False  # 戻ってきた直後かどうかのフラグ
    while visited_count < N:
        # 戻ってきた直後でなければ、ノードを処理
        if not just_backtracked:
            Allrireki[now] = True
            visited_count += 1
            rirekilist.append(now)
            if seisu[A[now]] == 1: # 1から2になる = 重複発生
                dup_count += 1
            seisu[A[now]] += 1
            if dup_count > 0:
                flag[now] = True
        just_backtracked = False
        # 次に探索すべき隣接ノードを探す
        idx = next_idx[now]
        found = False
        while idx < len(g[now]):
            i = g[now][idx]
            if not Allrireki[i]:  # i が未訪問の場合
                next_idx[now] = idx + 1  # 次回はその次から探索
                now = i
                found = True
                break
            idx += 1
        
        if not found:
            end = 1  # すべての隣接頂点が既に訪問済みの場合
        if end: # 戻る
            if len(rirekilist) <= 1: # 戻る先がない場合
                break
            seisu[A[now]] -= 1 # 現在のノードの値をカウントから減らす
            if seisu[A[now]] == 1: # 2から1になる = 重複解消
                dup_count -= 1
            rirekilist.pop() # 現在のノードをリストから削除
            now = rirekilist[-1] # 親ノードを now に設定（削除しない）
            end = 0
            just_backtracked = True  # 戻ってきたことを記録
    for i in flag:
        if i:
            Yes()
        else:
            No()



















if __name__ == "__main__":
    main()