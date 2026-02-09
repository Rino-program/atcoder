// AtCoder競技プログラミング専用ヘッダー
// 使用方法: #include "atcoder.hpp" をmain.cppの先頭に追加

#pragma once
#include <bits/stdc++.h>
using namespace std;

// ===== 型定義 =====
using ll = long long;
using ull = unsigned long long;
using ld = long double;
using pii = pair<int, int>;
using pll = pair<ll, ll>;
using pdd = pair<double, double>;
using vi = vector<int>;
using vl = vector<ll>;
using vd = vector<double>;
using vs = vector<string>;
using vb = vector<bool>;
using vc = vector<char>;
using vvi = vector<vector<int>>;
using vvl = vector<vector<ll>>;
using vvd = vector<vector<double>>;
using vvs = vector<vector<string>>;
using vvb = vector<vector<bool>>;
using vpii = vector<pii>;
using vpll = vector<pll>;

// ===== よく使うマクロ =====
#define rep(i, n) for (int i = 0; i < (int)(n); i++)
#define rep1(i, n) for (int i = 1; i <= (int)(n); i++)
#define repr(i, n) for (int i = (int)(n) - 1; i >= 0; i--)
#define repd(i, a, b) for (int i = (int)(a); i < (int)(b); i++)
#define reps(i, a, b) for (int i = (int)(a); i <= (int)(b); i++)
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define sz(x) (int)(x).size()

// ===== 定数 =====
const int INF = 1e9 + 7;
const ll LINF = 1e18;
const ld EPS = 1e-9;
const ld PI = acos(-1.0);
const int MOD = 998244353;

// ===== 方向ベクトル =====
const int dx4[4] = {1, 0, -1, 0};
const int dy4[4] = {0, 1, 0, -1};
const int dx8[8] = {1, 1, 0, -1, -1, -1, 0, 1};
const int dy8[8] = {0, 1, 1, 1, 0, -1, -1, -1};

// ===== 便利関数 =====
template<class T> inline bool chmax(T& a, T b) { return a < b ? a = b, true : false; }
template<class T> inline bool chmin(T& a, T b) { return a > b ? a = b, true : false; }
template<class T> inline T abs_diff(T a, T b) { return a > b ? a - b : b - a; }

// 高速べき乗
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

// 逆元計算
ll mod_inverse(ll a, ll mod = MOD) {
    return pow_mod(a, mod - 2, mod);
}

// ===== 頻出アルゴリズム =====

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
        return parent[x] == x ? x : parent[x] = leader(parent[x]);
    }
    bool merge(int a, int b) {
        a = leader(a); b = leader(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a;
        sz[a] += sz[b];
        return true;
    }
    bool same(int a, int b) { return leader(a) == leader(b); }
    int size(int x) { return sz[leader(x)]; }
};

// BIT (Fenwick Tree)
struct BIT {
    int n; vector<ll> bit;
    BIT(int n=0){ init(n); }
    void init(int n_){ n = n_; bit.assign(n+1, 0); }
    void add(int i, ll x){ for(++i; i<=n; i += i & -i) bit[i] += x; }
    ll sum_prefix(int i){ ll s=0; for(++i; i>0; i -= i & -i) s += bit[i]; return s; }
    ll sum_range(int l,int r){ return l <= r ? sum_prefix(r) - (l ? sum_prefix(l-1) : 0) : 0; }
};

// セグメントツリー（範囲和）
struct SegTree {
    int n; vector<ll> seg;
    SegTree(int n_=0){ if(n_) init(n_); }
    void init(int n_){ n=1; while(n < n_) n <<= 1; seg.assign(2*n, 0); }
    void update(int i, ll v){ int p = i + n; seg[p] = v; for(p >>= 1; p; p >>= 1) seg[p] = seg[p<<1] + seg[p<<1|1]; }
    ll query(int l, int r){ ll res = 0; for(l += n, r += n; l < r; l >>=1, r >>=1){ if(l & 1) res += seg[l++]; if(r & 1) res += seg[--r]; } return res; }
};

