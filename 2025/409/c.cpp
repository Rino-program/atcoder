#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    string s;
    cin >> n >> s;
    
    vector<int> pos_a, pos_b;
    
    // AとBの位置を記録
    for (int i = 0; i < 2 * n; i++) {
        if (s[i] == 'A') {
            pos_a.push_back(i);
        } else {
            pos_b.push_back(i);
        }
    }
    
    // パターン1: 奇数位置(1,3,5,...)にAを配置
    int cost1 = 0;
    for (int k = 0; k < n; k++) {
        cost1 += abs(pos_a[k] - (2 * k + 1));
    }
    
    // パターン2: 偶数位置(0,2,4,...)にAを配置
    int cost2 = 0;
    for (int k = 0; k < n; k++) {
        cost2 += abs(pos_a[k] - (2 * k));
    }
    
    cout << min(cost1, cost2) << endl;
    return 0;
}