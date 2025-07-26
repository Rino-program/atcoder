def test_different_strings():
    print("=== 異なる文字列でのテスト ===")
    
    # 全て異なる文字列のケース
    n, k, x = 3, 2, 6
    s = ['abc', 'def', 'xyz']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    
    # 全組み合わせ
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
    expected = all_combinations[x-1]
    actual = ''.join(result)
    print(f"一致: {expected == actual}")

if __name__ == "__main__":
    test_different_strings()
