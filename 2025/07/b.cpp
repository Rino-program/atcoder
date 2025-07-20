#include <iostream>
#include <fstream>
#include <chrono>
using namespace std;

int main() {
    // 入出力の高速化
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n;
    cin >> n;
    
    auto start = chrono::high_resolution_clock::now();
    
    ofstream fout("output.txt");
    for (int i = 1; i <= n; i++) {
        fout << i << ".\n";
    }
    fout << "finish\n";
    fout.close();
    
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double, milli> duration = end - start;
    cout << "Execution time: " << duration.count() << " milliseconds" << endl;

    return 0;
}