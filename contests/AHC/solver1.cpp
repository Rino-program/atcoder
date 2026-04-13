#include <iostream>
#include <vector>
#include <string>

/**
 * Pythonのsys.stdin.readlineとmap(int, input().split())の動作を再現
 */
int main() {
    // 高速な入出力設定
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int N, M, C;
    if (!(std::cin >> N >> M >> C)) return 0;

    // d の読み込み (Python版では使用されていないが、入力として存在する)
    std::vector<int> d(M);
    for (int i = 0; i < M; ++i) {
        std::cin >> d[i];
    }

    // f (2次元配列) の読み込み (同じく使用されていないが、入力として存在する)
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            int temp;
            std::cin >> temp;
        }
    }

    // 出力文字列の構築
    // Python版: for _ in range(4, N - 1): ans.append('D')
    for (int i = 4; i < N - 1; ++i) {
        std::cout << "D\n";
    }

    // Python版: 蛇行移動ロジック
    for (int col = 1; col < N; ++col) {
        std::cout << "R\n";
        if (col % 2 == 1) {
            for (int i = 0; i < N - 1; ++i) {
                std::cout << "U\n";
            }
        } else {
            for (int i = 0; i < N - 1; ++i) {
                std::cout << "D\n";
            }
        }
    }

    return 0;
}