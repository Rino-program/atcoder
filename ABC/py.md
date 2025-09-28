


# Python テンプレ関数 & 構造体 解説

`templates/main.py` の内容説明。必要に応じてコピペで拡張。

## 基本方針

- 入出力を最優先（高速 input）。
- main 直実行。`solve` を挟まない。
- 典型最小セット + よく使う軽量構造。

---

## 入出力ラッパ

| 関数 | 説明 | 例 |
|------|------|----|
| `INT()` | 1 整数 | `n = INT()` |
| `MAP()` | 複数整数 | `a,b = MAP()` |
| `LIST()` | 整数配列 | `A = LIST()` |
| `STR()` | 文字列1行 | `s = STR()` |

内部で `sys.stdin.readline().rstrip()` を使用。

---

## 定数 / 方向

| 名称 | 説明 |
|------|------|
| `INF` | 10**18 |
| `MOD` | 998244353 (変更可) |
| `DIR4` | 上下左右 | 
| `DIR8` | 8 方向 |

---

## 便利関数

### lcm

Python 3.9+ は `math.lcm` でも可。

### pow_mod / mod_inverse

高速べき乗と逆元計算。組み合わせや数学問題で頻出。

### factorials / nCr

階乗と逆元の事前計算で、組み合わせをO(1)で計算。

### binary_search

汎用的な二分探索ヘルパー。

### compress (座標圧縮)

```python
idx, xs = compress([100,5,5,20])  # xs=[5,20,100]; idx[20] -> 1
```

`idx` : 元値→圧縮 index, `xs` : 昇順ユニーク配列。

---

## DSU (Union-Find)

```python
uf = DSU(N)
uf.merge(a,b)
if uf.same(x,y): ...
sz = uf.component_size(x)
all_groups = uf.groups()  # 全連結成分を取得
```

---

## BFS

```python
dist = bfs_graph(g, s)  # 未到達は -1
```

---

## Dijkstra

```python
dist = dijkstra(g, s)  # g[v] = [(to,cost),...]
```

---

## Fenwick Tree (BIT)

区間和 / 点加算。

```python
bit = BIT(N)
bit.add(i, x)
s = bit.range_sum(l, r)
```

---

## Segment Tree (Sum)

```python
st = SegTree(N)
st.build(A)
st.update(i, v)
s = st.query(l, r)
```

---

## Prefix Sum

```python
ps = prefix_sum(A)
segment = ps[r] - ps[l]
```

---

## Sieve (素数)

```python
is_prime, primes = sieve(MAXN)
if is_prime[x]: ...
```

---

## 手順例

1. 入力読む
2. 必要なら圧縮 / DSU init
3. グラフ構築→BFS/Dijkstra
4. 計算
5. `print(ans)`

---

## 速度メモ

- PyPy3 利用
- 再帰: `setrecursionlimit` 済
- 大量 I/O: まとめ読み / 出力は join

---

## チェックリスト

- 使ってない構造を削除
- 余計な print 無し
- 多ケースはループ実装

---

追加したい構造 (BIT 以外の木 DP, 二分探索テンプレ, 2D 累積和など) があれば依頼ください。
