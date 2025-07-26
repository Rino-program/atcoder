def test_edge_cases():
    print("=== エッジケース検証 ===")
    
    # ケース1: X=1の場合
    print("ケース1: X=1")
    n, k, x = 3, 2, 1
    s = ['c', 'a', 'b']
    s_sorted = sorted(s)
    
    result = []
    remaining = x - 1  # 0
    
    for pos in range(k):
        for i in range(n):
            combinations = n ** (k - pos - 1)
            if remaining < combinations:
                result.append(s_sorted[i])
                break
            else:
                remaining -= combinations
    
    print(f"ソート済み: {s_sorted}")
    print(f"結果: {''.join(result)}")
    print(f"期待値: {s_sorted[0] + s_sorted[0]}")  # 最初の文字列2回
    print()
    
    # ケース2: X=最大値の場合
    print("ケース2: X=最大値")
    n, k, x = 2, 3, 8  # 2^3 = 8
    s = ['b', 'a']
    s_sorted = sorted(s)
    
    result = []
    remaining = x - 1  # 7
    
    for pos in range(k):
        for i in range(n):
            combinations = n ** (k - pos - 1)
            if remaining < combinations:
                result.append(s_sorted[i])
                break
            else:
                remaining -= combinations
    
    print(f"ソート済み: {s_sorted}")
    print(f"結果: {''.join(result)}")
    print(f"期待値: {s_sorted[1] + s_sorted[1] + s_sorted[1]}")  # 最後の文字列3回
    print()
    
    # ケース3: 大きなKでのオーバーフロー確認
    print("ケース3: 大きなK")
    n, k, x = 50, 10, 1000000000000000000
    
    # アルゴリズムが正常に動作するか確認
    try:
        result = []
        remaining = x - 1
        
        for pos in range(k):
            for i in range(n):
                combinations = n ** (k - pos - 1)
                if remaining < combinations:
                    result.append(f"s{i}")
                    break
                else:
                    remaining -= combinations
        
        print(f"大きなケースでの結果長: {len(result)}")
        print(f"最初の3要素: {result[:3]}")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    test_edge_cases()
