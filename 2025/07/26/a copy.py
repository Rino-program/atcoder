def solve():
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

# メイン実行
if __name__ == "__main__":
    solve()