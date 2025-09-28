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

// 定数
const int INF = 1e9 + 7;
const ll LINF = 1e18;
const ld PI = acos(-1.0);
const int MOD = 1e9 + 7;
// const int MOD = 998244353;

// 便利関数
template<class T> inline bool chmax(T& a, T b) { if (a < b) { a = b; return true; } return false; }
template<class T> inline bool chmin(T& a, T b) { if (a > b) { a = b; return true; } return false; }

// デバッグ用（提出時は削除またはコメントアウト）
#ifdef DEBUG
#define dbg(x) cerr << #x << " = " << (x) << endl
#define dbg2(x, y) cerr << #x << " = " << (x) << ", " << #y << " = " << (y) << endl
#else
#define dbg(x)
#define dbg2(x, y)
#endif

// gcd, lcm
ll gcd(ll a, ll b) { return b ? gcd(b, a % b) : a; }
ll lcm(ll a, ll b) { return a / gcd(a, b) * b; }

// 高速べき乗
ll pow_mod(ll x, ll n, ll mod = MOD) {
    ll res = 1;
    while (n > 0) {
        if (n & 1) res = res * x % mod;
        x = x * x % mod;
        n >>= 1;
    }
    return res;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout << fixed << setprecision(10);
    
    // ここにコードを書く
    
    
    
    return 0;
}