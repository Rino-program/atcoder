# AtCoder oj+acc 環境 - 動作確認手順

このドキュメントでは、セットアップした環境が正しく動作するかを確認する手順を説明します。

---

## ✅ 事前確認

以下のコマンドでツールがインストールされているか確認：

```powershell
acc --version    # 2.2.0 以上
oj --version     # 11.5.1 以上
g++ --version    # MinGW-w64 GCC
python --version # Python または PyPy
```

すべてバージョンが表示されればOKです。

---

## 🔐 ステップ1: ログイン設定（初回のみ）

### 方法1: ヘルパースクリプトを使用（推奨）

```powershell
.\acc-helper.ps1 login
```

### 方法2: 個別にログイン

```powershell
# atcoder-cliにログイン
acc login

# online-judge-toolsにログイン
oj login https://atcoder.jp/
```

**確認事項**:
- accログイン時、ユーザー名とパスワードを正しく入力
- ojログイン時、ブラウザが開いてAtCoderのログイン画面が表示される
- 両方とも "OK" や成功メッセージが表示される

---

## 📥 ステップ2: テストダウンロード

既に終了したコンテスト（例: ABC373）を使ってテストします。

```powershell
# ヘルパースクリプトを使用
.\acc-helper.ps1 download 373

# または直接accコマンドを使用
acc new abc373
```

**確認事項**:
- `abc373/` フォルダが作成される
- フォルダ内に `a`, `b`, `c`, `d`, `e`, `f` フォルダがある
- 各フォルダに `tests/` ディレクトリとサンプルファイル (`sample-1.in`, `sample-1.out` など) がある
- 各フォルダに `main.cpp` または `main.py` テンプレートがある

---

## 🧪 ステップ3: テスト実行

### C++でテスト

```powershell
cd abc373/a

# コードを簡単に編集（例: sample-1の入力に対応する出力を返すコード）
# main.cpp を開いて、適当なコードを書く

# コンパイル & テスト
g++ main.cpp
oj t

# ヘルパースクリプトを使う場合（ワークスペースルートから）
cd ../..
.\acc-helper.ps1 test 373 a
```

### Pythonでテスト

```powershell
cd abc373/a

# main.py を編集

# テスト (PyPyを使用)
oj t -c "..\..\\.venv-pypy310\Scripts\python.exe main.py"

# または通常のPython
oj t -c "python main.py"

# ヘルパースクリプトを使う場合（ワークスペースルートから）
cd ../..
.\acc-helper.ps1 test 373 a
```

**確認事項**:
- コンパイルまたは実行が成功する
- サンプルケースのテスト結果が表示される
- `[SUCCESS]` や `[PASSED]` などの成功メッセージが表示される

---

## 📤 ステップ4: 提出テスト（オプション）

**注意**: 実際に提出が行われるため、練習問題やすでに解いた問題で試すことをおすすめします。

```powershell
cd abc373/a

# 提出
acc s main.cpp
# または
acc s main.py

# ヘルパースクリプトを使う場合（ワークスペースルートから）
.\acc-helper.ps1 submit 373 a
```

**確認事項**:
- 提出確認メッセージが表示される（例: `Are you sure? Please type "abc373a"`）
- 問題IDを入力すると提出が実行される
- ブラウザで提出結果を確認できる

---

## 🔧 トラブルシューティング

### エラー: `acc: The term 'acc' is not recognized`

**原因**: npmのグローバルパスが通っていない

**解決策**:
1. PowerShellを再起動
2. それでも解決しない場合、npmのグローバルパスを確認:
   ```powershell
   npm config get prefix
   ```
3. 表示されたパスが環境変数PATHに含まれているか確認

### エラー: `oj t` で "No such file or directory: a.exe"

**原因**: コンパイルされた実行ファイルがない

**解決策**:
```powershell
# C++の場合、まずコンパイル
g++ main.cpp

# それからテスト
oj t
```

### エラー: `[ERROR] 'value'` (提出時)

**原因**: online-judge-toolsのバージョンが古い

**解決策**:
```powershell
pip uninstall online-judge-tools
pip install online-judge-tools
```

### テンプレートが反映されない

**原因**: `acc new` 実行後にテンプレートが更新された

**解決策**:
```powershell
# テンプレートを再コピー
Copy-Item -Path ".\templates\main.cpp" -Destination "$env:USERPROFILE\.config\atcoder-cli-nodejs\cpp\main.cpp"
Copy-Item -Path ".\templates\main.py" -Destination "$env:USERPROFILE\.config\atcoder-cli-nodejs\python\main.py"
```

---

## ✨ 動作確認完了！

すべてのステップが成功すれば、環境のセットアップは完了です。

次のステップ:
1. 実際のコンテストで使ってみる
2. `docs/OJ_ACC_Setup.md` で詳細な機能を確認
3. 自分なりのワークフローを確立する

---

Happy Competitive Programming! 🚀
