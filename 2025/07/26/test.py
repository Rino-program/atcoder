n, l, r = tuple(map(int, input().split()))
s = input()
print("Yes"if all([i == 'o' for i in s[l - 1:r]]) else "No")
