from collections import Counter

def analyze_original_approach():
    print("=== 元のa.pyのアプローチを分析 ===")
    
    # サンプルデータ
    n, k, x = 3, 2, 6
    s = ['abc', 'xxx', 'abc']
    
    print(f"n={n}, k={k}, x={x}")
    print(f"元の文字列: {s}")
    
    # ソートして、各文字列のインデックスを取得
    so = sorted(s)
    print(f"ソート済み: {so}")
    
    li = []
    for i in s:
        li.append(so.index(i))
    
    print(f"インデックスリスト: {li}")
    
    c = dict(Counter(li))
    print(f"インデックスの出現回数: {c}")
    
    # このアプローチの問題点を確認
    print("\n問題点の分析:")
    print("- so.index(i)は最初に見つかったインデックスを返すため、")
    print("  同じ文字列が複数ある場合に情報が失われる")
    
    # 正しい方法との比較
    print("\n正しい方法:")
    s_sorted = sorted(s)
    print(f"単純ソート: {s_sorted}")
    
    # 全組み合わせを生成
    all_combinations = []
    for i in range(n):
        for j in range(n):
            all_combinations.append(s_sorted[i] + s_sorted[j])
    
    all_combinations.sort()
    print(f"全組み合わせ: {all_combinations}")
    print(f"6番目: {all_combinations[x-1]}")

def test_improved_index_approach():
    print("\n=== 改良されたインデックスアプローチ ===")
    
    n, k, x = 3, 2, 6
    s = ['abc', 'xxx', 'abc']
    
    # ユニークな文字列とその出現回数を取得
    unique_strings = sorted(list(set(s)))
    counts = [s.count(string) for string in unique_strings]
    
    print(f"ユニークな文字列: {unique_strings}")
    print(f"出現回数: {counts}")
    
    # 辞書順でX番目の文字列を構築
    result = []
    remaining = x - 1
    
    for pos in range(k):
        for i, (string, count) in enumerate(zip(unique_strings, counts)):
            # この文字列を選んだ場合の組み合わせ数
            combinations = count * (n ** (k - pos - 1))
            
            if remaining < combinations:
                result.append(string)
                break
            else:
                remaining -= combinations
    
    print(f"結果: {''.join(result)}")

if __name__ == "__main__":
    analyze_original_approach()
    test_improved_index_approach()
