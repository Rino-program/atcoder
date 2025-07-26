def test_algorithm():
    # テストケース1: 元のサンプル
    print("=== テストケース1 ===")
    n, k, x = 3, 2, 6
    s = ['abc', 'xxx', 'abc']
    s_sorted = sorted(s)
    print(f"元の文字列: {s}")
    print(f"ソート済み: {s_sorted}")
    
    # 全ての組み合わせを生成
    all_combinations = []
    for i in range(n):
        for j in range(n):
            all_combinations.append(s_sorted[i] + s_sorted[j])
    all_combinations.sort()
    print(f"全組み合わせ: {all_combinations}")
    print(f"6番目: {all_combinations[x-1]}")
    
    # アルゴリズム実行
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
    
    print(f"アルゴリズム結果: {''.join(result)}")
    print()
    
    # テストケース2: より複雑なケース
    print("=== テストケース2 ===")
    n, k, x = 2, 3, 5
    s = ['a', 'b']
    s_sorted = sorted(s)
    print(f"元の文字列: {s}")
    print(f"ソート済み: {s_sorted}")
    
    # 全ての組み合わせを生成
    all_combinations = []
    for i in range(n):
        for j in range(n):
            for l in range(n):
                all_combinations.append(s_sorted[i] + s_sorted[j] + s_sorted[l])
    all_combinations.sort()
    print(f"全組み合わせ: {all_combinations}")
    print(f"5番目: {all_combinations[x-1]}")
    
    # アルゴリズム実行
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
    
    print(f"アルゴリズム結果: {''.join(result)}")
    print()
    
    # テストケース3: 異なる文字列の場合
    print("=== テストケース3 ===")
    n, k, x = 3, 2, 7
    s = ['z', 'a', 'b']
    s_sorted = sorted(s)
    print(f"元の文字列: {s}")
    print(f"ソート済み: {s_sorted}")
    
    # 全ての組み合わせを生成
    all_combinations = []
    for i in range(n):
        for j in range(n):
            all_combinations.append(s_sorted[i] + s_sorted[j])
    all_combinations.sort()
    print(f"全組み合わせ: {all_combinations}")
    print(f"7番目: {all_combinations[x-1]}")
    
    # アルゴリズム実行
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
    
    print(f"アルゴリズム結果: {''.join(result)}")

if __name__ == "__main__":
    test_algorithm()
