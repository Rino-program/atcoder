def test_overflow_scenarios():
    print("=== オーバーフロー検証 ===")
    
    # 大きな値でのテスト
    test_cases = [
        (50, 10, 1000000000000000000),  # 非常に大きなX
        (100, 5, 10**18),  # 大きなn, k
        (10, 20, 10**15),  # 大きなk
    ]
    
    for n, k, x in test_cases:
        print(f"\nケース: n={n}, k={k}, x={x}")
        
        try:
            # 最大組み合わせ数をチェック
            max_combinations = n ** k
            print(f"最大組み合わせ数: {max_combinations}")
            
            if x > max_combinations:
                print("エラー: Xが最大組み合わせ数を超えています")
                continue
            
            # アルゴリズムのシミュレーション（実際の文字列は使わない）
            remaining = x - 1
            result_length = 0
            
            for pos in range(k):
                found = False
                for i in range(n):
                    combinations = n ** (k - pos - 1)
                    
                    if remaining < combinations:
                        result_length += 1
                        found = True
                        break
                    else:
                        remaining -= combinations
                
                if not found:
                    print(f"警告: 位置{pos+1}で該当文字列が見つかりませんでした")
                    break
            
            print(f"結果の長さ: {result_length}")
            print(f"期待される長さ: {k}")
            
        except OverflowError as e:
            print(f"オーバーフローエラー: {e}")
        except Exception as e:
            print(f"その他のエラー: {e}")

def test_potential_fix():
    print("\n=== 潜在的な修正案のテスト ===")
    
    # より安全な実装を試す
    def safe_solve_simulation(n, k, x):
        remaining = x - 1
        result_positions = []
        
        for pos in range(k):
            found = False
            for i in range(n):
                # より安全な計算
                if k - pos - 1 == 0:
                    combinations = 1
                else:
                    combinations = n ** (k - pos - 1)
                
                if remaining < combinations:
                    result_positions.append(i)
                    found = True
                    break
                else:
                    remaining -= combinations
            
            if not found:
                # フォールバック: 最後の文字列を選択
                result_positions.append(n - 1)
        
        return result_positions
    
    # テストケース
    test_cases = [
        (3, 2, 6),
        (4, 2, 10),
        (2, 3, 8),
    ]
    
    for n, k, x in test_cases:
        positions = safe_solve_simulation(n, k, x)
        print(f"n={n}, k={k}, x={x} -> positions: {positions}")

if __name__ == "__main__":
    test_overflow_scenarios()
    test_potential_fix()