// ===== 入出力補助 =====
template<class T> vector<T> read_vec(int n) {
    vector<T> a(n);
    rep(i, n) cin >> a[i];
    return a;
}

template<class T> void print_vec(const vector<T>& a, const string& sep = " ") {
    rep(i, sz(a)) cout << a[i] << (i == sz(a) - 1 ? "\n" : sep);
}

// Yes/No出力
void Yes() { cout << "Yes\n"; }
void No() { cout << "No\n"; }
void yes() { cout << "yes\n"; }
void no() { cout << "no\n"; }
void YES() { cout << "YES\n"; }
void NO() { cout << "NO\n"; }

// ===== デバッグ用 =====
#ifdef LOCAL
template<class T> void debug_vec(const vector<T>& v, const string& name = "") {
    if (!name.empty()) cerr << name << ": ";
    cerr << "[";
    rep(i, sz(v)) cerr << v[i] << (i == sz(v) - 1 ? "" : ", ");
    cerr << "]\n";
}
#define debug(x) cerr << #x << " = " << (x) << endl
#define debug2(x,y) cerr << #x << " = " << (x) << ", " << #y << " = " << (y) << endl
#define debugv(v) debug_vec(v, #v)
#else
#define debug(x)
#define debug2(x,y)
#define debugv(v)
#endif

// ===== 座標圧縮 =====
template<class T> vector<T> compress(vector<T> v) {
    sort(all(v));
    v.erase(unique(all(v)), v.end());
    return v;
}

template<class T> int get_index(const vector<T>& comp, const T& x) {
    return lower_bound(all(comp), x) - comp.begin();
}

// ===== 二分探索 =====
template<class F> ll binary_search(ll ok, ll ng, F check) {
    while (abs(ok - ng) > 1) {
        ll mid = (ok + ng) / 2;
        if (check(mid)) ok = mid;
        else ng = mid;
    }
    return ok;
}

// ===== 素数関連 =====
pair<vector<bool>, vector<int>> sieve(int N){
    vector<bool> is(N+1, true);
    if (N >= 0) is[0] = false;
    if (N >= 1) is[1] = false;
    for(int p = 2; p * p <= N; ++p) {
        if (is[p]) {
            for(long long q = 1LL * p * p; q <= N; q += p) {
                is[(int)q] = false;
            }
        }
    }
    vector<int> primes;
    for(int i = 2; i <= N; i++) {
        if (is[i]) primes.push_back(i);
    }
    return {is, primes};
}

// ===== 最短経路（グラフ） =====
vector<int> bfs_dist(const vvi& g, int s) {
    vector<int> dist(sz(g), -1);
    queue<int> q;
    dist[s] = 0;
    q.push(s);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        for (int to : g[v]) {
            if (dist[to] == -1) {
                dist[to] = dist[v] + 1;
                q.push(to);
            }
        }
    }
    return dist;
}

vector<ll> dijkstra(const vector<vector<pll>>& g, int s) {
    vector<ll> dist(sz(g), LINF);
    priority_queue<pll, vector<pll>, greater<pll>> pq;
    dist[s] = 0;
    pq.emplace(0, s);
    while (!pq.empty()) {
        auto [d, v] = pq.top(); pq.pop();
        if (d != dist[v]) continue;
        for (auto [to, w] : g[v]) {
            if (chmin(dist[to], d + w)) {
                pq.emplace(dist[to], to);
            }
        }
    }
    return dist;
}

// ===== トポロジカルソート =====
vi topological_sort(const vvi& g) {
    int n = sz(g);
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
    return sz(result) == n ? result : vi{};
}

// ===== 組み合わせ・階乗 =====
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

ll nCr(int n, int r, const vl& fact, const vl& inv_fact, ll mod = MOD) {
    if (r < 0 || r > n) return 0;
    return (__int128)fact[n] * inv_fact[r] % mod * inv_fact[n-r] % mod;
}
