# AtCoder oj+acc 環境 - クイックスタートガイド

このガイドでは、最も基本的な使い方を3ステップで説明します。

---

## 🚀 3ステップで始める

### ステップ1: 初回ログイン（最初の1回だけ）

```powershell
# atcoder-cliにログイン
acc login

# online-judge-toolsにログイン
oj login https://atcoder.jp/
```

### ステップ2: 問題をダウンロード

```powershell
# 例: ABC373をダウンロード
acc new abc373
```

### ステップ3: 解く → テスト → 提出

```powershell
# A問題のフォルダに移動
cd abc373/a

# コードを編集（VS Codeで開く）
code main.cpp

# コンパイル & テスト（C++の場合）
g++ main.cpp && oj t

# テストが通ったら提出
acc s
```

---

## 📝 Python（PyPy）で解く場合

```powershell
cd abc373/a
code main.py

# テスト（PyPyを使用）
oj t -c "..\..\\.venv-pypy310\Scripts\python.exe main.py"

# 提出
acc s main.py
```

---

## 🔄 テンプレートの切り替え

### Pythonをデフォルトに設定

```powershell
acc config default-template python
```

次回 `acc new` を実行すると、Pythonテンプレートが使われます。

### C++に戻す

```powershell
acc config default-template cpp
```

---

## 💡 便利なコマンド

```powershell
# 設定を確認
acc config

# 現在のデフォルトテンプレートを確認
acc config default-template

# ojのバージョン確認
oj --version

# accのバージョン確認
acc --version
```

---

## 📚 詳細はこちら

より詳しい情報は `docs/OJ_ACC_Setup.md` を参照してください。

---

Happy Competitive Programming! 🚀
