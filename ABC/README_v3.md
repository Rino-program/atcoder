# 🚀 AtCoder ABC フォルダテンプレート作成ツール v3.0

## 🌟 概要

AtCoder Beginner Contest (ABC) 参加用の高機能フォルダ自動生成システムです。
実際のコンテストでの使用を想定した多数の支援機能を備えています。

---

## ✨ 主要機能

### 🎯 **コンテスト支援機能（NEW！）**
- **タイマー機能**: リアルタイム残り時間表示
- **問題URL一括オープン**: 全問題を瞬時にブラウザで開く
- **提出前自動チェック**: TLE/MLE検出、テスト自動実行
- **進捗管理**: 各問題の状況を記録・表示

### 🧪 **高度なテスト機能**
- **複数テストケース対応**: 1つのファイルに複数のテストケース記述
- **自動テスト実行**: 期待値との比較、パス/フェイル判定
- **パフォーマンス測定**: 実行時間・メモリ使用量の詳細測定
- **TLE/MLE警告**: 制限時間・メモリ超過の自動検出

### 📊 **パフォーマンス監視**
- **リアルタイム測定**: C++/Python両対応の実行時間測定
- **メモリ使用量追跡**: Pythonの詳細メモリプロファイル
- **制限値チェック**: カスタマイズ可能な制限時間・メモリ設定

### 🔧 **開発効率化**
- **VS Code統合**: タスクランナー自動設定
- **クイック実行**: バッチファイルによる簡単テスト実行
- **言語選択**: C++のみ、Pythonのみ、両方から選択可能

---

## 📁 ファイル構成

### 基本構成
```
ABC372/
├── main.cpp              # C++テンプレート（パフォーマンス測定付き）
├── main.py               # Pythonテンプレート（メモリプロファイル付き）
├── README.md             # 詳細なコンテスト記録用ドキュメント
├── input_a.txt           # A問題複数テストケース
├── input_b.txt           # B問題複数テストケース
├── input_c.txt           # C問題複数テストケース
└── input_d.txt           # D問題複数テストケース
```

### コンテストモード追加ファイル
```
ABC372/
├── test_runner.ps1       # 高機能テストランナー
├── contest_helper.ps1    # コンテスト支援ツール
├── test.bat              # クイックテスト実行
├── contest.bat           # コンテスト支援GUI
└── contest_status.json   # 進捗管理データ（自動生成）
```

---

## 🚀 使用方法

### 基本的なフォルダ作成
```powershell
# 基本作成
.\create_abc_v2.ps1 372

# テストファイル付きで作成
.\create_abc_v2.ps1 372 -CreateTestFiles

# コンテスト支援機能付きで作成（推奨）
.\create_abc_v2.ps1 372 -CreateTestFiles -ContestMode

# VS Code統合・自動オープン
.\create_abc_v2.ps1 372 -VSCode -Open -CreateTestFiles -ContestMode
```

### パラメータ詳細

| パラメータ | 説明 | 例 |
|------------|------|-----|
| `ContestNumber` | コンテスト番号（必須） | `372` |
| `-Force` | 既存フォルダを強制上書き | `-Force` |
| `-Open` | エクスプローラーでフォルダを開く | `-Open` |
| `-VSCode` | VS Codeでフォルダを開く | `-VSCode` |
| `-CreateTestFiles` | テスト入力ファイルを作成 | `-CreateTestFiles` |
| `-Language` | 言語選択 (cpp/python/both) | `-Language cpp` |
| `-Date` | 開催日指定 (YYYY-MM-DD) | `-Date "2025-01-15"` |
| `-ContestMode` | 🎯 コンテスト支援機能ON | `-ContestMode` |

---

## 🎯 コンテスト支援機能の使い方

### 1. **コンテスト開始時**
```powershell
# 全問題URLを一括で開く
.\contest_helper.ps1 -Action OpenProblems -ContestNumber 372

# またはバッチファイルで
contest.bat open 372
```

### 2. **タイマー機能**
```powershell
# リアルタイム残り時間表示
.\contest_helper.ps1 -Action Timer

# またはバッチファイルで
contest.bat timer
```

### 3. **問題解答中**
```powershell
# A問題をPythonでクイックテスト
.\test_runner.ps1 -Problem a -Language python

# バッチファイルで
test.bat a python

# 制限時間・メモリをカスタマイズ
.\test_runner.ps1 -Problem c -Language cpp -TimeLimit 1000 -MemoryLimit 256
```

### 4. **提出前チェック**
```powershell
# 提出前の最終チェック
.\contest_helper.ps1 -Action Submit -Problem a -Language python

# バッチファイルで
contest.bat submit a python
```

