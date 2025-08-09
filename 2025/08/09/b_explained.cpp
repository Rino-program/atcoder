// 充填率最大化問題 解説付き実装
// S の部分文字列で、両端が 't' かつ長さ3以上、内部に 't' が1個以上あるものについて
// 充填率 = (x−2)/(|t|−2) (x: 部分文字列内の 't' の個数) を最大化する
// |t|: 部分文字列の長さ
// x: 部分文字列内の 't' の個数
// 例: S = "ttattx" の部分文字列 "ttatt" (位置0..4) → |t|=5, x=4, 充填率=2/3 ≈ 0.666...
// アルゴリズム: 't' の出現位置列を作り、全ての (i, j) (j-i>=2) で (j-i-1)/(pos[j]-pos[i]-1) を最大化
// O(M^2) だが M ('t' の個数) が小さければ十分高速

#include <bits/stdc++.h>
using namespace std;

int main() {
    string S;
    cin >> S;
    vector<int> pos;
    for (int i = 0; i < (int)S.size(); ++i) {
        if (S[i] == 't') pos.push_back(i);
    }
    int M = pos.size();
    if (M < 3) {
        cout << 0 << '\n';
        return 0;
    }
    double ans = 0.0;
    // 全ての (i, j) (j-i>=2) で計算
    for (int i = 0; i < M; ++i) {
        for (int j = i + 2; j < M; ++j) {
            int len = pos[j] - pos[i] + 1;
            int x = j - i + 1;
            if (len - 2 == 0) continue; // 0除算防止
            double rate = (double)(x - 2) / (len - 2);
            ans = max(ans, rate);
        }
    }
    cout << fixed << setprecision(15) << ans << '\n';
    return 0;
}
