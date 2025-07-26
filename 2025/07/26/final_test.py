def final_verification():
    print("=== 最終検証 ===")
    
    # 問題のケース
    n, k, x = 4, 2, 10
    s = ['a', 'a', 'b', 'a']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    
    # 実際の組み合わせを位置ごとに確認
    print("\n実際の組み合わせ（インデックスベース）:")
    combinations_with_index = []
    for i in range(n):
        for j in range(n):
            combination = s_sorted[i] + s_sorted[j]
            combinations_with_index.append((i, j, combination))
            print(f"({i},{j}): {combination}")
    
    # 辞書順にソート
    combinations_with_index.sort(key=lambda x: x[2])
    print(f"\n辞書順ソート後:")
    for idx, (i, j, combination) in enumerate(combinations_with_index):
        print(f"{idx+1:2d}: ({i},{j}) -> {combination}")
    
    print(f"\n10番目の組み合わせ: {combinations_with_index[9][2]}")
    print(f"そのインデックス: ({combinations_with_index[9][0]}, {combinations_with_index[9][1]})")
    
    # アルゴリズム実行
    print(f"\nアルゴリズム実行:")
    result = []
    remaining = x - 1  # 9
    
    for pos in range(k):
        print(f"\n位置 {pos + 1}, remaining = {remaining}:")
        for i in range(n):
            combinations = n ** (k - pos - 1)
            print(f"  インデックス {i}: 組み合わせ数 = {combinations}")
            
            if remaining < combinations:
                result.append(s_sorted[i])
                print(f"  -> 選択: {s_sorted[i]} (インデックス {i})")
                break
            else:
                remaining -= combinations
                print(f"  -> スキップ, remaining = {remaining}")
    
    print(f"\n結果: {''.join(result)}")
    
    # 期待値と実際の値
    expected = combinations_with_index[9][2]
    actual = ''.join(result)
    print(f"\n期待値: {expected}")
    print(f"実際値: {actual}")
    print(f"一致: {expected == actual}")

if __name__ == "__main__":
    final_verification()
