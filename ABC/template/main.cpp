#include <bits/stdc++.h>
// #include <atcoder/all>  // 必要に応じてコメントアウト

// AtCoder競プロテンプレート（パフォーマンス測定機能付き）
using namespace std;
using ll = long long;
using Pa = pair<int, int>;
using Vec = vector<int>;
using VecVec = vector<Vec>;
using VecPa = vector<Pa>;

// 定数定義
inline constexpr int INF = 1'000'000'000;
inline constexpr ll LINF = (ll)4e18;
inline constexpr int MOD = 1'000'000'007;

// 高速入出力の初期化
struct AutoIo { AutoIo(){ ios::sync_with_stdio(false); cin.tie(nullptr); } };
static AutoIo auto_io;

// パフォーマンス測定クラス
class PerformanceMonitor {
private:
    chrono::high_resolution_clock::time_point start_time;
    size_t initial_memory;
    
public:
    PerformanceMonitor() {
        start_time = chrono::high_resolution_clock::now();
    }
    
    void report() {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        
        cerr << "[Performance] Time: " << duration.count() << "ms" << endl;
        
        // TLE警告
        if (duration.count() > 2000) {
            cerr << "⚠️  TLE Warning: Execution time > 2000ms" << endl;
        }
    }
};

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

// 安全版数学関数
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

inline ll ceil_div_safe(ll a, ll b) {
    assert(b != 0);
    ll q = a / b;
    ll r = a % b;
    if (r != 0 && ((r > 0) == (b > 0))) q += 1;
    return q;
}

inline ll floor_div_safe(ll a, ll b) {
    assert(b != 0);
    ll q = a / b;
    ll r = a % b;
    if (r != 0 && ((r > 0) != (b > 0))) q -= 1;
    return q;
}

int main() {
    PerformanceMonitor monitor;
    
    // TODO: ここに問題の解法を実装
    
    monitor.report();
    return 0;
}