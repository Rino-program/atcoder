
#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    unordered_map<int, long long> mp; // i+Aiの値が何回出たかを記録
    long long ans = 0;
    
    // j=1,2,...,Nに対して処理（0-indexedなので実際はj=0,1,...,N-1）
    for (int j = 0; j < n; j++) {
        int idx = j + 1; // 1-indexedに変換
        
        // 条件を満たすiの個数を答えに加算
        // j-Aj と等しい i+Ai の個数を探す
        ans += mp[idx - a[j]];
        
        // 現在のjについて j+Aj をmapに記録（未来のjのため）
        mp[idx + a[j]]++;
    }
    cout << ans << endl;
    return 0;
}