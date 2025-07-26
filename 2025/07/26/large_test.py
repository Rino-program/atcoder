def test_large_strings():
    print("=== 大きな文字列のテスト ===")
    
    # 長い文字列での挙動テスト
    n, k, x = 3, 5, 100
    
    # 長い文字列を作成
    s = ['a' * 1000, 'b' * 1000, 'c' * 1000]
    s_sorted = sorted(s)
    
    print(f"文字列の長さ: {len(s_sorted[0])}")
    print(f"n={n}, k={k}, x={x}")
    
    result = []
    remaining = x - 1
    
    for pos in range(k):
        for i in range(n):
            combinations = n ** (k - pos - 1)
            
            if remaining < combinations:
                result.append(s_sorted[i])
                break
            else:
                remaining -= combinations
    
    result_string = ''.join(result)
    print(f"結果の文字列長: {len(result_string)}")
    print(f"メモリ使用量概算: {len(result_string) * 8} bytes = {len(result_string) * 8 / 1024} KB")
    
    # 最初と最後の50文字だけ表示
    if len(result_string) > 100:
        print(f"結果の一部: '{result_string[:50]}...{result_string[-50:]}'")
    else:
        print(f"結果: '{result_string}'")

def test_boundary_conditions():
    print("\n=== 境界条件のテスト ===")
    
    # X = N^K の場合（最大値）
    print("X = 最大値のケース:")
    n, k = 3, 4
    x = n ** k  # 81
    print(f"n={n}, k={k}, x={x} (最大値)")
    
    s = ['z', 'y', 'x']
    s_sorted = sorted(s)
    
    result = []
    remaining = x - 1  # 80
    
    print(f"初期remaining: {remaining}")
    
    for pos in range(k):
        found = False
        for i in range(n):
            combinations = n ** (k - pos - 1)
            print(f"  位置{pos+1}, 文字列{i}: combinations={combinations}, remaining={remaining}")
            
            if remaining < combinations:
                result.append(s_sorted[i])
                print(f"  -> 選択: {s_sorted[i]}")
                found = True
                break
            else:
                remaining -= combinations
                print(f"  -> スキップ, new remaining={remaining}")
        
        if not found:
            print(f"  -> 該当なし、最後の文字列を選択")
            result.append(s_sorted[-1])
    
    print(f"最終結果: {''.join(result)}")
    print(f"期待値: {''.join([s_sorted[-1]] * k)}")  # 最後の文字列をk回

if __name__ == "__main__":
    test_large_strings()
    test_boundary_conditions()
