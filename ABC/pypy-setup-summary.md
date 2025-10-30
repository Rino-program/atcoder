# PyPy 3.10 (v7.3.12) 環境セットアップ結果まとめ

作成日: 2025-10-30

## 概要
このファイルはワークスペース内で行った PyPy 3.10 (pypy3.10-v7.3.12) 環境構築の結果をまとめたものです。成功・失敗した項目、原因、次の推奨アクションを記載しています。

## 環境（場所）
- PyPy 本体: `./.pypy/pypy3.10-v7.3.12-win64/`
- PyPy 仮想環境: `./.venv-pypy310/`（Windows 用に `.venv-pypy310\Scripts\python.exe` が存在）
- VS Code ワークスペース設定: `./.vscode/settings.json` は `.venv-pypy310\Scripts\python.exe` を指す
- 依存ピンファイル: `./requirements-pypy.txt` を作成済

## 完了したこと
- PyPy 本体のダウンロードと展開（`.pypy/pypy3.10-v7.3.12-win64`）
- PyPy を使った仮想環境作成（`.venv-pypy310`）
- VS Code のワークスペース設定で PyPy 仮想環境を指定
- 一部パッケージのインストール成功（下記参照）
- 依存リスト `requirements-pypy.txt` の作成
- インポート検証スクリプトの実行（結果記録、下記参照）

## インポート検証結果（実際に import を試したパッケージ）
- 成功して import できたもの:
  - networkx==3.0
  - sympy==1.11.1
  - sortedcontainers==2.4.0
  - more-itertools==9.0.0
  - PuLP==2.7.0
  - mpmath==1.2.1
  - z3-solver==4.12.1.0
  - ac-library-python は pip 上は存在（インストール済の可能性あり）だが import 名の判別で `aclibrary` 等を試した結果、import に失敗

- 失敗（インストール・ビルドで問題が発生、または import 失敗）:
  - numpy==1.24.1 — Windows PyPy で wheel が見つからずソースからのビルドが要求され、ビルドに MSVC / Fortran / BLAS 等のネイティブツールが必要で失敗
  - scipy==1.10.1 — Meson + Fortran (gfortran) / BLAS/LAPACK 等が必要でメタデータ生成/ビルド失敗
  - pandas==1.5.2 — numpy 未整備のため失敗
  - scikit-learn==1.3.0 — C/C++/Fortran 等のネイティブ依存でビルド失敗
  - shapely==2.0.0 — C 拡張・numpy 等の依存でビルドに失敗
  - bitarray==2.6.2 — wheel がなく、Windows では MSVC が必要でビルド失敗
  - cppyy==2.4.1（cppyy-backend のビルドで MSVC が必要、失敗）
  - ac-library-python — import 名が環境により異なり、今回は import に失敗

## 失敗の主な原因
- Windows + PyPy の組み合わせでは、多くの「数値計算系」「C/C++/Fortran 拡張」を含むパッケージに対して PyPy 用の公式ホイールが提供されていないことが多い。
- そのため pip はソースからビルドしようとし、MSVC（Visual C++ Build Tools）や gfortran、OpenBLAS などのネイティブビルドツールとライブラリが必要となる。
- Windows上でこれらを揃えるのは手間が大きく、AtCoder/競プロの用途ではオーバーヘッドが高い。

## 推奨アクション（選択肢）
1. 最も現実的 — CPython と PyPy を併用
   - 数値系（numpy/scipy/pandas/scikit-learn/shapely/cppyy など）は CPython（通常の CPython 3.10/3.11 仮想環境）で管理・利用する。
   - PyPy は純 Python 実装や特定の高速化が見込める処理だけに使う。
   - リポジトリに CPython 用の仮想環境（例: `.venv-cpython310`）を作り、`requirements-pypy.txt` と別に `requirements-cpython.txt` を作成して分離するのが簡単で再現性が高い。

2. WSL / Linux 上で PyPy を使う
   - Linux では PyPy 向けのホイールやビルドツール（gfortran, openblas など）が揃いやすく、成功率が高い。
   - WSL(Ubuntu) に PyPy をインストールして同じ手順を試すのが現実的。

3. Windows にフルビルド環境を導入して強引に解決
   - Visual Studio Build Tools、gfortran（MinGW-w64（fortran）やIntel Fortranなど）、OpenBLAS 等をインストールすればビルド可能になる場合があるが、設定と時間が大きく必要。

## 再現・検証手順（簡易）
1. PyPy 仮想環境を有効化（PowerShell）:

```powershell
& ".\.venv-pypy310\Scripts\Activate.ps1"
```

2. 依存をインストール（すでに実行済）:

```powershell
python -m pip install -r .\requirements-pypy.txt --prefer-binary
```

3. 簡易インポート検証（例）:

```powershell
python -c "import numpy, scipy, pandas, networkx; print('ok')"
```

> 注: 上記は Windows PyPy 環境では多くが失敗する可能性があります。エラーは Visual C++ や gfortran、BLAS/LAPACK 等の不足によるものが多いです。

## 参考・備考
- 今回の作業で `requirements-pypy.txt` をリポジトリルートに保存しました。これは PyPy 用の希望リストで、Windows 環境で全てのパッケージがインストールできることを保証するものではありません。
- 競プロ用途であれば "必要なら CPython を併用する" 方針がメンテナンスコストと実用性の点で最もバランスが良いです。

---

必要なら、このファイルを `README.md` にリンクする、あるいは CPython 用仮想環境を作成して `requirements-cpython.txt` を追加する作業を続けます。どちらを希望しますか？
