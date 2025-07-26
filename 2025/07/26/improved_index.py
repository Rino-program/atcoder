from collections import Counter

def solve_with_index_approach():
    # 入力を読み込む
    n, k, x = map(int, input().split())
    s = []
    for _ in range(n):
        s.append(input().strip())
    
    # ユニークな文字列を辞書順にソートして、出現回数を取得
    unique_strings = sorted(list(set(s)))
    counts = [s.count(string) for string in unique_strings]
    
    # 辞書順でX番目の文字列を構築
    result = []
    remaining = x - 1  # 0-indexedにする
    
    for pos in range(k):
        # この位置で各ユニークな文字列を選んだ場合の組み合わせ数を計算
        for i, (string, count) in enumerate(zip(unique_strings, counts)):
            # この文字列を選んだ場合の残りの組み合わせ数
            combinations = count * (n ** (k - pos - 1))
            
            if remaining < combinations:
                # この文字列を選択
                result.append(string)
                break
            else:
                # この文字列をスキップ
                remaining -= combinations
    
    # 結果を連結して出力
    print(''.join(result))

# テスト用の関数
def test_index_approach():
    print("=== インデックスアプローチのテスト ===")
    
    test_cases = [
        {
            "n": 3, "k": 2, "x": 6,
            "s": ['abc', 'xxx', 'abc'],
            "expected": "abcxxx"
        },
        {
            "n": 4, "k": 2, "x": 10,
            "s": ['a', 'a', 'b', 'a'],
            "expected": "ab"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nテストケース {i+1}:")
        n, k, x = test['n'], test['k'], test['x']
        s = test['s']
        
        print(f"入力: n={n}, k={k}, x={x}, s={s}")
        
        # インデックスアプローチ
        unique_strings = sorted(list(set(s)))
        counts = [s.count(string) for string in unique_strings]
        
        print(f"ユニークな文字列: {unique_strings}")
        print(f"出現回数: {counts}")
        
        result = []
        remaining = x - 1
        
        for pos in range(k):
            print(f"\n位置 {pos + 1}, remaining = {remaining}:")
            for j, (string, count) in enumerate(zip(unique_strings, counts)):
                combinations = count * (n ** (k - pos - 1))
                print(f"  文字列 '{string}' (出現{count}回): 組み合わせ数 = {combinations}")
                
                if remaining < combinations:
                    result.append(string)
                    print(f"  -> 選択: '{string}'")
                    break
                else:
                    remaining -= combinations
                    print(f"  -> スキップ, remaining = {remaining}")
        
        actual = ''.join(result)
        print(f"\n結果: '{actual}'")
        print(f"期待値: '{test['expected']}'")
        print(f"一致: {actual == test['expected']}")

if __name__ == "__main__":
    test_index_approach()
