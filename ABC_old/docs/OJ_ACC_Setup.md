# AtCoder自動テスト・提出環境 (oj + acc) セットアップガイド

**作成日**: 2025年11月1日  
**参考記事**: [AtCoderのための環境作成: 自動テスト, コマンド提出 (oj, acc)](https://qiita.com/NaokiOsako/items/dcbc0a91e1bbca8ee45d)

---

## 📚 目次

1. [概要](#概要)
2. [インストール済みツール](#インストール済みツール)
3. [初回ログイン設定](#初回ログイン設定)
4. [基本的な使い方](#基本的な使い方)
5. [C++とPythonの切り替え](#c++とpythonの切り替え)
6. [コマンド一覧](#コマンド一覧)
7. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 概要

このワークスペースには、AtCoderの問題を効率的に解くための以下のツールがセットアップされています：

- **atcoder-cli (acc)**: 問題のサンプルテストケースをダウンロード、プログラムの提出を行うツール
- **online-judge-tools (oj)**: ダウンロードしたサンプルで自動テストを実行するツール

### 🚀 何ができるのか？

1. コマンド1つでコンテストの全問題とサンプルケースをダウンロード
2. ローカルでサンプルケースの自動テスト
3. コマンド1つで問題を提出

---

## ✅ インストール済みツール

このワークスペースには以下がすでにインストールされています：

```powershell
# 確認コマンド
acc --version    # atcoder-cli 2.2.0
oj --version     # online-judge-tools 11.5.1
```

### 言語環境

- **C++**: g++ (MinGW-w64)
- **Python**: PyPy 3.10 (`.venv-pypy310/` 仮想環境)

---

## 🔐 初回ログイン設定

初めて使う場合は、各ツールでAtCoderにログインする必要があります。

### 1. atcoder-cli (acc) にログイン

```powershell
acc login
```

実行すると、ユーザー名とパスワードの入力を求められます：

```
? username: あなたのAtCoderユーザー名
? password: [hidden] あなたのAtCoderパスワード
OK
```

### 2. online-judge-tools (oj) にログイン

```powershell
oj login https://atcoder.jp/
```

ブラウザが開くので、AtCoderにログインしてください。ログイン後、ターミナルに戻って確認メッセージが表示されます。

---

## 📖 基本的な使い方

### 1. 問題のダウンロード

コンテストの問題とサンプルケースを一括ダウンロード：

```powershell
acc new abc373
```

これにより、以下のような構造でフォルダが作成されます：

```
abc373/
├── contest.acc.json
├── a/
│   ├── main.cpp (または main.py)
│   └── tests/
│       ├── sample-1.in
│       ├── sample-1.out
│       ├── sample-2.in
│       └── sample-2.out
├── b/
├── c/
├── d/
├── e/
└── f/
```

### 2. コードの編集

ダウンロードした問題フォルダに移動してコードを編集：

```powershell
cd abc373/a
code main.cpp   # または main.py
```

### 3. テストの実行

#### C++の場合

```powershell
g++ main.cpp && oj t
```

- `g++ main.cpp`: コンパイルして `a.exe` を生成
- `oj t`: サンプルケースで自動テスト (`a.exe` または `a.out` を実行)

#### Pythonの場合

```powershell
oj t -c "python main.py"
```

または、PyPy環境を使用する場合：

```powershell
oj t -c "..\..\\.venv-pypy310\Scripts\python.exe main.py"
```

### 4. 問題の提出

テストが成功したら、以下のコマンドで提出：

```powershell
acc s
```

確認メッセージが表示されるので、問題名（例: `abc373a`）を入力して提出します。

### 5. 実行言語の指定

提出時に言語を指定する場合：

```powershell
acc s main.cpp     # C++ (GCC 13.2.0)
acc s main.py      # Python (CPython 3.11.4)
```

PyPyで提出する場合は、提出時にブラウザで言語を選択するか、以下のようにします：

```powershell
acc s main.py -- --language 5078  # PyPy3 (7.3.0)
```

言語IDは `acc submit --help` で確認できます。

---

## 🔄 C++とPythonの切り替え

デフォルトのテンプレートを切り替えることができます。

### C++をデフォルトに設定（現在の設定）

```powershell
acc config default-template cpp
```

### Pythonをデフォルトに設定

```powershell
acc config default-template python
```

---

## 📋 コマンド一覧

### atcoder-cli (acc) コマンド

| コマンド | 説明 | 使用例 |
|----------|------|--------|
| `acc new <contest>` | コンテストの全問題をダウンロード | `acc new abc373` |
| `acc add <problem_url>` | 特定の問題だけをダウンロード | `acc add https://atcoder.jp/contests/abc373/tasks/abc373_a` |
| `acc s [file]` | 問題を提出 | `acc s main.cpp` |
| `acc login` | AtCoderにログイン | `acc login` |
| `acc config` | 設定の確認・変更 | `acc config` |

### online-judge-tools (oj) コマンド

| コマンド | 説明 | 使用例 |
|----------|------|--------|
| `oj t` | サンプルケースで自動テスト | `oj t` |
| `oj t -c "<command>"` | 実行コマンドを指定してテスト | `oj t -c "python main.py"` |
| `oj d <url>` | 問題のサンプルケースをダウンロード | `oj d https://atcoder.jp/contests/abc373/tasks/abc373_a` |
| `oj s <url> <file>` | 問題を提出 | `oj s https://atcoder.jp/contests/abc373/tasks/abc373_a main.cpp` |
| `oj login <service>` | サービスにログイン | `oj login https://atcoder.jp/` |

---

## 🚀 実際の作業フロー例

### 例: ABC373 A問題をC++で解く

```powershell
# 1. 問題をダウンロード
acc new abc373

# 2. A問題のフォルダに移動
cd abc373/a

# 3. コードを編集
code main.cpp

# 4. コンパイル & テスト
g++ main.cpp && oj t

# 5. テストが通ったら提出
acc s
```

### 例: ABC373 B問題をPythonで解く

```powershell
# 1. B問題のフォルダに移動
cd abc373/b

# 2. コードを編集
code main.py

# 3. テスト (PyPyを使用)
oj t -c "..\..\\.venv-pypy310\Scripts\python.exe main.py"

# 4. テストが通ったら提出
acc s main.py
```

---

## ⚙️ 設定ファイルの場所

accの設定ファイルは以下の場所に保存されています：

```
C:\Users\<YourUsername>\.config\atcoder-cli-nodejs\
├── config.json                      # acc全体の設定
├── cpp/
│   ├── template.json               # C++の設定
│   └── main.cpp                    # C++テンプレート
└── python/
    ├── template.json               # Pythonの設定
    └── main.py                     # Pythonテンプレート
```

テンプレートファイルは、`.\templates\` フォルダ内のものと同期されています。

---

## 🚨 トラブルシューティング

### 1. `acc` コマンドが見つからない

**原因**: npmのグローバルインストールパスが通っていない

**解決策**:
```powershell
npm install -g atcoder-cli
```

再インストール後、PowerShellを再起動してください。

### 2. `oj t` でテストが失敗する

**原因**: コンパイル済みの実行ファイルがない、またはPythonのパスが間違っている

**解決策**:
- C++の場合: `g++ main.cpp` でコンパイルしてから `oj t` を実行
- Pythonの場合: `oj t -c "python main.py"` で実行コマンドを明示

### 3. `acc s` で提出時にエラー

**エラー例**:
```
[ERROR] 'value'
```

**原因**: online-judge-toolsのバージョンが古い

**解決策**:
```powershell
pip uninstall online-judge-tools
pip install online-judge-tools
```

### 4. PyPyで提出したい

**解決策**:

ブラウザで提出時に言語を選択するか、以下のように言語IDを指定：

```powershell
# PyPy3での提出（言語IDを指定）
acc s main.py -- --language 5078
```

言語IDは提出画面で確認できます。

### 5. テンプレートが反映されない

**原因**: `acc new` 実行後にテンプレートファイルが更新された

**解決策**:

設定ディレクトリのテンプレートを更新：

```powershell
# C++テンプレートを更新
Copy-Item -Path ".\templates\main.cpp" -Destination "$env:USERPROFILE\.config\atcoder-cli-nodejs\cpp\main.cpp"

# Pythonテンプレートを更新
Copy-Item -Path ".\templates\main.py" -Destination "$env:USERPROFILE\.config\atcoder-cli-nodejs\python\main.py"
```

---

## 🔗 参考リンク

- [atcoder-cli GitHub](https://github.com/Tatamo/atcoder-cli)
- [online-judge-tools GitHub](https://github.com/online-judge-tools/oj)
- [元記事 (Qiita)](https://qiita.com/NaokiOsako/items/dcbc0a91e1bbca8ee45d)
- [AtCoder公式サイト](https://atcoder.jp/)

---

## 📝 補足: このワークスペースの既存システムとの統合

このワークスペースには既に `main.ps1` による多機能統合システムが存在します。

### 既存システムとの併用

- **既存システム (`main.ps1`)**: ローカルでのテスト実行、フォルダ作成、VS Code統合に最適
- **oj + acc**: AtCoderからのサンプルダウンロード、自動提出に最適

### 推奨ワークフロー

1. `acc new abc373` でコンテストをダウンロード
2. `.\main.ps1 test 373 a cpp` で既存システムを使ってテスト
3. `acc s` で提出

または、ojを使った完全自動化も可能です：

1. `acc new abc373` でダウンロード
2. `cd abc373/a`
3. `g++ main.cpp && oj t` でテスト
4. `acc s` で提出

---

**🎯 これで、AtCoderの問題を効率的に解ける環境が整いました！**

Happy Competitive Programming! 🚀
