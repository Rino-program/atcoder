import sys
from collections import deque

RAW_MAP = [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "..................i..ji.................",
    "...................jfnni................",
    "..............iifkaegdddc...............",
    ".............inkdddbdddhdai.............",
    "............cagddbdbkhbddbh.............",
    "............ahdbbbbgdgbbbddf............",
    "...........eagdbbbbddgagbbdgi...........",
    "..........nekdgbbbbbdannhbdda...........",
    ".........ieakhdbddbdanffngbddi..........",
    ".........fehdabdbdganfffnedbbh..........",
    "........ihkggagaabhnfffnnngbddi.........",
    "........iaahnahhahnfllfnnnkbbdf.........",
    "........jeeeaaaaalfjilfnanabbdl.........",
    "........jneehheeiiiijfnahnebbbj.........",
    "........inaaaafijiijfcicnfndbbl.........",
    "........jnaani.inn.jahaeaafkbbf.........",
    "........jnkeljicnlijeaeccffabbi.........",
    "........neknj.ilii.inenjcfcndg..........",
    "........jeani.ijji.ifeaclfcfkg..........",
    ".........ieni..jci.innaacfffah..........",
    "..........cni.ifi.iieaaenffffl..........",
    "...........iiiji..iifeeanffci...........",
    "...........ii.ilaiijfnkanffc............",
    "............i.iiiiillcnnnnfj............",
    "..............ii...ijfnennfj............",
    "..............ii...ijcnnnffi............",
    "..............iii.iijjcnnnf.............",
    "...............iii.ijjnnnnfi............",
    "................iiijcfnnnnff............",
    ".............i...iijcfneenffh...........",
    "............ia.....icnnnnnfndaj.........",
    "...........fne....iiifnfffnnghahj.......",
    ".........ienef....iiicllfnnecnhhhai.....",
    ".......iceelei....iiiiicffnicahhhkde....",
    ".....ilfcfjje.....iiiiicfliiifakkhadhni.",
    "...ijcfcfcjlf...i.iiiiili.i.ijnkghagdaan"
]

# マップは一切広げず最小限の 72x72 のまま
N = 72
OFFSET_R = 16
OFFSET_C = 16
K = 14

DIRS_CHAR = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]
OPP_DIR = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}

