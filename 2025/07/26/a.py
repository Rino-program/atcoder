from collections import deque, Counter
n, k, x = 3, 2, 6
s = ['abc', 'xxx', 'abc']
so = sorted(s)
li = []
for i in s:
    li.append(so.index(i))
c = dict(Counter(li))
def f(di_n, a = 0, c = 0, i = 1):
    if a == x:
        return a
    else:
        while a < x:
            b = di_n[a]
            if b * (n ** (k - i)) + c >= x:
                return f(di_n, a, c, i + 1)
            else:
                return f(di_n, a + b, c + b * (n ** (k - i)), i)