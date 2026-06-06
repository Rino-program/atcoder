# AtCoder Competition Template (template.py) 収録機能一覧

提供された [template.py](c:/VSCode_program/atcoder/contests/.template/template.py) に含まれている機能をカテゴリ別にまとめます。

## 1. 入出力ヘルパ
- `input()`: `sys.stdin.readline` を用いた高速入力。
- `INT()`: 整数入力を取得。
- `MAP()`: 複数の整数入力を取得。
- `LIST()`: 1行の整数をリストとして取得。
- `LISTS(n)`: $n$ 行の整数リスト（行列）を取得。
- `LISTSI(n)`: $n$ 行の整数（1行1列）を取得。
- `STR()`: 文字列入力を取得。
- `STRS(n)`: $n$ 行の文字列を取得。
- `CHARS()`: 文字列を1文字ずつのリストとして取得。
- `STRSL(n)`: $n$ 行の文字列を1文字ずつのリストとして取得。

## 2. 定数・グローバル設定
- `INF`: 無限大（$10^{18}$）。
- `MOD`: 法（$998244353$）。
- `sys.setrecursionlimit`: 再帰深度の上限設定（$10^6$）。

## 3. 方向ベクトル
- `DIR4`: 4近傍（上下左右）。
- `DIR8`: 8近傍。
- `DIR9`: 8近傍 ＋ 自己。

## 4. 文字列のリスト
- `LOWER`: 英小文字 `a-z`。
- `UPPER`: 英大文字 `A-Z`。
- `DIGITS`: 数字 `0-9`。

## 5. よく使う出力関数
- `pr`: `print` のエイリアス。
- `Yes()`, `No()`, `yes()`, `no()`, `YES()`, `NO()`: 定型文字列の出力。

## 6. 数学・整数論
- `is_prime(n)`: 素数判定。
- `prime_factors(n)`: 素因数分解。
- `divisors(n)`: 約数列挙。
- `sieve(n)`: エラトステネスの篩。
- `gcd(a, b)`: 最大公約数。
- `lcm(a, b)`: 最小公倍数。
- `ext_gcd(a, b)`: 拡張ユークリッドの互除法。
- `pow_mod(x, n, mod)`: 繰り返し二乗法による冪乗。
- `mod_inverse(a, mod)`: モジュロ逆元。

## 7. 組み合わせ計算
- `Combination` クラス: 階乗・等を用いた $nCr, nPr, nHr, catalan$（カタラン数）の計算。

## 8. 累積和
- `prefix_sum(arr)`: 1次元累積和。
- `prefix_sum_2d(grid)`: 2次元累積和。
- `range_sum_2d(ps, y1, x1, y2, x2)`: 2次元累積和を用いた矩形和取得。

## 9. いもす法
- `Imos1D`: 1次元いもす法クラス。
- `Imos2D`: 2次元いもす法クラス。

## 10. Union-Find
- `DSU`: 通常の Union-Find。
- `WeightedDSU`: 重み付き Union-Find。

## 11. グラフアルゴリズム
- `build_graph()` / `build_weighted_graph()`: 隣接リストの構築。
- `bfs(g, s)`: 最短経路（重みなし）。
- `multi_source_bfs(g, sources)`: 多始点 BFS。
- `bfs_grid(grid, sy, sx)`: グリッド上での BFS。
- `dijkstra(g, s)`: ダイクストラ法（非負重み）。
- `zero_one_bfs(g, s)`: 0-1 BFS。
- `bellman_ford(n, edges, s)`: ベルマンフォード法（負閉路検知）。
- `warshall_floyd(n, edges)`: ワーシャルフロイド法（全点対最短経路）。
- `topological_sort(g)`: トポロジカルソート。
- `detect_cycle(g)`: 有向グラフの閉路検出。
- `bipartite_coloring(g)`: 二部グラフ判定と彩色。
- `kruskal(n, edges)`: クラスカル法（最小全域木）。

## 12. 木アルゴリズム
- `tree_diameter(g)`: 木の直径。
- `tree_depth(g, root)`: 各頂点の深さ。
- `tree_parent(g, root)`: 各頂点の親。
- `subtree_size(g, root)`: 各頂点の部分木サイズ。
- `LCA` クラス: ダブリングによる最小共通祖先。

## 13. データ構造
- `BIT`: Binary Indexed Tree (Fenwick Tree)。
- `SegTree`: 汎用セグメント木。
- `LazySegTree`: 遅延評価セグメント木。
- `BIT2` / `BIT2D`: 1-indexed BIT または 2次元 BIT。
- `SortedMultiset`: 順序付きマルチセット。

## 14. 文字列アルゴリズム
- `RollingHash`: ローリングハッシュ。
- `z_algorithm(s)`: Z-algorithm。
- `run_length_encode(s)`: ランレングス圧縮（連長圧縮）。
- `Trie`: トライ木。
- `kmp_table()` / `kmp_search()`: KMP法。

## 15. 二分探索
- `binary_search_min(ng, ok, check)`: 条件を満たす最小値の探索。
- `binary_search_max(ok, ng, check)`: 条件を満たす最大値の探索。
- `binary_search_float(...)`: 浮動小数点の二分探索。

## 16. 座標圧縮・転倒数・その他
- `lis(arr)`: 最長増加部分列。
- `compress()` / `compress_list()`: 座標圧縮。
- `rank_data(arr, reverse, competition)`: データの順位付け。
- `inversion_count(arr)`: 転倒数。
- `manhattan(x1, y1, x2, y2)`: マンハッタン距離。
- `chebyshev(x1, y1, x2, y2)`: チェビシェフ距離。
- `ceil_div(a, b)`: 切り上げ除算。
- `floor_sum(n, m, a, b)`: $\sum \lfloor (ai+b)/m \rfloor$ の計算。
- `rotate_90(grid)`: グリッドの90度回転。
- `transpose(grid)`: グリッドの転置。
- `bit_full_search(n)`: bit全探索のループ。
- `bit_indices(bit, n)`: 立っているビットの指数列挙。
- `submasks(mask)`: 部分集合の列挙。

## 17. 出力・デバッグ
- `Output` クラス: 複数の値を一括出力するヘルパ。
- `debug(*args, **kwargs)`: デバッグプリント。
- `print_grid(grid, sep)`: 2次元配列を綺麗に出力。
- `yn(cond)`: 真偽値による Yes/No 出力。
