#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>

using namespace std;

int main() {
    int n, q, sum;
    cin >> n >> q;
    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    vector<int> b(q);
    for (int i = 0; i < q; i++) {
        cin >> b[i];
    }

    for (int i : b) {
        int s = 0;
        for (int j : a) {
            if (j < i) s += j;
            else s += i;
        }
        cout << s + 1 << endl;
    }
    return 0;
}