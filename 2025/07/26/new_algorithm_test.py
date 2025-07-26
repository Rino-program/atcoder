def test_new_algorithm():
    print("=== 新しいアルゴリズムのテスト ===")
    
    # テストケース
    test_cases = [
        {
            "n": 3, "k": 2, "x": 6,
            "s": ['abc', 'xxx', 'abc']
        },
        {
            "n": 4, "k": 2, "x": 10,
            "s": ['a', 'a', 'b', 'a']
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n--- テストケース {i+1} ---")
        n, k, x = test['n'], test['k'], test['x']
        s = test['s']
        
        print(f"n={n}, k={k}, x={x}")
        print(f"文字列: {s}")
        
        # 新しいアルゴリズム
        def generate_combinations(strings, length):
            if length == 1:
                return strings[:]
            
            result = []
            for string in strings:
                for sub_combo in generate_combinations(strings, length - 1):
                    result.append(string + sub_combo)
            return result
        
        s_sorted = sorted(s)
        all_combinations = generate_combinations(s_sorted, k)
        all_combinations.sort()
        
        print(f"ソート済み文字列: {s_sorted}")
        print(f"全組み合わせ: {all_combinations}")
        print(f"結果: '{all_combinations[x-1]}'")

if __name__ == "__main__":
    test_new_algorithm()
