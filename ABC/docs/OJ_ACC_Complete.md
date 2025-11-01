# 🎯 AtCoder oj+acc 環境構築 - 完了レポート

**作成日**: 2025年11月1日  
**参考**: [AtCoderのための環境作成: 自動テスト, コマンド提出 (oj, acc)](https://qiita.com/NaokiOsako/items/dcbc0a91e1bbca8ee45d)

---

## ✅ 実施内容

このワークスペースに、AtCoderの問題を効率的に解くための自動テスト・提出環境を構築しました。

### インストールしたツール

1. **atcoder-cli (acc) v2.2.0**
   - NPMでグローバルインストール
   - 問題のダウンロード、提出を自動化

2. **online-judge-tools (oj) v11.5.1**
   - 既にPyPy環境にインストール済み
   - サンプルケースでの自動テストを実行

### セットアップ内容

#### 1. accの設定ファイル作成

場所: `C:\Users\<YourUsername>\.config\atcoder-cli-nodejs\`

- **C++テンプレート**: `cpp/template.json` + `cpp/main.cpp`
- **Pythonテンプレート**: `python/template.json` + `python/main.py`

両方のテンプレートには、ワークスペースの `templates/` フォルダ内の高品質テンプレートを使用しています。

#### 2. デフォルト設定

```powershell
acc config default-task-choice all
```

コンテストの全問題を一括ダウンロードする設定を有効化しました。

#### 3. ドキュメント作成

以下のドキュメントを `docs/` フォルダに作成しました：

- **`OJ_ACC_Setup.md`**: 詳細なセットアップガイドと使い方
- **`OJ_ACC_QuickStart.md`**: 3ステップで始めるクイックガイド
- **`OJ_ACC_Verification.md`**: 動作確認手順

#### 4. 統合スクリプト

`acc-helper.ps1` を作成し、既存の `main.ps1` システムと連携できるようにしました。

---

## 🚀 使い方

### クイックスタート（3ステップ）

```powershell
# 1. ログイン（初回のみ）
.\acc-helper.ps1 login

# 2. 問題をダウンロード
.\acc-helper.ps1 download 373

# 3. テスト & 提出
.\acc-helper.ps1 test 373 a
.\acc-helper.ps1 submit 373 a
```

### 直接コマンドを使う場合

```powershell
# 問題をダウンロード
acc new abc373

# テスト実行
cd abc373/a
g++ main.cpp && oj t          # C++の場合
oj t -c "python main.py"      # Pythonの場合

# 提出
acc s main.cpp                # または main.py
```

---

## 📁 ディレクトリ構造

```
ABC/
├── main.ps1                           # 既存の統合システム
├── acc-helper.ps1                     # NEW: oj+acc統合ヘルパー
├── README.md                          # 更新: oj+acc情報を追加
├── docs/
│   ├── OJ_ACC_Setup.md               # NEW: 詳細ガイド
│   ├── OJ_ACC_QuickStart.md          # NEW: クイックスタート
│   └── OJ_ACC_Verification.md        # NEW: 動作確認手順
├── templates/
│   ├── main.cpp                       # C++テンプレート
│   └── main.py                        # Pythonテンプレート
└── .venv-pypy310/                    # PyPy環境（ojがインストール済み）
```

---

## 🎯 対応言語

### C++
- コンパイラ: g++ (MinGW-w64)
- テンプレート: 高品質な競プロテンプレート（DSU, BIT, セグ木など含む）

### Python (PyPy)
- 環境: PyPy 3.10 (`.venv-pypy310/`)
- テンプレート: 高品質な競プロテンプレート（DSU, BIT, ダイクストラなど含む）

---

## 📖 ドキュメント一覧

| ファイル | 内容 | 対象 |
|---------|------|------|
| `docs/OJ_ACC_Setup.md` | 詳細なセットアップガイド<br>コマンド一覧、トラブルシューティング | 全ユーザー |
| `docs/OJ_ACC_QuickStart.md` | 3ステップで始めるガイド | 初心者向け |
| `docs/OJ_ACC_Verification.md` | 動作確認手順 | セットアップ後の確認用 |

---

## 💡 既存システムとの統合

このワークスペースには、既に `main.ps1` による多機能統合システムが存在します。

### 両方のシステムの使い分け

| 機能 | 既存システム (`main.ps1`) | oj+acc |
|------|---------------------------|---------|
| フォルダ作成 | ✅ 独自形式 | ✅ AtCoder公式形式 |
| テスト実行 | ✅ ローカルテストケース | ✅ サンプルケース自動取得 |
| 提出 | ❌ ブラウザ手動 | ✅ コマンド一発 |
| VS Code統合 | ✅ 自動設定 | △ 手動で開く |

### 推奨ワークフロー

**パターン1: oj+accメイン**
```powershell
acc new abc373              # ダウンロード
cd abc373/a
code main.cpp               # 編集
g++ main.cpp && oj t        # テスト
acc s                       # 提出
```

**パターン2: 既存システムとの併用**
```powershell
acc new abc373              # ダウンロード（oj+acc）
.\main.ps1 open 373         # ブラウザで問題を開く（既存システム）
cd abc373/a
code main.cpp               # 編集
g++ main.cpp && oj t        # テスト（oj）
acc s                       # 提出（acc）
```

**パターン3: ヘルパースクリプト**
```powershell
.\acc-helper.ps1 download 373    # ダウンロード
.\acc-helper.ps1 test 373 a      # テスト
.\acc-helper.ps1 submit 373 a    # 提出
```

---

## 🔐 初回設定（必須）

初めて使う前に、必ず以下のコマンドでログインしてください：

```powershell
# 方法1: ヘルパースクリプト（推奨）
.\acc-helper.ps1 login

# 方法2: 個別にログイン
acc login
oj login https://atcoder.jp/
```

---

## 🎓 学習リソース

- **詳細ガイド**: `docs/OJ_ACC_Setup.md`
- **クイックスタート**: `docs/OJ_ACC_QuickStart.md`
- **動作確認**: `docs/OJ_ACC_Verification.md`
- **元記事**: https://qiita.com/NaokiOsako/items/dcbc0a91e1bbca8ee45d
- **acc公式**: https://github.com/Tatamo/atcoder-cli
- **oj公式**: https://github.com/online-judge-tools/oj

---

## 🚨 注意事項

1. **ログインが必須**: 初回は必ず `acc login` と `oj login` を実行してください
2. **Python環境**: PyPyを使う場合は `.venv-pypy310\Scripts\python.exe` を明示的に指定
3. **提出前の確認**: 必ずローカルでテストを実行してから提出してください
4. **テンプレート更新**: `templates/` フォルダのテンプレートを変更した場合は、accの設定フォルダにもコピーが必要

---

## ✅ 次のステップ

1. **動作確認**: `docs/OJ_ACC_Verification.md` に従って動作確認
2. **ログイン**: `.\acc-helper.ps1 login` でログイン
3. **実践**: 過去問（例: ABC373）で試す
4. **カスタマイズ**: 自分に合ったワークフローを確立

---

## 🎉 完了！

AtCoderの問題を効率的に解くための環境が整いました。

次のコンテストで、この環境を活用して素晴らしい成績を収めてください！

**Happy Competitive Programming! 🚀**

---

**作成者**: GitHub Copilot  
**更新日**: 2025年11月1日
