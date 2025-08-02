n = int(input())
a = list(map(int, input().split()))
s = 0
for i, ai in enumerate(a):
    for j, aj in enumerate(a):
        if (i - j) == (ai + aj):
            s += 1
print(s)