from collections import deque

s = deque()
x = input()
for c in x:
    if c == "0":
        if s and s[-1] == "1":
            s.pop()
        else:
            s.append(c)
    elif c == "1":
        if s and s[-1] == "0":
            s.pop()
        else:
            s.append(c)

print(len(x) - len(s))