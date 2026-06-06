# coding: utf-8
# AtCoder Competition Template v2 (PyPy 7.3.20 / Python 3.11)
import sys

sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin. readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> list[int]:
    return list(MAP())



# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIR9 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

# ===== 文字列のリスト =====

# ===== よく使う出力関数 =====
pr = print # ただのさぼり。
def Yes(): print("Yes")
def No(): print("No")
def yes(): print("yes")
def no(): print("no")
def YES(): print("YES")
def NO(): print("NO")

# ============================================================
# main
# ============================================================

def main() -> None:
    # ここに解答を書く
    #out = Output()
    N = INT()
    Q = INT()
    hako = [list() for _ in range(N)]
    card = [list() for _ in range(2*(10**5))]
    for _ in range(Q):
        inp = LIST()
        if len(inp) == 3:
            _, i, j = inp
            hako[j-1].append(i)
            card[i-1].append(j)
        else:
            if inp[0] == 2:
                _, i = inp
                hako[i-1] = sorted(hako[i-1])
                print(" ".join(map(str, hako[i-1])))
            else:
                _, i = inp
                card[i-1] = sorted(list(set(card[i-1])))
                print(" ".join(map(str, card[i-1])))







if __name__ == "__main__":
    main()