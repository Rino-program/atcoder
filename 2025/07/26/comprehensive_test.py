def comprehensive_test():
    print("=== 包括的テスト ===")
    
    # テストケース1: 制約内の複雑なケース
    test_cases = [
        {
            "n": 3, "k": 2, "x": 6,
            "s": ['abc', 'xxx', 'abc'],
            "description": "元のサンプル"
        },
        {
            "n": 4, "k": 2, "x": 10,
            "s": ['a', 'a', 'b', 'a'],
            "description": "同じ文字列が多い"
        },
        {
            "n": 2, "k": 3, "x": 5,
            "s": ['a', 'b'],
            "description": "シンプルなケース"
        },
        {
            "n": 3, "k": 1, "x": 2,
            "s": ['z', 'a', 'b'],
            "description": "K=1のケース"
        },
        {
            "n": 5, "k": 2, "x": 25,
            "s": ['e', 'd', 'c', 'b', 'a'],
            "description": "最大値のケース"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n--- テストケース {i+1}: {test['description']} ---")
        n, k, x = test['n'], test['k'], test['x']
        s = test['s']
        
        print(f"n={n}, k={k}, x={x}")
        print(f"文字列: {s}")
        
        # 全ての組み合わせを生成（ブルートフォース）
        def generate_all_combinations(strings, length):
            if length == 1:
                return strings[:]
            
            result = []
            for string in strings:
                for sub_combo in generate_all_combinations(strings, length - 1):
                    result.append(string + sub_combo)
            return result
        
        s_sorted = sorted(s)
        all_combinations = generate_all_combinations(s_sorted, k)
        all_combinations.sort()
        
        print(f"総組み合わせ数: {len(all_combinations)}")
        if len(all_combinations) >= x:
            print(f"期待値 (x={x}番目): '{all_combinations[x-1]}'")
        else:
            print(f"ERROR: x={x}が総組み合わせ数{len(all_combinations)}を超えています")
            continue
        
        # 現在のアルゴリズム実行
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
        
        actual = ''.join(result)
        expected = all_combinations[x-1]
        
        print(f"アルゴリズム結果: '{actual}'")
        print(f"一致: {expected == actual}")
        
        if expected != actual:
            print(f"*** MISMATCH: 期待値='{expected}', 実際値='{actual}' ***")

if __name__ == "__main__":
    comprehensive_test()
