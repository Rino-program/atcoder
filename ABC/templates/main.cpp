#include <bits/stdc++.h>
using namespace std;

// 型定義
using ll = long long;
using ull = unsigned long long;
using ld = long double;
using pii = pair<int, int>;
using pll = pair<ll, ll>;
using vi = vector<int>;
using vl = vector<ll>;
using vs = vector<string>;
using vvi = vector<vector<int>>;
using vvl = vector<vector<ll>>;

// マクロ
#define rep(i, n) for (int i = 0; i < (int)(n); i++)
#define rep1(i, n) for (int i = 1; i <= (int)(n); i++)
#define repr(i, n) for (int i = (int)(n) - 1; i >= 0; i--)
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define sz(x) (int)(x).size()

// デバッグ用マクロ (提出時は無効化)
#ifdef LOCAL
#define debug(x) cerr << #x << " = " << (x) << endl
#define debug2(x,y) cerr << #x << " = " << (x) << ", " << #y << " = " << (y) << endl
#else
#define debug(x) 
#define debug2(x,y)
#endif

// 定数
const int INF = 1e9;  // 加算でオーバーフローしない値
const ll LINF = 1e18;
const ld PI = acos(-1.0);
const int MOD = 998244353;  // AtCoderで最頻出、切り替え時は 1000000007

// 便利関数
template<class T> inline bool chmax(T& a, T b) { if (a < b) { a = b; return true; } return false; }
template<class T> inline bool chmin(T& a, T b) { if (a > b) { a = b; return true; } return false; }

// gcd, lcm (C++14+ では std::gcd も使用可)
ll gcd(ll a, ll b) { return b ? gcd(b, a % b) : a; }
ll lcm(ll a, ll b) { return a / gcd(a, b) * b; }

// 高速べき乗 (オーバーフロー対策済み)
ll pow_mod(ll x, ll n, ll mod = MOD) {
    ll res = 1;
    x %= mod;
    while (n > 0) {
        if (n & 1) res = (__int128)res * x % mod;
        x = (__int128)x * x % mod;
        n >>= 1;
    }
    return res;
}

// 逆元計算 (mod が素数の場合)
ll mod_inverse(ll a, ll mod = MOD) {
    return pow_mod(a, mod - 2, mod);
}

// 階乗とその逆元のテーブル作成
pair<vl, vl> factorials(int n, ll mod = MOD) {
    vl fact(n + 1, 1), inv_fact(n + 1, 1);
    for (int i = 1; i <= n; i++) {
        fact[i] = (__int128)fact[i-1] * i % mod;
    }
    inv_fact[n] = mod_inverse(fact[n], mod);
    for (int i = n - 1; i > 0; i--) {
        inv_fact[i] = (__int128)inv_fact[i + 1] * (i + 1) % mod;
    }
    return {fact, inv_fact};
}

// 組み合わせ計算 (事前計算済みテーブル使用)
ll nCr(int n, int r, const vl& fact, const vl& inv_fact, ll mod = MOD) {
    if (r < 0 || r > n) return 0;
    return (__int128)fact[n] * inv_fact[r] % mod * inv_fact[n-r] % mod;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout << fixed << setprecision(15);  // 精度を上げる
    
    #ifdef LOCAL
    freopen("input.txt", "r", stdin);  // ローカルテスト用
    #endif
    
    // ===== サンプル =====
    // int N; cin >> N;
    // vi a(N); rep(i,N) cin >> a[i];
    // ll ans = accumulate(all(a), 0LL);
    // cout << ans << "\n";
    // ====================
    
    return 0;
}

// ===== Optional Utilities =====
// 必要なものだけコピペして使ってください。出力に影響しません。

// 基本的な方向ベクトル
const int dx4[4] = {1, 0, -1, 0};
const int dy4[4] = {0, 1, 0, -1};
const int dx8[8] = {1, 1, 0, -1, -1, -1, 0, 1};
const int dy8[8] = {0, 1, 1, 1, 0, -1, -1, -1};

