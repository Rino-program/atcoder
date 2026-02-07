# =============================================================================
# ReadmeGenerator.ps1 - README.md生成ライブラリ v4.0
# =============================================================================

. "$PSScriptRoot\Common.ps1"

# コンテストフォルダ用README生成（情報・メモ主体）
function New-ContestReadme {
    param(
        [string]$ContestName,
        [string]$FolderPath,
        [bool]$IsNumeric = $false
    )
    
    $dateString = Get-DateString
    $isABC = $IsNumeric -and ($ContestName -match '^\d{3}$')
    
    $readmeContent = @"
# $ContestName コンテスト情報・記録

**作成日時**: $dateString  
**システム**: AtCoder ABC 多機能統合システム v4.0

"@

    if ($isABC) {
        $readmeContent += @"
## � コンテストリンク

**メインページ**: [ABC$ContestName](https://atcoder.jp/contests/abc$ContestName/tasks)

### 個別問題
- **A問題**: [ABC${ContestName}_A](https://atcoder.jp/contests/abc$ContestName/tasks/abc${ContestName}_a)
- **B問題**: [ABC${ContestName}_B](https://atcoder.jp/contests/abc$ContestName/tasks/abc${ContestName}_b)
- **C問題**: [ABC${ContestName}_C](https://atcoder.jp/contests/abc$ContestName/tasks/abc${ContestName}_c)
- **D問題**: [ABC${ContestName}_D](https://atcoder.jp/contests/abc$ContestName/tasks/abc${ContestName}_d)

"@
    } else {
        $readmeContent += @"
## � 練習コンテスト

このフォルダは練習用です。

"@
    }

    $readmeContent += @"
## 📊 問題進捗

| 問題 | 状態 | 難易度 | 解法 | 実行時間 | 備考 |
|------|------|--------|------|----------|------|
| A | ⭕❌ | ★☆☆☆☆ | | ms | |
| B | ⭕❌ | ★★☆☆☆ | | ms | |
| C | ⭕❌ | ★★★☆☆ | | ms | |
| D | ⭕❌ | ★★★★☆ | | ms | |

## ⏱️ 時間記録

- **開始時刻**: ____:____
- **A問題**: ____:____ (____分)
- **B問題**: ____:____ (____分)  
- **C問題**: ____:____ (____分)
- **D問題**: ____:____ (____分)
- **終了時刻**: ____:____
- **合計時間**: ____分

## 💡 解法メモ・反省点

### A問題
\`\`\`
解法:

反省:

\`\`\`

### B問題  
\`\`\`
解法:

反省:

\`\`\`

### C問題
\`\`\`
解法:

反省:

\`\`\`

### D問題
\`\`\`
解法:

反省:

\`\`\`

## 🔍 学んだこと・Tips

\`\`\`
今回のコンテストで学んだアルゴリズムやテクニック:

次回への改善点:

\`\`\`

## 🗂️ ファイル構成

- **main.cpp** / **main.py** - 解答ファイル
- **in_*_*.txt** - テストケース（手動作成）
- **.vscode/** - VS Code設定

---
*AtCoder ABC 多機能統合システム v4.0*
"@

    try {
        $readmePath = Join-Path $FolderPath "README.md"
        $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
        return @{
            "Success" = $true
            "Path" = $readmePath
        }
    }
    catch {
        return @{
            "Success" = $false
            "Error" = $_.Exception.Message
        }
    }
}

# メインREADME生成（取説主体）
function New-MainReadme {
    param([string]$RootPath)
    
    $dateString = Get-DateString
    
    $mainReadmeContent = @"
# � AtCoder ABC 多機能統合システム v4.0 - 取扱説明書

**最終更新**: $dateString  
**開発**: GitHub Copilot

---

## 🚀 クイックスタートガイド

### 1. 新しいコンテストフォルダを作成
\`\`\`powershell
.\main.ps1 new 373                    # ABC373フォルダ作成
.\main.ps1 new 373 -VSCode -Browser   # + VS Code & ブラウザ起動
.\main.ps1 new JOI                    # 練習用フォルダ作成
\`\`\`

### 2. テスト実行（複数ケース・TLE判定付き）
\`\`\`powershell
.\main.ps1 test 373 a cpp             # ABC373のA問題をC++でテスト
.\main.ps1 test 373 b py              # ABC373のB問題をPythonでテスト
\`\`\`

### 3. ブラウザで問題を開く
\`\`\`powershell
.\main.ps1 open 373                   # ABC373の全問題をブラウザで開く
\`\`\`

---

## 📋 全コマンド一覧

| コマンド | 短縮形 | 説明 | 使用例 |
|----------|--------|------|--------|
| \`new\` | \`n\`, \`create\`, \`c\` | コンテストフォルダ作成 | \`.\main.ps1 n 373\` |
| \`test\` | \`t\`, \`run\`, \`r\` | テスト実行 | \`.\main.ps1 t 373 a cpp\` |
| \`open\` | \`o\`, \`browse\`, \`b\` | ブラウザ起動 | \`.\main.ps1 o 373\` |
| \`clean\` | \`cl\` | 一時ファイル削除 | \`.\main.ps1 clean\` |
| \`help\` | \`h\`, \`?\` | ヘルプ表示 | \`.\main.ps1 help\` |

---

## 🎯 主要機能

### ⚡ 複数テストケース対応
- \`in_a_1.txt\`, \`in_a_2.txt\` など複数のテストケースを自動実行
- 各ケースの実行時間測定
- **TLE判定機能**: 2秒を超えた場合に警告表示

### 🏗️ 自動環境構築
- 高品質C++/Pythonテンプレート
- VS Code設定自動生成（ビルド・デバッグ対応）
- テストケースファイル自動生成

### 📊 詳細記録機能
- 各コンテストフォルダに詳細README.md生成
- 問題進捗表、時間記録、解法メモ欄
- 反省点・学習内容記録欄

---

## 📁 フォルダ構成

### メインディレクトリ（このフォルダ）
\`\`\`
ABC/
├── main.ps1              # メインコマンド
├── README.md             # この取扱説明書
├── lib/                  # ライブラリ群
│   ├── Common.ps1        # 共通機能
│   ├── VSCodeConfig.ps1  # VS Code設定生成
│   ├── ReadmeGenerator.ps1 # README生成
│   └── RunBatGenerator.ps1 # 実行スクリプト生成
├── scripts/              # 個別機能
│   ├── New.ps1           # フォルダ作成
│   ├── Test.ps1          # テスト実行
│   ├── Open.ps1          # ブラウザ起動
│   └── Clean.ps1         # クリーンアップ
└── templates/            # テンプレートファイル
    ├── main.cpp          # C++テンプレート
    ├── main.py           # Pythonテンプレート
    └── in_*.txt          # 入力ファイルサンプル
\`\`\`

### 各コンテストフォルダ（自動生成）
\`\`\`
ABC373/
├── main.cpp              # C++解答ファイル
├── main.py               # Python解答ファイル
├── README.md             # コンテスト情報・記録用
├── in_a_1.txt            # A問題テストケース1
├── in_a_2.txt            # A問題テストケース2
├── in_b_1.txt ~ in_d_2.txt # B-D問題テストケース
└── .vscode/              # VS Code設定
    ├── tasks.json        # ビルド・実行タスク
    └── launch.json       # デバッグ設定
\`\`\`

---

## ⚙️ システム要件・初期設定

### 必要環境
- **OS**: Windows 10/11
- **PowerShell**: 5.1以上
- **C++コンパイラ**: g++（MinGW-w64推奨）
- **Python**: 3.6以上
- **VS Code**: 推奨エディタ

### 初期設定（1回のみ）
\`\`\`powershell
# PowerShell実行ポリシー設定
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 文字化け防止設定
chcp 65001
\`\`\`

---

## 🧪 テスト機能詳細

### 複数テストケース対応
各問題に対して複数のテストケースを準備できます：
\`\`\`
in_a_1.txt    # A問題 テストケース1
in_a_2.txt    # A問題 テストケース2
in_a_3.txt    # A問題 テストケース3 (必要に応じて追加)
\`\`\`

### TLE判定
- 実行時間2000ms（2秒）を基準にTLE判定
- 最も時間のかかったケースを基準に判定
- 結果サマリーで一覧表示

### 実行例
\`\`\`
� テスト結果サマリー
実行ケース数: 3
最大実行時間: 145ms
✅ TLE判定: OK (制限時間内)
成功: 3 ケース
\`\`\`

---

## �🚨 トラブルシューティング

### よくある問題
1. **実行ポリシーエラー**
   - 解決: \`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser\`

2. **コンパイルエラー**
   - MinGW-w64がインストールされているか確認
   - パス設定を確認

3. **文字化け**
   - \`chcp 65001\` を実行してUTF-8に設定

4. **VS Codeが起動しない**
   - VS Codeがインストールされているか確認
   - パス設定を確認

### サポート
- エラーが解決しない場合はGitHub Issuesで報告
- 機能追加要望も歓迎

---

## 📈 バージョン履歴

### v4.0 (現在) - 2025年9月26日
- 🎯 **機能重視設計**: 環境構築速度より多機能性を優先
- 🧪 **複数テストケース対応**: TLE判定機能付き
- 📊 **詳細記録機能**: コンテスト情報・反省記録
- 🧹 **クリーンアップ機能**: 一時ファイル自動削除
- 📁 **ディレクトリ整理**: メイン・コンテスト分離
- ⚡ **コマンド短縮**: 長い綴りを短縮形で対応

### v3.0 - 統合システム（廃止）
### v2.0 - 基本システム（廃止）

---

**🎯 設計思想**: 多機能性と使いやすさを両立  
**🏆 目標**: AtCoderでの学習・競技を最大限サポート  
**⚙️ アプローチ**: 品質重視、記録重視、学習促進

*Happy Competitive Programming! 🚀*
"@

    try {
        $readmePath = Join-Path $RootPath "README.md"
        $mainReadmeContent | Out-File -FilePath $readmePath -Encoding UTF8
        return @{
            "Success" = $true
            "Path" = $readmePath
        }
    }
    catch {
        return @{
            "Success" = $false
            "Error" = $_.Exception.Message
        }
    }
}