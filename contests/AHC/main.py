from collections import deque
import heapq, sys
N, M, C = map(int, input().split()) #8<=N<=16, N^2/4<=M<=3N^2/4, 3<=C<=7
D = list(map(int, input().split())) #M
Map = [list(map(int, input().split())) for i in range(N)] #N*N
DIR4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
hebi_li: tuple = ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0))
length = 5
# ===== デバッグ =====
def debug(*args, **kwargs) -> None:
    """デバッグ出力（標準エラー）"""
    print("[DEBUG]", *args, **kwargs, file=sys.stderr)

while length < M:
    now = hebi_li[-1]
    pq = [(0, now[0], now[1], hebi_li, "")]
    temp = []
    tmp = []
    dist = [[float("inf")] * N for _ in range(N)]
    dist[now[0]][now[1]] = 0
    target_found_dist = float("inf")
    while pq:
        cost, x, y, body, path = heapq.heappop(pq)
        if cost > target_found_dist:
            break
        if cost > dist[x][y]:
            continue
        for i, move_char in enumerate(["R", "D", "L", "U"]):
            dx, dy = DIR4[i]
            nx, ny = x + dx, y + dy
            after_body = set(body[1:])
            if not (0 <= nx < N and 0 <= ny < N) or (nx, ny) in body:
                continue
            new_path = path + move_char
            if Map[nx][ny] != 0:
                new_cost = cost + 1
                if Map[nx][ny] == D[length]:
                    heapq.heappush(temp, (new_cost, nx, ny, new_path))
                else:
                    heapq.heappush(tmp, (new_cost, nx, ny, new_path))
                target_found_dist = min(target_found_dist, new_cost)
                continue
            body_new = body[1:] + ((nx, ny),)
            if i % 2 == 1:
                nn1, nn2 = (nx, ny - 1), (nx, ny + 1)
            else:
                nn1, nn2 = (nx - 1, ny), (nx + 1, ny)
            can_pass = False
            for r, c in [nn1, nn2]:
                if 0 <= r < N and 0 <= c < N and (r, c) not in body_new:
                    can_pass = True
                    break
            step = cost + (1 if can_pass else 3)
            total_cost = step
            state = (nx, ny, body_new)
            if total_cost < dist[nx][ny]:
                dist[nx][ny] = total_cost
                heapq.heappush(pq, (total_cost, nx, ny, body_new, path + ["R", "D", "L", "U"][i]))
    if not temp and not tmp:
        break
    if not temp:
        _, nx, ny, result = heapq.heappop(tmp)
    else:
        _, nx, ny, result = heapq.heappop(temp)
    if not result:
        break
    for move in result:
        hx, hy = hebi_li[-1]
        if move == "R":
            hy += 1
        elif move == "D":
            hx += 1
        elif move == "L":
            hy -= 1
        elif move == "U":
            hx -= 1
        new_list = list(hebi_li)
        new_list.append((hx, hy))
        if (hx, hy) == (nx, ny):
            length += 1
            Map[hx][hy] = 0
            hebi_li = tuple(new_list)
        else:
            hebi_li = tuple(new_list[1:])
        print(move)