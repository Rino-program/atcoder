# C - Sum of Numbers Greater Than Me
from collections import Counter
N = int(input())
A = list(map(int, input().split()))
A_sort = sorted(A)
C = dict(Counter(A_sort))
print(C, A_sort)
# 