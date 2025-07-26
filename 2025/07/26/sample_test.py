import sys
from io import StringIO

def test_with_sample_input():
    print("=== サンプル入力でのテスト ===")
    
    # サンプル入力
    sample_input = """3 2 6
abc
xxx
abc"""
    
    old_stdin = sys.stdin
    sys.stdin = StringIO(sample_input)
    
    try:
        # 新しいsolve関数を実行
        n, k, x = map(int, input().split())
        s = []
        for _ in range(n):
            s.append(input().strip())
        
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
        
        result = all_combinations[x - 1]
        print(f"結果: {result}")
        
    finally:
        sys.stdin = old_stdin

if __name__ == "__main__":
    test_with_sample_input()
