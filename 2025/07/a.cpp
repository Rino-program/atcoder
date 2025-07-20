#include <iostream>
#include <bitset>
#include <string>
#include <sstream>
#include <set>
#include <list>
using namespace std;

int main() {
    int t;
    list<string> l;
    cin >> t;
    while (t--) {
        int n, s;
        cin >> n >> s;
        stringstream ss;
        ss << s;
        string sstr = ss.str();
        set<int> se;

        for (int i = 0; i < sstr.size(); i++) {
            if (sstr[i] == '1') {
                bitset<18> binary(i);
                ostringstream oss;
                oss << binary;
                string binaryString = oss.str();
                for (int j = 0; j < binaryString.size(); j++) {
                    if (binaryString[j] == '1') {
                        se.insert(j);
                    }
                }
            }
        }
        if (se.size() == n) {
            l.push_back("No");
        } else {
            l.push_back("Yes");
        }
    }
    for (const string& result : l) {
        cout << result << endl;
    }
    return 0;
}
