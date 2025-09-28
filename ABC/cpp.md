
# C++ テンプレ関数 & 構造体 解説

`templates/main.cpp` に含まれるテンプレの簡潔な説明です。重複見出しを除去し一意化しています。

## 基本方針

- main は上
- 出力を汚さない
- 典型最小セット（方向 / DSU / 座標圧縮 / BIT / SegTree / Sieve）

---

## 型エイリアス

| 名前 | 意味 |
|------|------|
| `ll` | `long long` |
| `ull` | `unsigned long long` |
| `ld` | `long double` |
| `pii` | `pair<int,int>` |
| `pll` | `pair<long long,long long>` |
| `vi` | `vector<int>` |
| `vl` | `vector<long long>` |
| `vvi` | `vector<vector<int>>` |

## マクロ

| マクロ | 内容 |
|--------|------|
| `rep(i,n)` | 0..n-1 ループ |
| `rep1(i,n)` | 1..n ループ |
| `repr(i,n)` | 逆順 n-1..0 |
| `all(x)` | begin/end |
| `rall(x)` | rbegin/rend |
| `sz(x)` | size を int |

## 定数

`INF`/`LINF`/`PI`/`MOD` を定義。`MOD` は必要に応じ変更。

## 汎用関数

### chmax / chmin

更新時のみ処理したいときのショートカット。

### gcd / lcm / pow_mod

基本数論。`pow_mod` は __int128 でオーバーフロー対策済み。C++14+ では `std::gcd` も使用可。

### mod_inverse / factorials / nCr

逆元計算と組み合わせの高速計算。数学問題で必須。

### binary_search

テンプレート化された汎用二分探索。

## 方向ベクトル

```cpp
const int dx4[4] = {1,0,-1,0};
const int dy4[4] = {0,1,0,-1};
```
4 方向走査。8 方向は `dx8/dy8`。

## Union-Find (DSU)

```cpp
DSU uf(N); uf.merge(a,b); uf.same(x,y); uf.size(v);
```
連結判定/併合/サイズ取得。

## 座標圧縮

```cpp
auto comp = compress(values);
int id = get_index(comp, x);
```
`comp` は昇順ユニーク配列。

## Fenwick Tree (BIT)

```cpp
BIT bit(N); bit.add(i,x); long long s=bit.sum_range(l,r);
```
`lower_bound(w)` で累積和閾値検索。

## Segment Tree (区間和)

```cpp
SegTree st(N); rep(i,N) st.set_val(i,a[i]); st.build(); st.update(i,v); st.query(l,r);
```

## RMQ Segment Tree (Range Minimum Query)

```cpp
RMQSegTree rmq(N); rep(i,N) rmq.set_val(i,a[i]); rmq.build(); ll min_val = rmq.query(l,r);
```

## 二分探索ヘルパー

```cpp
ll result = binary_search(ok, ng, [&](ll mid) { return check_condition(mid); });
```

## Sieve (素数列挙)

```cpp
auto [is, primes] = sieve(MAXN);
```

`is[p]` が true なら p は素数。

## 使用例フロー

1. 入力
2. 必要なら圧縮
3. DSU / BIT / SegTree 初期化
4. 本処理
5. 出力

## ワンライナ例

| 用途 | 書き方 |
|------|--------|
| 配列和 | `accumulate(all(a),0LL)` |
| 最大値 | `*max_element(all(a))` |
| 降順ソート | `sort(rall(a))` |
| 要素数 | `sz(a)` |

## メンテ

不要な構造は提出前に削除してビルド高速化。

## 他に追加希望があれば連絡してください

---

必要に応じて他の典型 (BFS/最短路テンプレ, 2-SAT, Rolling Hash, 逆元/階乗前計算 等) も追加できます。要望ください。
