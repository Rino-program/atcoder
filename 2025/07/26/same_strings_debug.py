def debug_same_strings():
    print("=== 同じ文字列の処理デバッグ ===")
    
    n, k, x = 4, 2, 10
    s = ['a', 'a', 'b', 'a']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    print(f"n={n}, k={k}, x={x}")
    
    # 手動で全組み合わせを正確に生成
    print("\n手動での組み合わせ生成:")
    combinations = []
    for i in range(n):
        for j in range(n):
            combination = s_sorted[i] + s_sorted[j]
            combinations.append(combination)
            print(f"({i},{j}): '{s_sorted[i]}' + '{s_sorted[j]}' = '{combination}'")
    
    combinations.sort()
    print(f"\nソート後の全組み合わせ: {combinations}")
    print(f"10番目 (index 9): '{combinations[9]}'")
    
    # アルゴリズムのステップバイステップ実行
    print(f"\nアルゴリズム実行:")
    result = []
    remaining = x - 1  # 9
    print(f"初期remaining: {remaining}")
    
    for pos in range(k):
        print(f"\n位置 {pos + 1}:")
        for i in range(n):
            combinations_count = n ** (k - pos - 1)
            print(f"  インデックス {i} ('{s_sorted[i]}'): 組み合わせ数 = {combinations_count}")
            
            if remaining < combinations_count:
                result.append(s_sorted[i])
                print(f"  -> 選択: '{s_sorted[i]}'")
                break
            else:
                remaining -= combinations_count
                print(f"  -> スキップ, remaining = {remaining}")
    
    print(f"\n最終結果: {''.join(result)}")
    
    # 期待値と比較
    expected = combinations[x-1]
    actual = ''.join(result)
    print(f"期待値: '{expected}'")
    print(f"実際値: '{actual}'")
    print(f"一致: {expected == actual}")

if __name__ == "__main__":
    debug_same_strings()
