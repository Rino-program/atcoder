(() => {
  const recipeData = [
    {
      title: "重み付き最短路（典型）",
      flow: "入力 → build_weighted_graph → dijkstra → 問い合わせ出力",
      code: `N, M = MAP()
edges = []
for _ in range(M):
    a, b, w = MAP()
    a -= 1; b -= 1
    edges.append((a, b, w))
g = build_weighted_graph(N, edges, directed=False)
dist = dijkstra(g, 0)
print(-1 if dist[N-1] == INF else dist[N-1])`
    },
    {
      title: "転倒数",
      flow: "入力列 → compress_list → BIT で加算/取得",
      code: `A = LIST()
print(inversion_count(A))`
    },
    {
      title: "連結成分クエリ",
      flow: "辺入力 → DSU.merge → DSU.same / DSU.size",
      code: `N, Q = MAP()
uf = DSU(N)
for _ in range(Q):
    t, a, b = MAP()
    if t == 0:
        uf.merge(a, b)
    else:
        print(1 if uf.same(a, b) else 0)`
    },
    {
      title: "木の距離クエリ",
      flow: "辺入力 → build_graph → LCA 前処理 → dist",
      code: `N = INT()
edges = []
for _ in range(N - 1):
    a, b = MAP(); a -= 1; b -= 1
    edges.append((a, b))
g = build_graph(N, edges)
lca = LCA(g, root=0)
Q = INT()
for _ in range(Q):
    u, v = MAP(); u -= 1; v -= 1
    print(lca.dist(u, v))`
    },
    {
      title: "矩形加算 + 点参照",
      flow: "更新列挙 → Imos2D.add → build",
      code: `H, W, Q = MAP()
imos = Imos2D(H, W)
for _ in range(Q):
    y1, x1, y2, x2 = MAP()
    imos.add(y1, x1, y2, x2, 1)
grid = imos.build()
print(max(max(row) for row in grid))`
    },
    {
      title: "二分探索 + 判定関数",
      flow: "check定義 → binary_search_min で最小解",
      code: `N, K = MAP()
A = LIST()

def check(x: int) -> bool:
    return sum(a // x for a in A if x > 0) <= K

ans = binary_search_min(0, 10**9 + 1, check)
print(ans)`
    }
  ];

  const referenceData = [
    {
      name: "build_weighted_graph + dijkstra",
      category: "グラフ",
      complexity: "O(M) + O((N+M)logN)",
      desc: "非負重みの最短路。dijkstraは重み付き隣接リスト前提。",
      useWhen: "辺重みが0以上で、始点から各点最短距離が必要なとき。",
      combo: "build_weighted_graph → dijkstra。1-index入力なら辺追加時に -1。",
      tags: ["最短路", "重み付き"],
      example: `N, M = MAP()
edges = []
for _ in range(M):
    a, b, c = MAP(); a -= 1; b -= 1
    edges.append((a, b, c))
g = build_weighted_graph(N, edges)
dist = dijkstra(g, 0)`
    },
    {
      name: "build_graph + bfs",
      category: "グラフ",
      complexity: "O(N+M)",
      desc: "重みなしグラフ最短路。未到達は -1。",
      useWhen: "辺コストが全て同じ（1）で最短手数を求めるとき。",
      combo: "build_graphで隣接リスト作成後に bfs。",
      tags: ["最短路", "重みなし"],
      example: `N, M = MAP()
edges = []
for _ in range(M):
    a, b = MAP(); a -= 1; b -= 1
    edges.append((a, b))
g = build_graph(N, edges)
dist = bfs(g, 0)`
    },
    {
      name: "zero_one_bfs",
      category: "グラフ",
      complexity: "O(N+M)",
      desc: "辺重み0/1専用最短路。dijkstraより軽い。",
      useWhen: "辺のコストが0か1に限定されるとき。",
      combo: "build_weighted_graphの代わりに手で (to, w) を作ってよい。",
      tags: ["最短路", "0-1"],
      example: `N = INT()
g = [[] for _ in range(N)]
for _ in range(INT()):
    u, v, w = MAP()
    g[u].append((v, w))
dist = zero_one_bfs(g, 0)`
    },
    {
      name: "bellman_ford",
      category: "グラフ",
      complexity: "O(NM)",
      desc: "負辺対応の最短路。負閉路検出付き。",
      useWhen: "負辺がある問題で、最短距離や閉路判定が必要なとき。",
      combo: "edges配列を直接渡す。dijkstraの代替として使う。",
      tags: ["最短路", "負辺"],
      example: `N, M = MAP()
edges = [tuple(MAP()) for _ in range(M)]
dist, has_neg = bellman_ford(N, edges, 0)
print("NEG" if has_neg else dist[N-1])`
    },
    {
      name: "DSU",
      category: "グラフ",
      complexity: "償却 O(αN)",
      desc: "連結判定・併合。オンラインクエリで強い。",
      useWhen: "辺追加しながら連結性を答える問題。",
      combo: "kruskal内部でも使用。same/size/group_countが実戦的。",
      tags: ["Union-Find"],
      example: `uf = DSU(N)
for a, b in edges:
    uf.merge(a, b)
print(uf.group_count())`
    },
    {
      name: "WeightedDSU",
      category: "グラフ",
      complexity: "償却 O(αN)",
      desc: "weight[x]-weight[y]=w の差分制約を管理。",
      useWhen: "方程式型の差分制約の整合チェック。",
      combo: "矛盾判定は same 時に diff と期待値比較。",
      tags: ["差分制約"],
      example: `wuf = WeightedDSU(N)
ok = True
for x, y, w in constraints:
    if wuf.same(x, y):
        ok &= (wuf.diff(x, y) == w)
    else:
        wuf.merge(x, y, w)`
    },
    {
      name: "kruskal",
      category: "グラフ",
      complexity: "O(MlogM)",
      desc: "最小全域木（MST）を構築。",
      useWhen: "全頂点連結の最小コストを求めるとき。",
      combo: "内部でDSU使用。戻り値のconnectedも判定に使う。",
      tags: ["MST"],
      example: `cost, used, connected = kruskal(N, edges)
print(cost if connected else -1)`
    },
    {
      name: "topological_sort",
      category: "グラフ",
      complexity: "O(N+M)",
      desc: "DAGの順序付け。閉路ならNone。",
      useWhen: "依存関係順に処理したいとき。",
      combo: "順序に沿ってDP配列を更新するのが定番。",
      tags: ["DAG", "順序"],
      example: `order = topological_sort(g)
if order is None:
    print(-1)
else:
    for v in order:
        pass`
    },
    {
      name: "prefix_sum",
      category: "累積和",
      complexity: "構築 O(N), 取得 O(1)",
      desc: "配列の区間和を高速化。",
      useWhen: "静的配列で区間和クエリが多いとき。",
      combo: "binary_searchと組み合わせて条件探索に使える。",
      tags: ["区間和"],
      example: `A = LIST()
ps = prefix_sum(A)
l, r = MAP()
print(ps[r] - ps[l])`
    },
    {
      name: "prefix_sum_2d + range_sum_2d",
      category: "累積和",
      complexity: "構築 O(HW), 取得 O(1)",
      desc: "矩形和クエリを高速化。",
      useWhen: "2Dグリッドで多数の矩形問い合わせがあるとき。",
      combo: "grid入力後に1回構築、以降は問い合わせのみ。",
      tags: ["2D", "矩形"],
      example: `ps = prefix_sum_2d(grid)
ans = range_sum_2d(ps, y1, x1, y2, x2)`
    },
    {
      name: "Imos1D",
      category: "累積和",
      complexity: "更新 O(1), build O(N)",
      desc: "区間加算をまとめて適用。",
      useWhen: "更新回数が多く、最終配列だけ必要なとき。",
      combo: "build後にprefix_sumやmaxで解析。",
      tags: ["差分"],
      example: `imos = Imos1D(N)
for l, r in queries:
    imos.add(l, r, 1)
arr = imos.build()`
    },
    {
      name: "Combination",
      category: "数学",
      complexity: "初期化 O(N), 参照 O(1)",
      desc: "nCr/nPr/nHr/catalanを高速計算。",
      useWhen: "組合せクエリが複数回あるとき。",
      combo: "MOD変更時は生成時mod引数を合わせる。",
      tags: ["組合せ"],
      example: `comb = Combination(200000)
print(comb.nCr(N, K))`
    },
    {
      name: "sieve",
      category: "数学",
      complexity: "O(N log logN)",
      desc: "素数判定配列と素数一覧を返す。",
      useWhen: "多数の素数判定/列挙が必要なとき。",
      combo: "prime_factorsと合わせて整数論問題を短縮。",
      tags: ["素数"],
      example: `is_p, primes = sieve(10**6)
print(is_p[97], len(primes))`
    },
    {
      name: "pow_mod + mod_inverse",
      category: "数学",
      complexity: "O(logN)",
      desc: "高速べき乗と逆元。",
      useWhen: "mod計算で割り算が出るとき。",
      combo: "Combination内部と同系。整合性を保つ。",
      tags: ["mod"],
      example: `x = pow_mod(3, 100)
inv2 = mod_inverse(2)
print((x * inv2) % MOD)`
    },
    {
      name: "tree_parent + subtree_size",
      category: "木",
      complexity: "O(N)",
      desc: "親配列と部分木サイズを構築。",
      useWhen: "部分木クエリ/木DP前処理。",
      combo: "depth配列と合わせると祖先条件判定に有効。",
      tags: ["木", "前処理"],
      example: `parent = tree_parent(g, 0)
size = subtree_size(g, 0)
print(size[0])`
    },
    {
      name: "LCA",
      category: "木",
      complexity: "前処理 O(NlogN), クエリ O(logN)",
      desc: "最小共通祖先と距離。",
      useWhen: "木上の多数クエリ。",
      combo: "tree_depth不要。LCAが内部で保持。",
      tags: ["木", "クエリ"],
      example: `lca = LCA(g, 0)
print(lca.query(u, v), lca.dist(u, v))`
    },
    {
      name: "BIT",
      category: "データ構造",
      complexity: "O(logN)",
      desc: "一点加算・prefix和。",
      useWhen: "動的更新しながら和を取りたいとき。",
      combo: "compress_listと一緒に使うのが定番。",
      tags: ["Fenwick"],
      example: `bit = BIT(N)
bit.add(i, x)
print(bit.range_sum(l, r))`
    },
    {
      name: "SegTree",
      category: "データ構造",
      complexity: "O(logN)",
      desc: "一点更新・区間演算。",
      useWhen: "min/max/sum/gcd など区間クエリ。",
      combo: "compressした座標に対して使う構成も多い。",
      tags: ["セグ木"],
      example: `st = SegTree(N, op=min, e=INF)
st.build(A)
print(st.query(l, r))`
    },
    {
      name: "LazySegTree",
      category: "データ構造",
      complexity: "O(logN)",
      desc: "区間更新・区間取得。",
      useWhen: "大量の区間更新がある問題。",
      combo: "mapping/composition設計が要点。",
      tags: ["遅延セグ木"],
      example: `lst = LazySegTree(n, op, e, mapping, composition, identity)
lst.build(A)
lst.apply(l, r, f)
print(lst.query(l, r))`
    },
    {
      name: "SortedMultiset",
      category: "データ構造",
      complexity: "平均 O(√N)",
      desc: "順序付き重複集合。",
      useWhen: "中央値/順位/前後要素を扱うとき。",
      combo: "index/index_rightと組み合わせて個数計算。",
      tags: ["順序統計"],
      example: `ms = SortedMultiset()
ms.add(x)
print(ms.index(x), x in ms)`
    },
    {
      name: "RollingHash",
      category: "文字列",
      complexity: "前処理 O(N), 取得 O(1)",
      desc: "部分文字列同一性比較。",
      useWhen: "多数の部分一致判定が必要。",
      combo: "二分探索で最長一致長探索にも応用可能。",
      tags: ["文字列", "ハッシュ"],
      example: `rh = RollingHash(S)
same = rh.get(l1, r1) == rh.get(l2, r2)`
    },
    {
      name: "z_algorithm",
      category: "文字列",
      complexity: "O(N)",
      desc: "接頭辞一致長の配列。",
      useWhen: "パターンマッチ/周期判定。",
      combo: "pattern + '$' + text で出現位置検出が可能。",
      tags: ["文字列"],
      example: `z = z_algorithm(P + "$" + T)
for i, v in enumerate(z):
    if v == len(P):
        pass`
    },
    {
      name: "kmp_search",
      category: "文字列",
      complexity: "O(|T|+|P|)",
      desc: "パターン出現位置列挙。",
      useWhen: "厳密一致の高速検索。",
      combo: "kmp_tableを内部利用済み。",
      tags: ["文字列", "検索"],
      example: `pos = kmp_search(text, pattern)
print(len(pos))`
    },
    {
      name: "run_length_encode",
      category: "文字列",
      complexity: "O(N)",
      desc: "連続要素圧縮。",
      useWhen: "同値連続ブロックの処理。",
      combo: "結果をそのままDP遷移に使える。",
      tags: ["圧縮"],
      example: `rle = run_length_encode(S)
for ch, cnt in rle:
    pass`
    },
    {
      name: "binary_search_min / max",
      category: "二分探索",
      complexity: "O(log range)",
      desc: "単調判定関数で境界探索。",
      useWhen: "答えが単調性を持つ最小/最大値。",
      combo: "prefix_sumやdijkstra結果を判定関数で使う。",
      tags: ["境界"],
      example: `def check(x):
    return x * x >= N
ans = binary_search_min(0, 10**9, check)`
    },
    {
      name: "lis",
      category: "二分探索",
      complexity: "O(NlogN)",
      desc: "LIS長を取得。",
      useWhen: "増加列長のみ必要なとき。",
      combo: "座圧不要でそのまま使える。",
      tags: ["LIS"],
      example: `A = LIST()
print(lis(A, strict=True))`
    },
    {
      name: "compress / compress_list",
      category: "座標圧縮",
      complexity: "O(NlogN)",
      desc: "値域を詰めて配列系DSに載せる。",
      useWhen: "値が大きいが順序だけ必要。",
      combo: "BIT/SegTreeの前処理として使用。",
      tags: ["前処理"],
      example: `A = LIST()
mp, xs = compress(A)
C = compress_list(A)`
    },
    {
      name: "inversion_count",
      category: "座標圧縮",
      complexity: "O(NlogN)",
      desc: "転倒数を一発で返す。",
      useWhen: "並び替え回数の指標が必要。",
      combo: "内部で compress + BIT を実施済み。",
      tags: ["転倒数"],
      example: `A = LIST()
print(inversion_count(A))`
    },
    {
      name: "Output",
      category: "入出力",
      complexity: "add O(1)",
      desc: "出力をバッファしてまとめて吐く。",
      useWhen: "出力行が大量。",
      combo: "forループでadd、最後にflush。",
      tags: ["出力最適化"],
      example: `out = Output()
for v in ans:
    out.add(v)
out.flush()`
    },
    {
      name: "bfs_grid",
      category: "グラフ",
      complexity: "O(HW)",
      desc: "グリッド最短路。",
      useWhen: "壁あり迷路の最短距離。",
      combo: "STRSLで盤面入力、DIR4で探索。",
      tags: ["グリッド"],
      example: `H, W = MAP()
grid = STRSL(H)
dist = bfs_grid(grid, sy, sx, wall='#')`
    }
  ];

  const listEl = document.getElementById("referenceList");
  const recipeEl = document.getElementById("recipeList");
  const searchEl = document.getElementById("searchInput");
  const categoryEl = document.getElementById("categoryFilter");
  const countEl = document.getElementById("countLabel");
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebarToggle");
  let dynamicCopyCounter = 0;

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderCategoryOptions() {
    const categories = [...new Set(referenceData.map((item) => item.category))].sort((a, b) => a.localeCompare(b, "ja"));
    for (const category of categories) {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryEl.appendChild(option);
    }
  }

  function makeCopyBlock(code, className = "inline-copy") {
    dynamicCopyCounter += 1;
    const codeId = `dynamic-code-${dynamicCopyCounter}`;
    return `
      <div class="snippet ${className}">
        <div class="snippet__head">
          <span>最小コード例</span>
          <button class="copy-btn" data-copy-target="${codeId}">コピー</button>
        </div>
        <pre id="${codeId}"><code>${escapeHtml(code)}</code></pre>
      </div>
    `;
  }

  function renderRecipes() {
    if (!recipeEl) return;
    recipeEl.innerHTML = recipeData
      .map((recipe) => {
        return `
          <article class="recipe-card">
            <div class="recipe-head">
              <h3 class="recipe-title">${escapeHtml(recipe.title)}</h3>
              <span class="badge">組み合わせ</span>
            </div>
            <p class="recipe-flow">${escapeHtml(recipe.flow)}</p>
            ${makeCopyBlock(recipe.code)}
          </article>
        `;
      })
      .join("");
  }

  function renderReference() {
    const word = (searchEl.value || "").trim().toLowerCase();
    const category = categoryEl.value;

    const filtered = referenceData.filter((item) => {
      if (category !== "all" && item.category !== category) return false;
      if (!word) return true;
      const haystack = [item.name, item.desc, item.category, item.useWhen, item.combo, ...(item.tags || [])].join(" ").toLowerCase();
      return haystack.includes(word);
    });

    countEl.textContent = `${filtered.length}件 / 全${referenceData.length}件`;

    if (filtered.length === 0) {
      listEl.innerHTML = '<p class="ref-meta">一致する項目がありません。キーワードを変えてください。</p>';
      return;
    }

    listEl.innerHTML = filtered
      .map((item) => {
        const tags = (item.tags || []).map((tag) => `<span class="badge">${escapeHtml(tag)}</span>`).join("");
        return `
          <article class="ref-item">
            <div class="ref-top">
              <h3 class="ref-name">${escapeHtml(item.name)}</h3>
              <span class="badge">${escapeHtml(item.category)}</span>
              ${tags}
            </div>
            <p class="ref-desc">${escapeHtml(item.desc)}</p>
            <p class="ref-meta">計算量: ${escapeHtml(item.complexity)}</p>
            <p class="ref-usage"><strong>使う条件:</strong> ${escapeHtml(item.useWhen)}</p>
            <p class="ref-combo"><strong>組み合わせ:</strong> ${escapeHtml(item.combo)}</p>
            ${makeCopyBlock(item.example)}
          </article>
        `;
      })
      .join("");
  }

  async function handleCopy(button) {
    const targetId = button.getAttribute("data-copy-target");
    if (!targetId) return;
    const codeEl = document.getElementById(targetId);
    if (!codeEl) return;

    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(codeEl.textContent || "");
      button.textContent = "コピー済み";
    } catch {
      button.textContent = "失敗";
    }
    setTimeout(() => {
      button.textContent = original;
    }, 1200);
  }

  function bindCopyButtons() {
    document.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("copy-btn")) return;
      handleCopy(target);
    });
  }

  function bindSidebarToggle() {
    if (!toggleBtn || !sidebar) return;
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  function init() {
    if (!listEl || !searchEl || !categoryEl || !countEl) return;
    renderCategoryOptions();
    renderRecipes();
    renderReference();
    bindCopyButtons();
    bindSidebarToggle();

    searchEl.addEventListener("input", renderReference);
    categoryEl.addEventListener("change", renderReference);
  }

  init();
})();
