def test_potential_issues():
    print("=== 潜在的な問題のテスト ===")
    
    # 問題1: 入力の改行文字の問題
    print("1. 入力処理のテスト")
    test_strings = ['abc\n', 'def', 'ghi\r\n']
    processed = []
    for s in test_strings:
        processed.append(s.strip())
    print(f"元: {test_strings}")
    print(f"処理後: {processed}")
    print()
    
    # 問題2: 大きなxでのオーバーフロー
    print("2. 大きなXでのテスト")
    n, k, x = 50, 10, 10**18
    
    # 最大組み合わせ数をチェック
    max_combinations = n ** k
    print(f"n={n}, k={k}")
    print(f"最大組み合わせ数: {max_combinations}")
    print(f"x: {x}")
    
    if x > max_combinations:
        print("ERROR: xが最大組み合わせ数を超えています")
    else:
        print("OK: xは有効範囲内です")
    print()
    
    # 問題3: 同じ文字列が複数ある場合の処理
    print("3. 同じ文字列が複数ある場合")
    n, k, x = 4, 2, 10
    s = ['a', 'a', 'b', 'a']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    
    # 全組み合わせを生成
    all_combinations = []
    for i in range(n):
        for j in range(n):
            all_combinations.append(s_sorted[i] + s_sorted[j])
    
    all_combinations.sort()
    print(f"全組み合わせ: {all_combinations}")
    print(f"10番目: {all_combinations[x-1]}")
    
    # アルゴリズム実行
    result = []
    remaining = x - 1
    
    for pos in range(k):
        found = False
        for i in range(n):
            combinations = n ** (k - pos - 1)
            if remaining < combinations:
                result.append(s_sorted[i])
                found = True
                break
            else:
                remaining -= combinations
        if not found:
            result.append(s_sorted[-1])
    
    print(f"アルゴリズム結果: {''.join(result)}")
    print()
    
    # 問題4: 空文字列の処理
    print("4. 空文字列のテスト")
    n, k, x = 2, 2, 3
    s = ['', 'a']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    
    # アルゴリズム実行
    result = []
    remaining = x - 1
    
    for pos in range(k):
        found = False
        for i in range(n):
            combinations = n ** (k - pos - 1)
            if remaining < combinations:
                result.append(s_sorted[i])
                found = True
                break
            else:
                remaining -= combinations
        if not found:
            result.append(s_sorted[-1])
    
    print(f"結果: '{':'.join(result)}'")

if __name__ == "__main__":
    test_potential_issues()
