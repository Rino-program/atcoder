# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
from collections import deque
import heapq

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

def TUPLES(n: int) -> list[tuple[int, ...]]:
    return [TUPLE() for _ in range(n)]

INF = 10**9

# ==============================================
# =================== main =====================
# ==============================================

def dijkstra(g: list[list[tuple[int, int]]], s: int) -> list[int]:
    """概要:
        非負重みグラフで始点 s からの最短距離を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト。
        s (int): 始点。
    出力:
        list[int]: 各頂点への最短距離（未到達は INF）。
    補足:
        計算量は O((V+E)logV)。負辺は非対応。
    """
    dist = [INF] * len(g)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]: continue
        for to, w in g[v]:
            if dist[v] + w < dist[to]:
                dist[to] = dist[v] + w
                heapq.heappush(pq, (dist[to], to))
    return dist

def main() -> None:
    # ここに解答を書く
    N, M = MAP()
    CR = TUPLES(N)
    g = [[] for _ in range(N)]
    for i in range(M):
        a, b = MAP()
        a -= 1
        b -= 1
        g[a].append(b)
        g[b].append(a)
    gn = [[] for _ in range(N)]
    for i in range(N):
        C, R = CR[i]
        f = [1] * N
        d = deque()
        d.append((i, 0))
        f[i] = 0
        s = set()
        s.add(i)
        while d:
            v, num = d.popleft()
            if num == R:
                continue
            for w in g[v]:
                if f[w]:
                    f[w] ^= 1
                    d.append((w, num + 1))
                    s.add(w)
        #debug(i, s)
        for v in s:
            gn[i].append((v, C))
    del g
    ans = dijkstra(gn, 0)[-1]
    print(ans)





















if __name__ == "__main__":
    main()
