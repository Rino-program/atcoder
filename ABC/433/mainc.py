import sys
import math
from typing import List, Tuple, Optional, Set, Dict

sys.setrecursionlimit(10 ** 6)  # PyPy での再帰制限緩和

# 全て動くか試していないので、壊れているテンプレがあるかも？
# そしてテンプレあっても問題に確実に合うと判断しない限り使わない事があります。

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin.readline().rstrip()

def INT() -> int:
    return int(input())

def MAP():
    return map(int, input().split())

def LIST() -> List[int]:
    return list(MAP())

def STR() -> str:
    return input()

# ===== よく使う関数 =====
def Yes(): print("Yes")
def No(): print("No")

# ===== 問題ごとの関数定義 =====

# ===== main関数 =====
# AI解説AC
def main() -> None:
    # 制約10^7で大きめ。
    # つまり係数が少ない感じ？
    # これは三平方の定理と似ている。
    # 唯一違うのはnが二乗にならない事。
    # 約数の時はsqrt(N)まで探索すればいい。
    # この場合は？
    # N以下のいい整数(n)はどうやって求める？
    # それぞれに対してsqrt(n)をする？
    # それだとTLEする可能性がある。
    # 制約が大きいの厄介すぎる。
    # 10**7でどうなるか見てみる。
    # 全挙列？
    # そんなわけないよね？
    # O(logN)だとするとどんな感じなんだろう
    # O(logN)回数だと想定量の数値にならない。50 -> 3項目
    N = INT()
    li = [0]*N
    for i in range(1, int(math.sqrt(N))+ 1):
        for j in range(i+1, int(math.sqrt(N - i*i))+ 1):
            if i ** 2 + j ** 2 <= N:
                li[i ** 2 + j ** 2 - 1] += 1
    ans = []
    for i, v in enumerate(li):
        if v == 1:
            ans.append(i + 1)
    print(len(ans))
    print(" ".join(map(str, ans)))
    """out = {}
    f = False
    for i in range(5, 10**7+1):
        ans = set()
        for j in range(1, 121):
            for k in range(i, 3161):
                if j ** 2 + k ** 2 == i:
                    ans.add(i)
                    ans.add(j)
                    f = True
                    break
            if f:
                f = False
                break
        if i % 10==0:print(i)
        out[i] = "["+",".join(map(str, list(ans)))+"]"
    print(out)"""
    """tei = 0
    for i in range(1, 121):
        for j in range(i, 3161):
            tei += 1
            if i ** 2 + j ** 2 == 10 ** 7:
                Yes()
                print(tei, i, j)
                sys.exit()
    No()"""










if __name__ == "__main__":
    main()
