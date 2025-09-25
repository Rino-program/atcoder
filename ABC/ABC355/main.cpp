#include <bits/stdc++.h>
#include <atcoder/all>

// 汎用的な競プロテンプレート（少しだけ整理・改良した版）
using namespace std;
using ll = long long;
using Pa = pair<int, int>;
using Vec = vector<int>;
using VecVec = vector<Vec>;
using VecPa = vector<Pa>;

// 定数は constexpr / inline で定義しておくと良いです
inline constexpr int INF = 1'000'000'000;
inline constexpr ll LINF = (ll)4e18;
inline constexpr int MOD = 1'000'000'007;

// 高速入出力の初期化（グローバルに一つ置くパターン）
struct AutoIo { AutoIo(){ ios::sync_with_stdio(false); cin.tie(nullptr); } };
static AutoIo auto_io;

// 汎用ユーティリティ
template<typename T> inline bool chmax(T& a, const T& b) noexcept {
    if (a < b) { a = b; return true; }
    return false;
}
template<typename T> inline bool chmin(T& a, const T& b) noexcept {
    if (b < a) { a = b; return true; }
    return false;
}

// DEBUG 用マクロ（LOCAL を定義してビルドすると有効）
#ifdef LOCAL
#define dbg(...) Debug::print(#__VA_ARGS__, __VA_ARGS__)
struct Debug {
    template<class T> static void show(const string& name, const T& v){ cerr<<name<<" = "<<v<<"\n"; }
    template<class T, class... Ts> static void print(const string& names, const T& v, const Ts&... vs){
        size_t pos = names.find(','); 
        if (pos==string::npos){ show(names, v); } 
        else {
            string cur = names.substr(0,pos);
            while(!cur.empty() && isspace(cur.back())) cur.pop_back();
            show(cur, v);
            print(names.substr(pos+1), vs...);
        }
    }
};
#else
#define dbg(...) do{}while(0)
#endif

// 整数向け安全版 gcd / ceil / floor（符号処理に注意）
inline ll gcd_ll_safe(ll a, ll b) noexcept {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) {
        ll t = a % b;
        a = b;
        b = t;
    }
    return a;
}

// 整数の切り上げ除算（a / b の ceil）
// b != 0 を仮定。符号混在にも対応。
inline ll ceil_div_safe(ll a, ll b) {
    assert(b != 0);
    ll q = a / b;
    ll r = a % b;
    if (r != 0 && ((r > 0) == (b > 0))) q += 1;
    return q;
}

// 整数の切り捨て除算（a / b の floor）
// b != 0 を仮定。符号混在にも対応。
inline ll floor_div_safe(ll a, ll b) {
    assert(b != 0);
    ll q = a / b;
    ll r = a % b;
    if (r != 0 && ((r > 0) != (b > 0))) q -= 1;
    return q;
}

int main() {
    ios::sync_with_stdio(false); // 二重でも安全（AutoIo 経由で既に設定済み）
    cin.tie(nullptr);

    return 0;
}