// Union-Find
struct DSU {
    vector<int> parent, sz;
    DSU(int n = 0) { init(n); }
    void init(int n) {
        parent.resize(n);
        sz.assign(n, 1);
        iota(all(parent), 0);
    }
    int leader(int x) {
        if (parent[x] == x) return x;
        return parent[x] = leader(parent[x]);
    }
    bool merge(int a, int b) {
        a = leader(a);
        b = leader(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a;
        sz[a] += sz[b];
        return true;
    }
    bool same(int a, int b) { return leader(a) == leader(b); }
    int size(int x) { return sz[leader(x)]; }
};

// 座標圧縮
template<class T>
vector<T> compress(vector<T> v) {
    sort(all(v));
    v.erase(unique(all(v)), v.end());
    return v;
}

template<class T>
int get_index(const vector<T>& comp, const T& x) {
    return lower_bound(all(comp), x) - comp.begin();
}

// prefix sum (長さ n+1 の累積和, ps[i] = a[0..i-1] 合計)
template<class T>
vector<long long> prefix_sum_ll(const vector<T>& a){
    vector<long long> ps(a.size()+1,0);
    for(size_t i=0;i<a.size();++i) ps[i+1]=ps[i]+(long long)a[i];
    return ps;
}

// 入力ヘルパ
template<class T>
vector<T> read_vec(int n) {
    vector<T> a(n);
    rep(i, n) cin >> a[i];
    return a;
}

// Fenwick Tree (BIT) : 0-indexed
struct BIT {
    int n; vector<ll> bit;
    BIT(int n=0){ init(n); }
    void init(int n_){ n = n_; bit.assign(n+1, 0); }
    // a[i] += x
    void add(int i, ll x){ for(++i; i<=n; i += i & -i) bit[i] += x; }
    // sum a[0..i]
    ll sum_prefix(int i){ ll s=0; for(++i; i>0; i -= i & -i) s += bit[i]; return s; }
    // sum a[l..r-1]
    ll sum_range(int l,int r){ if(r<=l) return 0; return sum_prefix(r-1) - (l? sum_prefix(l-1):0); }
    // sum_prefix(idx) >= w となる最小のidx (存在しない場合 n)
    int lower_bound(ll w) {
        if (w <= 0) return 0;
        int pos = 0;
        for (int k = 1; k < n; k <<= 1);
        for (; k > 0; k >>= 1) {
            if (pos + k < n && bit[pos + k] < w) {
                w -= bit[pos + k];
                pos += k;
            }
        }
        return pos;
    }
};

// Segment Tree (range sum, point update) : 0-indexed 半開区間 [l,r)
struct SegTree {
    int n; vector<ll> seg; // サイズ 2*n (1-based 内部)
    SegTree(int n_=0){ if(n_) init(n_); }
    void init(int n_){ n=1; while(n < n_) n <<= 1; seg.assign(2*n, 0); }
    // 点 i に値 v (build 用) : 後で build() を呼ぶ
    void set_val(int i, ll v){ seg[i + n] = v; }
    void build(){ for(int i = n-1; i; --i) seg[i] = seg[i<<1] + seg[i<<1|1]; }
    // a[i] = v (上書き)
    void update(int i, ll v){ int p = i + n; seg[p] = v; for(p >>= 1; p; p >>= 1) seg[p] = seg[p<<1] + seg[p<<1|1]; }
    // 区間和 [l,r)
    ll query(int l, int r){ ll res = 0; for(l += n, r += n; l < r; l >>=1, r >>=1){ if(l & 1) res += seg[l++]; if(r & 1) res += seg[--r]; } return res; }
};

// Range Minimum Query Segment Tree
struct RMQSegTree {
    int n; vector<ll> seg;
    const ll INF_VAL = LINF;
    RMQSegTree(int n_=0){ if(n_) init(n_); }
    void init(int n_){ n=1; while(n < n_) n <<= 1; seg.assign(2*n, INF_VAL); }
    void set_val(int i, ll v){ seg[i + n] = v; }
    void build(){ for(int i = n-1; i; --i) seg[i] = min(seg[i<<1], seg[i<<1|1]); }
    void update(int i, ll v){ int p = i + n; seg[p] = v; for(p >>= 1; p; p >>= 1) seg[p] = min(seg[p<<1], seg[p<<1|1]); }
    ll query(int l, int r){ ll res = INF_VAL; for(l += n, r += n; l < r; l >>=1, r >>=1){ if(l & 1) res = min(res, seg[l++]); if(r & 1) res = min(res, seg[--r]); } return res; }
};

// 二分探索ヘルパー
template<class F>
ll binary_search(ll ok, ll ng, F check) {
    while (abs(ok - ng) > 1) {
        ll mid = (ok + ng) / 2;
        if (check(mid)) ok = mid;
        else ng = mid;
    }
    return ok;
}

// エラトステネス (is_prime と primes を返す)
pair<vector<bool>, vector<int>> sieve(int N){
    vector<bool> is(N+1, true); is[0]=false; if(N>=1) is[1]=false; 
    for(int p=2; p*p<=N; ++p) if(is[p]) for(long long q=1LL*p*p; q<=N; q+=p) is[(int)q]=false;
    vector<int> primes; for(int i=2;i<=N;i++) if(is[i]) primes.push_back(i);
    return {is, primes};
}

// DFS (グラフ探索)
void dfs(const vvi& g, int v, vector<bool>& visited) {
    visited[v] = true;
    for (int to : g[v]) {
        if (!visited[to]) dfs(g, to, visited);
    }
}

// トポロジカルソート
vi topological_sort(const vvi& g) {
    int n = g.size();
    vi in_degree(n, 0);
    for (int v = 0; v < n; v++) {
        for (int to : g[v]) in_degree[to]++;
    }
    
    queue<int> q;
    for (int i = 0; i < n; i++) {
        if (in_degree[i] == 0) q.push(i);
    }
    
    vi result;
    while (!q.empty()) {
        int v = q.front(); q.pop();
        result.push_back(v);
        for (int to : g[v]) {
            in_degree[to]--;
            if (in_degree[to] == 0) q.push(to);
        }
    }
    return result.size() == n ? result : vi{}; // 空の場合は閉路あり
}

// ローリングハッシュ (文字列)
struct RollingHash {
    static const ll MOD1 = 1000000007, MOD2 = 1000000009;
    static const ll BASE1 = 1007, BASE2 = 2009;
    int n; string s;
    vl hash1, hash2, pow1, pow2;
    
