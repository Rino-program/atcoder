#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;
#define rep(i, n) for (int i = 0; i < (n); i++)

int main() {
    int n, w;
    cin >> n >> w;
    vector<int> a(n);
    rep(i, n) cin >> a[i];

    rep(i, 1 << n) {
        tmp = 0;
        rep(j, n) {
            if (i & (1 << j)) {
                tmp += a[j];
            }
        }
        if (tmp == w) {
            cout << "Yes" << endl;
            return 0;
        }
    }
    cout << "No" << endl;

    return 0;
}