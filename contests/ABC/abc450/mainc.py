from collections import deque


# ===== 入出力ヘルパ =====
def MAP():
    return map(int, input().split())

def STR() -> str:
    return input()

def CHARS() -> list[str]:
    return list(STR())

def CHARSL(n: int) -> list[list[str]]:
    return [list(STR()) for _ in range(n)]

# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 関数短縮 =====
pr = print
en = enumerate

# ===== 方向ベクトル =====
DIR4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIR8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIR9 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

# ==============================================
# =================== main =====================
# ==============================================

def main() -> None:
    # ここに解答を書く
    H, W = MAP()
    S = CHARSL(H)
    ans = 0
    for i in range(H):
        for j in range(W):
            if S[i][j] == ".":
                # OK (+)
                d = deque()
                d.append((i, j))
                ans += 1
                f = 0
                while d:
                    x, y = d.popleft()
                    if x == 0 or y == 0 or x == H-1 or y == W-1:
                        f = 1
                    for dx, dy in DIR4:
                        if x+dx >= 0 and x+dx < H and y+dy >= 0 and y+dy < W and S[x+dx][y+dy] == ".":
                            S[x+dx][y+dy] = str(ans)
                            d.append((x+dx, y+dy))
                if f:
                    ans -= 1
    print(ans)





















if __name__ == "__main__":
    main()