    RollingHash(const string& str) : n(str.size()), s(str) {
        hash1.assign(n + 1, 0); hash2.assign(n + 1, 0);
        pow1.assign(n + 1, 1); pow2.assign(n + 1, 1);
        
        for (int i = 0; i < n; i++) {
            hash1[i + 1] = (hash1[i] * BASE1 + s[i]) % MOD1;
            hash2[i + 1] = (hash2[i] * BASE2 + s[i]) % MOD2;
            pow1[i + 1] = pow1[i] * BASE1 % MOD1;
            pow2[i + 1] = pow2[i] * BASE2 % MOD2;
        }
    }
    
    pair<ll, ll> get(int l, int r) { // [l, r)
        ll h1 = (hash1[r] - hash1[l] * pow1[r - l]) % MOD1;
        ll h2 = (hash2[r] - hash2[l] * pow2[r - l]) % MOD2;
        if (h1 < 0) h1 += MOD1;
        if (h2 < 0) h2 += MOD2;
        return {h1, h2};
    }
};

/* 使用例 (コピペ用)
// 数学系
// auto [fact, inv_fact] = factorials(200000); ll c = nCr(n, r, fact, inv_fact);

// データ構造
// BIT bit(N); bit.add(i, x); ll s = bit.sum_range(l,r); int pos = bit.lower_bound(w);
// DSU uf(N); uf.merge(a,b); bool connected = uf.same(x,y);

// グラフ
// vi topo = topological_sort(g); if(topo.empty()) { /* 閉路検出 */ }
// vector<bool> visited(N); dfs(g, start, visited);

// 文字列
// RollingHash rh(s); auto hash_val = rh.get(l, r);

// 二分探索
// ll ans = binary_search(ok, ng, [&](ll mid) { return check(mid); });
*/

// (EOF)
    
    