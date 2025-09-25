# AtCoder ABC フォルダ生成ツール設定ファイル
# このファイルを編集して動作をカスタマイズできます

[General]
# デフォルトの言語設定 (cpp, python, both)
DefaultLanguage = "both"

# デフォルトでフォルダを開くかどうか
AutoOpenFolder = $false

# デフォルトでVS Codeを開くかどうか
OpenWithVSCode = $true

[Paths]
# テンプレートディレクトリ（相対パス）
TemplateDirectory = "template"

# 作成されるフォルダの命名規則
FolderNamePattern = "ABC{0}"

[Features]
# 追加で作成するファイル
CreateTestFiles = $true
CreateInputFiles = $true

# 問題の範囲 (A-D, A-E, A-F等)
ProblemRange = "A-D"

[URLs]
# AtCoderのベースURL
AtCoderBaseURL = "https://atcoder.jp/contests/abc{0}/tasks"

# 個別問題のURL形式
ProblemURLPattern = "https://atcoder.jp/contests/abc{0}/tasks/abc{0}_{1}"