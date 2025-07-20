# deque
import time
# from collections import deque

n = int(input("試行回数:")) # 試行回数

print("準備開始")

# 準備
search_target = n - 1  # 存在する要素
li = list(range(n))
d = {i: None for i in range(n)}

print("準備完了\n計測開始")

# 進捗の計算
si = n // 5

# listを使った時間計測

start1 = time.time()
for i in range(n):
    found = search_target in li
    if (i + 1) % si == 0:  # 進捗表示
        print(f"進捗: {i + 1} / {n}")
end1 = time.time()

# dictを使った時間計測

start2 = time.time()
for i in range(n):
    found = search_target in d
    if (i + 1) % si == 0:  # 進捗表示
        print(f"進捗: {i + 1} / {n}")
end2 = time.time()

# 結果の表示
print(f"試行 {n} 回 (list): {end1 - start1} 秒")
print(f"試行 {n} 回 (dict): {end2 - start2} 秒")