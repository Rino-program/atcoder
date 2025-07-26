# 実際の入力をシミュレート
import sys
from io import StringIO

def test_input_output():
    print("=== 入力出力のテスト ===")
    
    # サンプル入力をシミュレート
    sample_input = """3 2 6
abc
xxx
abc"""
    
    # 標準入力を一時的に置き換え
    old_stdin = sys.stdin
    sys.stdin = StringIO(sample_input)
    
    try:
        # solve関数を実行
        n, k, x = map(int, input().split())
        s = []
        for _ in range(n):
            s.append(input().strip())
        
        s_sorted = sorted(s)
        
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
        
        output = ''.join(result)
        print(f"出力: '{output}'")
        
    finally:
        # 標準入力を元に戻す
        sys.stdin = old_stdin
    
    print("入力出力テスト完了")

if __name__ == "__main__":
    test_input_output()
