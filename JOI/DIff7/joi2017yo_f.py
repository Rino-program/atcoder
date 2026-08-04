# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/contests/.template/main.py
# oj test -c 'C:\Rino-program\AtCoder\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
import sys
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

def LISTS(n: int) -> list[list[int]]:
    return [LIST() for _ in range(n)]

def TUPLES(n: int) -> list[tuple[int, ...]]:
    return [TUPLE() for _ in range(n)]

def LISTSI(n: int) -> list[int]:
    return [INT() for _ in range(n)]

hepu = heapq.heappush
hepo = heapq.heappop

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N, M, X = MAP()
    T = LISTSI(N)
    ABD = TUPLES(M)
    # 状態記憶せずにダイクストラする方針
    h = []
    g = [[] for _ in range(N)]
    for i in range(M):
        u, v, d = ABD.pop()
        u -= 1
        v -= 1
        g[u].append((v, d))
        g[v].append((u, d))
    del ABD
    hepu(h, (0, 0, 0, X))
    ans = -1
    dist = [[[False] * (X+1) for _ in range(3)] for _ in range(N)]
    while h:
        cost, now, mode, cut = hepo(h)
        if dist[now][mode][cut]:
            continue
        dist[now][mode][cut] = True
        if now == N - 1:
            ans = cost
            break
        for i in g[now]:
            nxt, nc = i
            nct = max(cut - nc, 0)
            nxc = cost + nc
            nmode = mode
            if nct == 0 and mode != 1:
                nmode = 1
            if nmode == T[nxt] != 1:
                hepu(h, (nxc, nxt, nmode, X))
            elif nmode == T[nxt]:
                hepu(h, (nxc, nxt, nmode, nct))
            elif T[nxt] == 1:
                hepu(h, (nxc, nxt, nmode, nct))
            elif nmode == 1:
                hepu(h, (nxc, nxt, T[nxt], X))
            elif nmode != 1 and nct == 0:
                hepu(h, (nxc, nxt, T[nxt], X))
    print(ans)





















if __name__ == "__main__":
    main()
