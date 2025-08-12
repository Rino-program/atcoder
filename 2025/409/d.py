n = list(map(int, input().split()))
n += n
for i in range(3):
    if n[i] + n[i+1] == n[i+2]:
        print("Yes")
        break
else:
    print("No")