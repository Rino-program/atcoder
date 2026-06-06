import os
import subprocess
import time

# 評価するケースの範囲 (0000.txt ~ 0100.txt)
START_CASE = 0
END_CASE = 100
TLE_LIMIT = 3.0

def simulate(input_file, moves_str):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().split()
    
    if not content:
        return None
        
    N = int(content[0])
    M = int(content[1])
    C = int(content[2])
    D = [int(x) for x in content[3:3+M]]
    
    idx = 3 + M
    F = []
    for i in range(N):
        row = []
        for j in range(N):
            row.append(int(content[idx]))
            idx += 1
        F.append(row)

    # 初期状態
    snake_coords = [(4,0), (3,0), (2,0), (1,0), (0,0)]
    snake_colors = [1, 1, 1, 1, 1]
    
    # 出力から改行等を除去し、有効な文字のみ抽出
    moves = [m for m in moves_str if m in 'UDLR']
    T_total = len(moves)
    valid = True

    for move in moves:
        hy, hx = snake_coords[0]
        if move == 'U': hy -= 1
        elif move == 'D': hy += 1
        elif move == 'L': hx -= 1
        elif move == 'R': hx += 1

        new_head = (hy, hx)
        
        # 盤面外チェック
        if hy < 0 or hy >= N or hx < 0 or hx >= N:
            valid = False
            break
            
        # Uターンチェック
        if len(snake_coords) > 1 and new_head == snake_coords[1]:
            valid = False
            break

        new_coords = [new_head] + snake_coords[:-1]
        new_colors = snake_colors[:]

        # 食事判定
        if F[hy][hx] > 0:
            eat_color = F[hy][hx]
            F[hy][hx] = 0
            new_coords.append(snake_coords[-1])
            new_colors.append(eat_color)
        else:
            # 噛みちぎり判定
            bite_h = -1
            for h in range(1, len(new_coords) - 1):
                if new_coords[h] == new_head:
                    bite_h = h
                    break
            
            if bite_h != -1:
                # 切断された部分は餌になる
                for p in range(bite_h + 1, len(new_coords)):
                    py, px = new_coords[p]
                    F[py][px] = new_colors[p]
                new_coords = new_coords[:bite_h + 1]
                new_colors = new_colors[:bite_h + 1]

        snake_coords = new_coords
        snake_colors = new_colors

    k = len(snake_coords)
    E = sum(1 for i in range(k) if snake_colors[i] != D[i])
    score = T_total + 10000 * (E + 2 * (M - k))
    
    return score, k, E, T_total, valid

def main():
    total_tle_count = 0
    results_summary = {}

    for solver_id in range(1, 6):
        exe_name = f"solver{solver_id}.exe"
        exe_path = os.path.join(".", exe_name)
        
        if not os.path.exists(exe_path):
            print(f"[{exe_name}] 見つかりません。スキップします。")
            continue
            
        print(f"========== {exe_name} ==========")
        
        sum_score = 0
        sum_length = 0
        sum_E = 0
        sum_T = 0
        sum_time = 0.0
        success_count = 0
        
        for case_id in range(START_CASE, END_CASE + 1):
            case_name = f"{case_id:04d}.txt"
            in_path = os.path.join("in", case_name)
            
            if not os.path.exists(in_path):
                print(f"[{case_name}] 入力ファイルが見つかりません。")
                continue
                
            try:
                with open(in_path, 'r') as f_in:
                    # 実行時間の計測開始
                    start_time = time.perf_counter()
                    proc = subprocess.run([exe_path], stdin=f_in, capture_output=True, text=True, timeout=TLE_LIMIT)
                    # 計測終了
                    exec_time = time.perf_counter() - start_time
                
                moves_str = proc.stdout
                sim_result = simulate(in_path, moves_str)
                
                if sim_result is None:
                    print(f"[{case_name}] シミュレーションに失敗しました。")
                    continue
                    
                score, length, error_e, moves_count, is_valid = sim_result
                
                status_str = "" if is_valid else " (WA: 無効な移動)"
                print(f"[{case_name}] 得点: {score:8d}, 長さ: {length:3d}, 色精度: {error_e:3d}, 手数: {moves_count:5d}, 実行時間: {exec_time:.3f}s{status_str}")
                
                sum_score += score
                sum_length += length
                sum_E += error_e
                sum_T += moves_count
                sum_time += exec_time
                success_count += 1
                
            except subprocess.TimeoutExpired:
                print(f"[{case_name}] TLE ({TLE_LIMIT}sec 超過)")
                total_tle_count += 1
            except Exception as e:
                print(f"[{case_name}] 実行エラー: {e}")

        if success_count > 0:
            avg_score = sum_score / success_count
            avg_length = sum_length / success_count
            avg_E = sum_E / success_count
            avg_T = sum_T / success_count
            avg_time = sum_time / success_count
            results_summary[exe_name] = (avg_score, avg_length, avg_E, avg_T, avg_time, success_count)
            print("-" * 60)
            print(f"{exe_name} 平均 -> 得点: {avg_score:.1f}, 長さ: {avg_length:.1f}, 色精度: {avg_E:.1f}, 手数: {avg_T:.1f}, 実行時間: {avg_time:.3f}s")
        else:
            print(f"{exe_name} の有効な結果はありませんでした。")
        print()

    print("========== 最終結果まとめ ==========")
    for exe_name, (avg_score, avg_length, avg_E, avg_T, avg_time, cnt) in results_summary.items():
        print(f"[{exe_name}] (有効 {cnt}ケース)")
        print(f"  平均得点    : {avg_score:.1f}")
        print(f"  平均長さ    : {avg_length:.1f}")
        print(f"  平均色精度  : {avg_E:.1f}")
        print(f"  平均手数    : {avg_T:.1f}")
        print(f"  平均実行時間: {avg_time:.3f}s")
        print()
    
    print("-" * 40)
    print(f"合計 TLE 回数: {total_tle_count} 回")

if __name__ == "__main__":
    main()