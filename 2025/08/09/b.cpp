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
        int s = 0, f = 0;
        if (*max_element(a.begin(), a.end()) < i) {
            cout << -1 << endl;
            continue;
        }
        for (int j : a){
            
        }
        cout << s << endl;
    }
    return 0;
}