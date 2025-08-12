#include <iostream>
#include <set>
#include <vector>

using namespace std;
#define rep(i, n) for (int i = 0; i < (n); i++)

int main() {
    int n;
    cin >> n;
    set<int> A;
    vector<int> all;
    vector<int> max_li = {0};
    vector<int> max_s;
    for (int i = 0; i < n; i++) { // 予測する
        int x;
        cin >> x;
        all.push_back(x);
        A.insert(x);
        max_s.push_back(A.size());
        int v = A.size() + n - i;
        if (v >= max_li.back()) {
            if (v > max_li.back()) {
                max_li.clear();
            }
            max_li.push_back(i);
        }
    }

    int l = 0;
    int max_v = 0;
    for (int i : max_li) { // 予測結果から詳しく計算する
        int sum = max_s[l];
        int s = 0;
        vector<int> li(all.begin() + i, all.begin() + all.size());
        for (int j : li) {
            s += j;
        }
        if (s > max_v) {
            max_v = s;
        }
        l++;
    }

    cout << max_v << endl;

    return 0;
}