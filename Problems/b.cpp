#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <stack>
#include <queue>

using namespace std;
using ll = long long;
using str = string;
using Interval = pair<ll, ll>;
#define rep(i, n) for (ll i = 0; i < (n); ++i)

int max_element_index(const vector<ll>& v) {
    return max_element(v.begin(), v.end()) - v.begin();
}

int binary_search(const vector<ll>& v, ll target) {
    ll left = 0;
    ll right = v.size();
    while (right - left > 1) {
        ll mid = (left + right) / 2;
        if (v[mid] == target) return mid;
        if (v[mid] >= target) right = mid;
        else left = mid;
    }
    return -1;
}

int main() {
    int n;
    cin >> n;
    

    

    return 0;
}