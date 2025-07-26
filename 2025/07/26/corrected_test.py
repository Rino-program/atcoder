from collections import Counter

def test_corrected_algorithm():
    print("=== 修正版アルゴリズムのテスト ===")
    
    n, k, x = 4, 2, 10
    s = ['a', 'a', 'b', 'a']
    s_sorted = sorted(s)
    
    print(f"元: {s}")
    print(f"ソート後: {s_sorted}")
    print(f"n={n}, k={k}, x={x}")
    
    # ユニークな文字列とその出現回数を取得
    unique_strings = []
    counts = []
    
    i = 0
    while i < n:
        current_string = s_sorted[i]
        count = 0
        while i < n and s_sorted[i] == current_string:
            count += 1
            i += 1
        unique_strings.append(current_string)
        counts.append(count)
    
    print(f"ユニークな文字列: {unique_strings}")
    print(f"出現回数: {counts}")
    
    # アルゴリズム実行
    result = []
    remaining = x - 1  # 9
    print(f"\n初期remaining: {remaining}")
    
    for pos in range(k):
        print(f"\n位置 {pos + 1}:")
        for i, (string, count) in enumerate(zip(unique_strings, counts)):
            combinations = count * (n ** (k - pos - 1))
            print(f"  文字列 '{string}' (出現{count}回): 組み合わせ数 = {combinations}")
            
            if remaining < combinations:
                result.append(string)
                print(f"  -> 選択: '{string}'")
                break
            else:
                remaining -= combinations
                print(f"  -> スキップ, remaining = {remaining}")
    
    print(f"\n最終結果: {''.join(result)}")
    
    # 検証
    all_combinations = []
    for i in range(n):
        for j in range(n):
            all_combinations.append(s_sorted[i] + s_sorted[j])
    
    all_combinations.sort()
    expected = all_combinations[x-1]
    actual = ''.join(result)
    
    print(f"期待値: '{expected}'")
    print(f"実際値: '{actual}'")
    print(f"一致: {expected == actual}")

if __name__ == "__main__":
    test_corrected_algorithm()
