from collections import Counter

def solve_efficient():
    # 入力を読み込む
    n, k, x = map(int, input().split())
    s = []
    for _ in range(n):
        s.append(input().strip())
    
    # 元の配列をソート（インデックスベースで処理）
    s_sorted = sorted(s)
    
    # 辞書順でX番目の文字列を構築
    result = []
    remaining = x - 1  # 0-indexedにする
    
    for pos in range(k):
        # この位置で各文字列を選んだ場合の組み合わせ数を計算
        for i in range(n):
            # この文字列を選んだ場合の残りの組み合わせ数
            combinations = n ** (k - pos - 1)
            
            if remaining < combinations:
                # この文字列を選択
                result.append(s_sorted[i])
                break
            else:
                # この文字列をスキップ
                remaining -= combinations
    
    # 結果を連結して出力
    print(''.join(result))

# より効率的なアプローチ（ユニークな文字列ベース）
def solve_very_efficient():
    # 入力を読み込む
    n, k, x = map(int, input().split())
    s = []
    for _ in range(n):
        s.append(input().strip())
    
    # ユニークな文字列とその出現回数
    from collections import OrderedDict
    string_counts = OrderedDict()
    for string in sorted(set(s)):
        string_counts[string] = s.count(string)
    
    result = []
    remaining = x - 1
    
    for pos in range(k):
        for string, count in string_counts.items():
            # この文字列を選んだ場合の組み合わせ数
            combinations = count * (n ** (k - pos - 1))
            
            if remaining < combinations:
                result.append(string)
                break
            else:
                remaining -= combinations
    
    print(''.join(result))

# 最もシンプルで確実なアプローチ
def solve_simple():
    # 入力を読み込む
    n, k, x = map(int, input().split())
    s = []
    for _ in range(n):
        s.append(input().strip())
    
    # 全ての組み合わせを生成
    def generate_combinations(strings, length):
        if length == 1:
            return strings[:]
        
        result = []
        for string in strings:
            for sub_combo in generate_combinations(strings, length - 1):
                result.append(string + sub_combo)
        return result
    
    # 文字列を辞書順にソート
    s_sorted = sorted(s)
    
    # 全組み合わせを生成して辞書順にソート
    all_combinations = generate_combinations(s_sorted, k)
    all_combinations.sort()
    
    # X番目の文字列を出力
    print(all_combinations[x - 1])

def test_all_approaches():
    print("=== 全アプローチの比較 ===")
    
    import sys
    from io import StringIO
    
    # テストケース
    test_input = """4 2 10
a
a
b
a"""
    
    for i, solve_func in enumerate([solve_efficient, solve_very_efficient, solve_simple], 1):
        print(f"\nアプローチ {i}:")
        
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        sys.stdin = StringIO(test_input)
        sys.stdout = StringIO()
        
        try:
            solve_func()
            output = sys.stdout.getvalue().strip()
            print(f"結果: '{output}'")
        except Exception as e:
            print(f"エラー: {e}")
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout

if __name__ == "__main__":
    test_all_approaches()