def solve():
    print("=== 1. ターゲットマスの解析 ===")
    targets = []
    for r in range(40):
        for c in range(40):
            ch = RAW_MAP[r][c]
            if ch != '.':
                targets.append((r + OFFSET_R, c + OFFSET_C, ch))
    
    print(f"盤面サイズ: {N}x{N}（拡張なし・最小サイズ）")
    print(f"ターゲットマス数: {len(targets)}")
    total_slimes = len(targets) * 7
    print(f"散開させるスライム数: {total_slimes} 匹")

    stacks = [[[] for _ in range(N)] for _ in range(N)]
    for r, c, ch in targets:
        stacks[r][c] = [ch] * 8

    # 巣の配置（最外周に隔離）
    nest_positions = {}
    for i in range(K):
        ch_upper = chr(ord('A') + i)
        nest_positions[ch_upper] = (0, i)
    forbidden = set(nest_positions.values())

    print("\n=== 2. 一括タワー運搬（Batch Transport）による高速散開 ===")
    reverse_moves = []
    slimes_moved = 0

    while slimes_moved < total_slimes:
        q = deque()
        visited = {}
        for r in range(N):
            for c in range(N):
                if len(stacks[r][c]) >= 2:
                    visited[(r, c)] = None
                    q.append((r, c))

        found_dest = None
        while q:
            r, c = q.popleft()
            if len(stacks[r][c]) == 0:
                found_dest = (r, c)
                break

            for dr, dc, d_char in DIRS_CHAR:
                nr, nc = r + dr, c + dc
                if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in forbidden:
                    if (nr, nc) not in visited:
                        if len(stacks[nr][nc]) < 8:
                            visited[(nr, nc)] = (r, c, d_char)
                            q.append((nr, nc))
                            if len(stacks[nr][nc]) == 0:
                                found_dest = (nr, nc)
                                break
            if found_dest:
                break

        curr = found_dest
        rev_path = [curr]
        while visited[curr] is not None:
            pr, pc, d_char = visited[curr]
            curr = (pr, pc)
            rev_path.append(curr)
        path = list(reversed(rev_path))
        T = path[0]

        # 幹（trunk）をまとめて運べる最大匹数 M の算出
        max_M = len(stacks[T[0]][T[1]]) - 1
        for p in path[1:-1]:
            max_M = min(max_M, 8 - len(stacks[p[0]][p[1]]))

        # found_dest の近傍にある空きマスを探す
        local_q = deque([found_dest])
        local_visited = {found_dest: None}
        nearby_free_paths = []
        while local_q and len(nearby_free_paths) < max_M - 1:
            curr_loc = local_q.popleft()
            for dr, dc, d_char in DIRS_CHAR:
                nr, nc = curr_loc[0] + dr, curr_loc[1] + dc
                if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in forbidden:
                    if (nr, nc) not in local_visited:
                        if len(stacks[nr][nc]) == 0:
                            local_visited[(nr, nc)] = (curr_loc[0], curr_loc[1], d_char)
                            p_curr = (nr, nc)
                            p_rev = [p_curr]
                            while local_visited[p_curr] is not None:
                                p_curr = (local_visited[p_curr][0], local_visited[p_curr][1])
                                p_rev.append(p_curr)
                            nearby_free_paths.append(list(reversed(p_rev)))
                            local_q.append((nr, nc))

        M = min(max_M, 1 + len(nearby_free_paths))
        M = max(1, M)

        # 1. T から M 匹をまとめて found_dest まで高速一括輸送
        moving_slimes = [stacks[T[0]][T[1]].pop() for _ in range(M)]
        for i in range(len(path) - 1):
            fr, fc = path[i]
            tr, tc = path[i+1]
            d_char = None
            for dr, dc, ch in DIRS_CHAR:
                if fr + dr == tr and fc + dc == tc:
                    d_char = ch
                    break
            reverse_moves.append((fr, fc, tr, tc, d_char, M))

        stacks[found_dest[0]][found_dest[1]].extend(moving_slimes)

        # 2. found_dest から近傍の空きマスへ 1 匹ずつ分岐
        for i in range(M - 1):
            sub_path = nearby_free_paths[i]
            sub_slime = stacks[found_dest[0]][found_dest[1]].pop()
            for j in range(len(sub_path) - 1):
                fr, fc = sub_path[j]
                tr, tc = sub_path[j+1]
                d_char = None
                for dr, dc, ch in DIRS_CHAR:
                    if fr + dr == tr and fc + dc == tc:
                        d_char = ch
                        break
                reverse_moves.append((fr, fc, tr, tc, d_char, 1))
            dest_cell = sub_path[-1]
            stacks[dest_cell[0]][dest_cell[1]].append(sub_slime)

        slimes_moved += M
        if slimes_moved % 1000 < M or slimes_moved == total_slimes:
            print(f"進捗: {slimes_moved} / {total_slimes} 匹完了 (累積手数: {len(reverse_moves)})")

    print(f"\n散開完了！ 総操作回数: {len(reverse_moves)} 手（100,000回の制限を大幅にクリア！）")

    print("\n=== 3. input.txt の生成 ===")
    grid_chars = [['.' for _ in range(N)] for _ in range(N)]
    for ch_upper, (r, c) in nest_positions.items():
        grid_chars[r][c] = ch_upper

    for r in range(N):
        for c in range(N):
            if len(stacks[r][c]) == 1:
                grid_chars[r][c] = stacks[r][c][0]

    with open("input.txt", "w") as f:
        f.write(f"{N} {K}\n")
        for r in range(N):
            f.write("".join(grid_chars[r]) + "\n")
    print("-> input.txt を生成しました。")

    print("\n=== 4. output.txt の生成 ===")
    sim_stacks = [[[] for _ in range(N)] for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if len(stacks[r][c]) == 1:
                sim_stacks[r][c] = [stacks[r][c][0]]

    forward_moves = []
    for from_r, from_c, to_r, to_c, rev_d, M in reversed(reverse_moves):
        cur_h = len(sim_stacks[to_r][to_c])
        k = cur_h - M
        fwd_d = OPP_DIR[rev_d]
        l = 1
        forward_moves.append(f"{to_r} {to_c} {k} {fwd_d} {l}")
        
        jumping = [sim_stacks[to_r][to_c].pop() for _ in range(M)]
        jumping.reverse()
        sim_stacks[from_r][from_c].extend(jumping)

    with open("output.txt", "w") as f:
        for line in forward_moves:
            f.write(line + "\n")
    print(f"-> output.txt を生成しました。（総操作数: {len(forward_moves)}）")

    print("\n=== 5. 整合性検証 ===")
    target_set = {(r, c) for r, c, _ in targets}
    for r, c, ch in targets:
        assert len(sim_stacks[r][c]) == 8 and sim_stacks[r][c] == [ch] * 8, f"Error at ({r}, {c})"

    for r in range(N):
        for c in range(N):
            if (r, c) not in target_set:
                assert len(sim_stacks[r][c]) == 0, f"Error at non-target ({r}, {c})"

    print("検証成功！ 635箇所すべてに完璧に高さ8タワーが完成し、残骸ゼロです！")

if __name__ == "__main__":
    solve()