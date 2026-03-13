# coding: utf-8
# AtCoder Competition Template v2.1 SHORT (PyPy 7.3.20 / Python 3.11)
# oj test -c 'C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe maina.py' -d input/a
from collections import defaultdict
import heapq

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    N: int = int(input())
    SC: list[list] = [list(map(int, input().split())) for _ in range(N)]
    ans: int = 0
    d: dict[int, int] = dict()
    for s, c in SC:
        d[s] = c
    S: list[int] = list(d.keys())
    heapq.heapify(S)
    se: set[int] = set()
    for s in S:
        se.add(s)
    while S:
        s: int = heapq.heappop(S)
        se.remove(s)
        tmp: int = d[s]
        ans += tmp % 2
        if tmp // 2 > 0:
            if s*2 not in d:
                d[s*2] = 0
            d[s*2] += tmp // 2
            if s*2 not in se:
                se.add(s*2)
                heapq.heappush(S, (s*2))
    print(ans)





















if __name__ == "__main__":
    main()