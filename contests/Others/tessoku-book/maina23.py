# coding: utf-8
import sys
from collections import deque, defaultdict, Counter
from bisect import bisect_left, bisect_right
import heapq
import math
from copy import deepcopy
import string
sys.setrecursionlimit(10 ** 6)

# ===== 入出力ヘルパ =====
def input() -> str:
    return sys.stdin.readline().rstrip()
def INT() -> int:
    return int(input())
def MAP():
    return map(int, input().split())
def LIST() -> list[int]:
    return list(MAP())

# ===== 定数 =====
INF = 10 ** 18

# ==============================================
# =================== main =====================
# ==============================================
def main() -> None:
    # 入力
    N, M = MAP()
    
    # dp[i][S] = i枚のクーポン券を使ったとき、
    # 状態S（どの品物を買ったか）に到達する最小クーポン券枚数
    dp = [[INF for _ in range(1 << N)] for _ in range(M + 1)]
    
    # 初期状態：0枚使用時は何も買ってない状態（S=0）
    dp[0][0] = 0
    
    # 各クーポン券を処理
    for i in range(M):
        # i番目のクーポン券で買える品物を読み込む
        coupon_items = LIST()  # N個の0or1
        
        # このクーポン券で買える品物をビットマスクに変換
        # 例：[1, 0, 1] → 0b101 (品物0と品物2が買える)
        mask = 0
        for j in range(N):
            if coupon_items[j] == 1:
                mask |= (1 << j)
        
        # dp[i]からdp[i+1]への遷移
        for state in range(1 << N):
            # このクーポン券を使わない場合
            # 前のレベルの状態をそのまま引き継ぐ
            dp[i + 1][state] = min(dp[i + 1][state], dp[i][state])
            
            # このクーポン券を使う場合
            if dp[i][state] < INF:  # 到達可能な状態のみ処理
                new_state = state | mask  # 現在の状態にmaskで買える品物を追加
                dp[i + 1][new_state] = min(
                    dp[i + 1][new_state],
                    dp[i][state] + 1  # クーポン券1枚追加
                )
    
    # 全品物を買った状態（すべてのビットが立った状態）
    all_items = (1 << N) - 1
    
    # M枚以内で全品物に到達する最小枚数を求める
    answer = min(dp[i][all_items] for i in range(M + 1))
    if answer == INF:
        print(-1)
    else:
        print(answer)

if __name__ == "__main__":
    main()