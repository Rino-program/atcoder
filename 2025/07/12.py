s = input()
li = []
for i, v in enumerate(list(s)):
    if v == "#":
        li.append(i + 1)

for l in range(0, len(li), 2):
    print(f"{li[l]},{li[l + 1]}")