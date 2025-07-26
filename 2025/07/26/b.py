from collections import Counter

# サンプルデータ
data = ['qpple', 'banana', 'qpple', 'orange', 'banana', 'qpple']

# Counterオブジェクトを作成
counter = Counter(data)

# 出現回数が多い順に取得
sorted_items = counter.most_common()

print(sorted_items)
print(type(dict(counter)))
print(dict(counter))