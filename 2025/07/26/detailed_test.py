def test_detailed():
    print("=== 詳細なデバッグ ===")
    
    # ケース: 境界条件での計算
    n, k, x = 3, 3, 27  # 3^3 = 27, 最大値
    s = ['c', 'b', 'a']
    s_sorted = sorted(s)
    
    print(f"n={n}, k={k}, x={x}")
    print(f"ソート済み: {s_sorted}")
    print(f"総組み合わせ数: {n**k}")
    
    result = []
    remaining = x - 1  # 26
    
    print(f"\n初期remaining: {remaining}")
    
    for pos in range(k):
        print(f"\n位置 {pos + 1}:")
        found = False
        for i in range(n):
            combinations = n ** (k - pos - 1)
            print(f"  文字列 {i} ('{s_sorted[i]}'): combinations={combinations}, remaining={remaining}")
            
            if remaining < combinations:
                result.append(s_sorted[i])
                print(f"  -> 選択: '{s_sorted[i]}'")
                found = True
                break
            else:
                remaining -= combinations
                print(f"  -> スキップ, new remaining={remaining}")
        
        if not found:
            print(f"  -> 見つからない場合、最後の文字列を選択")
            result.append(s_sorted[-1])
    
    print(f"\n最終結果: {''.join(result)}")
    
    # 検証: 実際に27番目を計算
    all_combinations = []
    for i in range(n):
        for j in range(n):
            for l in range(n):
                all_combinations.append(s_sorted[i] + s_sorted[j] + s_sorted[l])
    
    all_combinations.sort()
    print(f"実際の27番目: {all_combinations[26]}")

if __name__ == "__main__":
    test_detailed()
