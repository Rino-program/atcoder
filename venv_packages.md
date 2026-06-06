# 仮想環境パッケージ管理 (.venv-pypy311)

作成日: 2026-02-27
Python実行環境: PyPy 3.11.13 (C:\Rino-program\AtCoder\\.pypy\pypy3.11-v7.3.20-win64\pypy3.11.exe)

## インストール状況

| パッケージ名 | 要求バージョン | インストール成否 | 備考 |
| :--- | :--- | :---: | :--- |
| PuLP | 3.2.2 | × | |
| ac-library-python | - | ○ | AtCoder Library (Python版) |
| acl-cpp-python | 0.6.2 | × | C++ビルド環境エラー |
| bitarray | 3.6.0 | × | fatal error C1083: 'io.h' no such file |
| cppyy | 3.5.0 | × | |
| more-itertools | 10.7.0 | ○ | |
| mpmath | 1.3.0 | ○ | |
| networkx | 3.5 | ○ | |
| numpy | 2.3.2 | ○ | Wheelからインストール成功 |
| pandas | 2.3.1 | × | コンパイルエラー |
| scikit-learn | 1.7.1 | × | |
| scipy | 1.15.3 | × | |
| shapely | 2.1.1 | × | |
| sortedcontainers | 2.4.0 | ○ | 競技プログラミング必須級 |
| sympy | 1.14.0 | ○ | |
| z3-solver | 4.15.1.0 | × | |

## 作業ログ
- 2026-02-27: 仮想環境を再作成 (.venv-pypy311)
- 2026-02-27: 主要なアルゴリズムパッケージのインストール完了。
- 2026-02-27: Windows SDK関連のパスが通っておらず、C拡張パッケージ (bitarray, pandas等) のインストールに失敗。