### 5. **進捗管理**
```powershell
# 現在の状況を確認
.\contest_helper.ps1 -Action Status

# バッチファイルで
contest.bat status
```

---

## 🧪 テストケース記述方法

### 入力ファイル形式
```
# A問題テスト入力ファイル

## Test Case 1
5
1 2 3 4 5
## Expected:
15

## Test Case 2
3
10 20 30
## Expected:
60
```

### 特徴
- **複数テストケース**: `##` 区切りで無制限に追加可能
- **期待値自動比較**: `## Expected:` で期待される出力を指定
- **詳細エラー表示**: 失敗時に期待値と実際値を表示
- **パフォーマンス測定**: 各テストケースの実行時間・メモリ使用量を表示

---

## 📊 パフォーマンス測定機能

### C++テンプレート特徴
```cpp
int main() {
    PerformanceMonitor monitor;  // 自動測定開始
    
    // あなたのコード
    
    monitor.report();  // 結果出力（stderr）
    return 0;
}
```

### Pythonテンプレート特徴
```python
def main():
    tracemalloc.start()  # メモリ追跡開始
    start_time = time.perf_counter()
    
    result = solve()  # あなたのsolve関数
    
    # 自動的にパフォーマンス情報を出力
    # TLE/MLE警告も自動表示
```

### 出力例
```
[Performance] Time: 1250.45ms, Memory: 89.32MB
⚠️  TLE Warning: Execution time > 2000ms
```

---

## 🔧 カスタマイズ

### 制限時間・メモリの変更
```powershell
# C++で制限時間1秒、メモリ256MBでテスト
.\test_runner.ps1 -Problem a -Language cpp -TimeLimit 1000 -MemoryLimit 256
```

### テンプレートファイルのカスタマイズ
`template/` フォルダ内のファイルを編集することで、生成されるテンプレートを自由にカスタマイズできます。

### VS Code設定
自動生成される `.vscode/tasks.json` により以下のタスクが利用可能：
- **Build C++**: Ctrl+Shift+P → "Tasks: Run Task" → "Build C++"
- **Run C++**: C++ビルド後の自動実行
- **Run Python**: Python直接実行

---

## 🎯 コンテスト戦略での活用

### 開始直後（最初の5分）
1. `contest.bat open 372` で全問題を開く
2. `contest.bat timer` でタイマー開始
3. 各問題を読んで解く順番を決定

### 解答中
1. 問題を解く
2. `test.bat a python` で素早くテスト
3. パフォーマンスに問題がないかチェック
4. `contest.bat submit a python` で提出前最終チェック

### 終盤（残り30分）
1. タイマーで残り時間を常時確認
2. `contest.bat status` で解答状況をチェック
3. TLE/MLEが起きていないか再確認

---

## 🚨 よくある問題と対処法

### Q: 「実行ポリシー」エラーが出る
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: C++のコンパイルエラー
- AtCoder Libraryがインストールされているか確認
- g++がパスに通っているか確認
- 必要に応じて `main.cpp` のincludeパスを調整

### Q: Pythonでメモリ測定ができない
- Python 3.4以降が必要
- `tracemalloc` モジュールが利用可能か確認

### Q: テストケースが認識されない
- 入力ファイルで `##` の区切りが正しいか確認
- `## Expected:` の記述が正確か確認

### Q: VS Codeが開かない
- VS Codeがシステムの PATH に追加されているか確認
- コマンドラインから `code --version` が実行できるか確認

---

## 🔄 更新履歴

### v3.0 (2025-09-25)
- 🎯 コンテスト支援機能追加
- 🧪 複数テストケース対応
- 📊 高度なパフォーマンス測定
- ⏰ タイマー・進捗管理機能
- 🚀 大幅な使いやすさ向上

### v2.0 (2025-09-25)
- 🎨 視覚的UI改善
- ⚙️ 柔軟な言語選択
- 📅 日付設定機能
- 💪 エラーハンドリング強化

### v1.0
- 基本的なフォルダ作成機能

---

## 🤝 貢献・フィードバック

このツールをより良くするためのアイデアや改善提案があれば、ぜひお聞かせください！

### 今後の計画
- [ ] Web UI版の開発
- [ ] 他のコンテスト（ARC/AGC）対応
- [ ] 自動提出機能
- [ ] AI解法ヒント機能
- [ ] チーム戦対応

---

**🚀 バージョン**: 3.0.0  
**📅 更新日**: 2025年9月25日  
**👤 作成者**: GitHub Copilot  
**🎯 目標**: あなたのAtCoderライフを最高にする！

---

*このツールが皆さんのコンテスト成績向上に貢献できれば幸いです。頑張ってください！* 🎉