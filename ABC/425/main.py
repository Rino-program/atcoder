import sys
from collections import defaultdict, deque, Counter
from itertools import permutations, combinations, product
from bisect import bisect_left, bisect_right
import heapq
import math
from functools import lru_cache
import re

# 高速入力
def input():
    return sys.stdin.readline().strip()



def main():
    n, q = map(int, input().split())
    a = list(map(int, input().split()))
    z = 0 # ずれ
    # 区間和の前計算
    prefix_sum = [0] * (n + 1)
    for i in range(n):
        prefix_sum[i + 1] = prefix_sum[i] + a[i]
    
    query = [list(map(int, input().split())) for _ in range(q)]
    for i in query:
        if len(i) == 3:
            _, l, r = i
            if (na := r + z) >= n:
                print(prefix_sum[(r + z - n)] + prefix_sum[n] - prefix_sum[l + z - 1])
            else:
                print(prefix_sum[(na) % (n)] - prefix_sum[(l + z - 1) % (n)])
        else:
            _, x = i
            if x != n:z = (z + x) % n

if __name__ == "__main__":
    main()