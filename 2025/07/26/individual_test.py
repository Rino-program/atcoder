def test_individual():
    print("=== 個別テスト ===")
    
    # テストデータ
    n, k, x = 4, 2, 10
    s = ['a', 'a', 'b', 'a']
    
    print(f"入力: n={n}, k={k}, x={x}, s={s}")
    
    # アプローチ1: 元の配列をそのままソート
    print("\n--- アプローチ1: 元の配列をソート ---")
    s_sorted = sorted(s)
    print(f"ソート済み: {s_sorted}")
    
    result1 = []
    remaining = x - 1
    
    for pos in range(k):
        for i in range(n):
            combinations = n ** (k - pos - 1)
            if remaining < combinations:
                result1.append(s_sorted[i])
                break
            else:
                remaining -= combinations
    
    print(f"結果: {''.join(result1)}")
    
    # アプローチ2: ブルートフォース（正解）
    print("\n--- アプローチ2: ブルートフォース ---")
    def generate_combinations(strings, length):
        if length == 1:
            return strings[:]
        
        result = []
        for string in strings:
            for sub_combo in generate_combinations(strings, length - 1):
                result.append(string + sub_combo)
        return result
    
    all_combinations = generate_combinations(s_sorted, k)
    all_combinations.sort()
    
    print(f"全組み合わせ: {all_combinations}")
    print(f"10番目: '{all_combinations[x-1]}'")
    
    # 比較
    print(f"\nアプローチ1の結果: {''.join(result1)}")
    print(f"正解: {all_combinations[x-1]}")
    print(f"一致: {':'.join(result1) == all_combinations[x-1]}")

if __name__ == "__main__":
    test_individual()
