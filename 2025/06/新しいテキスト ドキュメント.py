n, q = map(int, input().split())
a = list(map(int, input().split()))
k = []
s = 0

def safe_index(lst, item):
    try:
        return lst.index(item)
    except ValueError:
        return -1
t = []
for i in a:
    if i in k:
        li = [-1] + k + [-1]
        j = safe_index(li, i)
        l = li[j - 1]
        r = li[j + 1]
        if l == i - 1 and r == i + 1:
            s += 1
        elif l != i - 1 and r != i + 1:
            s -= 1
        k.remove(i)
        t.append(str(s))
    else:
        k.append(i)
        k.sort()
        li = [-1] + k + [-1]
        j = safe_index(li, i)
        l = li[j - 1]
        r = li[j + 1]
        if l == i - 1 and r == i + 1:
            s -= 1
        elif l != i - 1 and r != i + 1:
            s += 1
        t.append(str(s))
print("\n".join(t))