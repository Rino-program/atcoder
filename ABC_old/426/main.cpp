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

// ===== 基本マクロ =====
#define rep(i, n) for (int i = 0; i < (int)(n); i++)
#define rep1(i, n) for (int i = 1; i <= (int)(n); i++)
#define repr(i, n) for (int i = (int)(n) - 1; i >= 0; i--)
#define repd(i, a, b) for (int i = (int)(a); i < (int)(b); i++)
#define reps(i, a, b) for (int i = (int)(a); i <= (int)(b); i++)
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define sz(x) (int)(x).size()
#define pb push_back
#define eb emplace_back
#define mp make_pair
#define fi first
#define se second

// ===== デバッグ用マクロ =====
#ifdef LOCAL
#define debug(x) cerr << #x << " = " << (x) << endl
#define debug2(x,y) cerr << #x << " = " << (x) << ", " << #y << " = " << (y) << endl
#define debug3(x,y,z) cerr << #x << " = " << (x) << ", " << #y << " = " << (y) << ", " << #z << " = " << (z) << endl
#define debugv(v) cerr << #v << " = "; for(auto x : v) cerr << x << " "; cerr << endl
#else
#define debug(x)
#define debug2(x,y)
#define debug3(x,y,z)
#define debugv(v)
#endif

// ===== 定数 =====
const int INF = 1e9 + 7;  // 安全な値
const ll LINF = 1e18;
const ld EPS = 1e-9;
const ld PI = acos(-1.0);
const int MOD = 998244353;  // AtCoderで最頻出
// const int MOD = 1000000007;  // 切り替え時用

// ===== 方向ベクトル =====
const int dx4[4] = {1, 0, -1, 0};
const int dy4[4] = {0, 1, 0, -1};
const int dx8[8] = {1, 1, 0, -1, -1, -1, 0, 1};
const int dy8[8] = {0, 1, 1, 1, 0, -1, -1, -1};

// 便利関数
template<class T> inline bool chmax(T& a, T b) { if (a < b) { a = b; return true; } return false; }
template<class T> inline bool chmin(T& a, T b) { if (a > b) { a = b; return true; } return false; }

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout << fixed << setprecision(15);  // 精度を上げる


    // ===== 入力 =====
    ll N, Q, x, y;
    cin >> N >> Q;
    ll m = 0;
    vl pc(N, 1);
    rep(i, Q) {
        cin >> x >> y;
        x--;
        y--;
        if (m >= x) {cout << 0 << endl; continue;}
        ll s = 0;
        for (ll i = m; i <= x; i++) {
            s += pc[i];
            pc[i] = 0;
        }
        pc[y] += s;
        cout << s << endl;
    }

    return 0;
}