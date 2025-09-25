n, m = map(int, input().split())
li = [tuple(map(int, input().split())) for _ in range(m)]
di = {i: set() for i in range(n)}
for a, b in li:
    di[a - 1].add(b - 1)
    di[b - 1].add(a - 1)

for i, v in di.items():
    print(f"{i} : {" ".join(map(str, list(v)))}")