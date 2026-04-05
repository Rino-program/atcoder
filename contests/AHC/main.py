N, M, C = map(int, input().split())
li = ["R", "U", "L", "D"]
print("\n".join(["D" for i in range(N-5)]))
"""for i in range((N-1)*3-1):
    print(li[(i // (N-1)) % 4])"""
print("R")
limit = N - 1
i = -1
now = 0
while limit > 0:
    if i == -1:
        print("U")
    now += 1
    if i == 1:
        print("D")
    if now == N-1:
        now = 0
        limit -= 1
        i = i * -1
        if limit: print("R")

"""li.insert(0, "D")
li.pop()
while N != 2:
    N -= 2
    for i in range(-1, (N)*4-1):
        if i == -1:
            print("D")
            continue
        print(li[(i // (N-1)) % 4])"""