import math
import sys
from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def get_compactness(region, p):
    cells = set(region)
    perimeter = 0
    for x, y in region:
        for dx, dy in DIRS:
            if (x + dx, y + dy) not in cells:
                perimeter += 1
    return 4 * math.sqrt(p) / perimeter

def find_best_compact_region(grid, owner, n, p):
    """
    空き芝生マスを始点として、コンパクト度 C ができるだけ大きくなるように
    P マスの連結領域を探索・生成する。
    """
    best_region = None
    best_c = -1.0

    # 探索の始点候補（すべての空きマスを試すと重い場合は間引きやランダムサンプリング）
    candidates = [(x, y) for x in range(n) for y in range(n) if grid[x][y] == '.' and owner[x][y] == -1]
    
    # 実行時間制限に応じて候補数を絞る
    import random
    if len(candidates) > 40:
        candidates = random.sample(candidates, 40)

    for start in candidates:
        # 始点から周りを巻き込んで P マス集める（貪欲に周囲長を抑える）
        region = [start]
        visited = {start}
        
        # 隣接マス群を管理
        adj_candidates = set()
        for dx, dy in DIRS:
            nx, ny = start[0] + dx, start[1] + dy
            if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == '.' and owner[nx][ny] == -1:
                adj_candidates.add((nx, ny))

        # P マスになるまで、最も重心に近い／周囲長を増やさないマスを追加
        while len(region) < p and adj_candidates:
            # 重心からの距離が近いマスを優先選択
            cx = sum(r[0] for r in region) / len(region)
            cy = sum(r[1] for r in region) / len(region)
            
            best_nxt = min(adj_candidates, key=lambda pos: (pos[0] - cx)**2 + (pos[1] - cy)**2)
            
            region.append(best_nxt)
            visited.add(best_nxt)
            adj_candidates.remove(best_nxt)

            # 新しい隣接マスを追加
            for dx, dy in DIRS:
                nx, ny = best_nxt[0] + dx, best_nxt[1] + dy
                if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == '.' and owner[nx][ny] == -1 and (nx, ny) not in visited:
                    adj_candidates.add((nx, ny))

        if len(region) == p:
            c = get_compactness(region, p)
            if c > best_c:
                best_c = c
                best_region = region

    return best_region, best_c

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    iterator = iter(input_data)
    n = int(next(iterator))
    m = int(next(iterator))
    r = float(next(iterator))

    grid = [next(iterator) for _ in range(n)]
    owner = [[-1] * n for _ in range(n)]
    
    # グループごとの情報保持用
    active_groups = {}

    for _ in range(m):
        gid = int(next(iterator))
        s = int(next(iterator))
        t = int(next(iterator))
        p = int(next(iterator))
        v = int(next(iterator))

        # 退去処理
        to_remove = [g for g, info in active_groups.items() if info['t'] < s]
        for g in to_remove:
            for x, y in active_groups[g]['pos']:
                owner[x][y] = -1
            del active_groups[g]

        # 1. 移動の出力 (まずは 0 でスキップ)
        print(0)

        # 2. 単位時間あたりの価値（V / (P * Duration)）が低すぎる場合は見送る閾値判定も有効
        duration = t - s
        value_density = v / (p * duration)

        # 領域探索
        region, c = find_best_compact_region(grid, owner, n, p)

        # 簡易フィルタ: C が低すぎる（細長すぎる）場合や条件に合わない場合は Reject
        if region is not None and c >= 0.6:
            for x, y in region:
                owner[x][y] = gid
            active_groups[gid] = {'t': t, 'pos': region, 'c': c}
            
            print("Yes")
            for x, y in region:
                print(x, y)
        else:
            print("No")

        sys.stdout.flush()

if __name__ == "__main__":
    main()