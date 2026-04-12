from collections import deque
import heapq, sys
N, M, C = map(int, input().split())
D = list(map(int, input().split()))
Map = [list(map(int, input().split())) for i in range(N)]
DIR4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
hebi_li: tuple = ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0))
length = 5

def debug(*args, **kwargs):
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

# 優先度計算（色と現在のlengthから）
def get_priority(color, curr_length):
    if curr_length >= M:
        return 0
    score = 0
    if color == D[curr_length]:
        score += 100000
    if curr_length + 1 < M and color == D[curr_length + 1]:
        score += 25000
    if curr_length + 2 < M and color == D[curr_length + 2]:
        score += 6000
    return score

# 簡易探索：ある状態から最も価値の高い餌を1つだけ探す（評価用）
def evaluate_after_eat(head, body, curr_length):
    if curr_length >= M - 1:
        return 0
    pq = [(0, head[0], head[1], body)]
    visited = set()
    best = 0
    limit = 8  # 軽く探索（深さ制限）

    while pq:
        cost, x, y, b = heapq.heappop(pq)
        if cost > limit or (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in DIR4:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < N and 0 <= ny < N) or (nx, ny) in b[1:]:
                continue
            if Map[nx][ny] != 0:
                pri = get_priority(Map[nx][ny], curr_length + 1)
                best = max(best, pri)
                continue  # 1つ目の餌だけ評価

            # 空マス移動（簡略化）
            new_body = b[1:] + ((nx, ny),)
            heapq.heappush(pq, (cost + 1, nx, ny, new_body))
    
    return best

while length < M:
    now = hebi_li[-1]
    candidates = []  # (総合スコア, cost, x, y, path, color)
    dist = [[float("inf")] * N for _ in range(N)]
    dist[now[0]][now[1]] = 0
    pq = [(0, now[0], now[1], hebi_li, "")]

    while pq:
        cost, x, y, body, path = heapq.heappop(pq)
        if cost > dist[x][y]:
            continue

        for i, move_char in enumerate(["R", "D", "L", "U"]):
            dx, dy = DIR4[i]
            nx, ny = x + dx, y + dy
            if not (0 <= nx < N and 0 <= ny < N) or (nx, ny) in body[1:]:
                continue

            new_path = path + move_char

            if Map[nx][ny] != 0:   # 餌発見
                color = Map[nx][ny]
                pri1 = get_priority(color, length)                    # 1つ目の優先度
                # 取った後の簡易評価
                new_head = (nx, ny)
                new_body = body[1:] + (new_head,)
                pri2 = evaluate_after_eat(new_head, new_body, length + 1)

                total_score = pri1 + pri2 * 0.6   # 2つ目の影響を少し弱めに
                candidates.append(( -total_score, cost, nx, ny, new_path, color ))
                continue

            # 空マス移動
            body_new = body[1:] + ((nx, ny),)
            total_cost = cost + 1   # コストほぼ無視するため1固定
            if total_cost < dist[nx][ny]:
                dist[nx][ny] = total_cost
                heapq.heappush(pq, (total_cost, nx, ny, body_new, new_path))

    if not candidates:
        break

    # ベスト選択
    candidates.sort()
    _, best_cost, nx, ny, result, _ = candidates[0]

    # 実行部（変更なし）
    for move in result:
        hx, hy = hebi_li[-1]
        if move == "R": hy += 1
        elif move == "D": hx += 1
        elif move == "L": hy -= 1
        elif move == "U": hx -= 1

        new_list = list(hebi_li)
        new_list.append((hx, hy))

        if (hx, hy) == (nx, ny):
            length += 1
            Map[hx][hy] = 0
            hebi_li = tuple(new_list)
        else:
            hebi_li = tuple(new_list[1:])
        print(move)