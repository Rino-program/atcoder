import sys

def main():
    data = list(map(int, sys.stdin.read().split()))
    X, Y, Z = data
    if (X - Z * Y) >= 0 and (X - Z * Y) % (Z - 1) == 0:
        print("Yes")
    else:
        print("No")

if __name__ == '__main__':
    main()
