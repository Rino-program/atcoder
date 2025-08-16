#include <iostream>
#include <vector>
#include <algorithm>
#include <string>

using namespace std;
using ll = long long;
using Interval = pair<int, int>;
#define rep(i, n) for (int i = 0; i < (n); ++i)

int max_element_index(const vector<int>& v) {
    return max_element(v.begin(), v.end()) - v.begin();
}

int binary_search(const vector<int>& v, int target) {
    int left = 0;
    int right = v.size();
    while (left - right > 1) {
        int mid = (left + right) / 2;
        if (v[mid] == target) return mid;
        if (v[mid] >= target) right = mid;
        else left = mid;
    }
    return -1;
}

int main() {
    int n, m;
    string s, t;
    cin >> n >> m >> s >> t;
    vector<Interval> a(m);
    rep(i, m) cin >> a[i].first >> a[i].second;

    vector<int> b(n, -1);
    vector<int> c(n, -1);
    rep(i, m) {
        int l = a[i].first, r = a[i].second;
        b[l - 1] *= -1;
        c[r - 1] *= -1;
    }

    bool bo = false, f = false;
    rep(i, n) {
        if (b[i] == 1) {
            if (bo == true) {
                bo = false;
            } else {
                bo = true;
            }
        }
        if (c[i] == 1) {
            f = true;
        }
        
        if (bo) {
            s[i] = t[i];
        }
        if (f) {
            if (bo == true) {
                bo = false;
            } else {
                bo = true;
            }
        }
    }

    cout << s << endl;

    return 0;
}