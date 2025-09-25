#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AtCoder Python Template with Performance Monitoring
"""

import sys
import time
import tracemalloc
from collections import defaultdict, deque, Counter
from itertools import combinations, permutations, product, accumulate
from bisect import bisect_left, bisect_right
from math import gcd, lcm, sqrt, ceil, floor
import heapq

# 高速入出力設定
input = sys.stdin.readline

def solve():
    """
    メイン処理をここに記述
    戻り値: 解答文字列（出力チェック用）
    """
    # TODO: 問題に応じて実装
    n = int(input())
    return str(n)

def main():
    """実行時間とメモリ使用量を測定して実行"""
    tracemalloc.start()
    start_time = time.perf_counter()
    
    try:
        result = solve()
        if result is not None:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1
    
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # パフォーマンス情報をstderrに出力（提出時は削除）
    execution_time = (end_time - start_time) * 1000  # ms
    memory_mb = peak / 1024 / 1024  # MB
    
    print(f"[Performance] Time: {execution_time:.2f}ms, Memory: {memory_mb:.2f}MB", file=sys.stderr)
    
    # TLE/MLE警告
    if execution_time > 2000:  # 2秒
        print("⚠️  TLE Warning: Execution time > 2000ms", file=sys.stderr)
    if memory_mb > 512:  # 512MB
        print("⚠️  MLE Warning: Memory usage > 512MB", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())