# AtCoder Contest Helper (local)

このリポジトリはローカルで AtCoder のコンテスト作業を支援する PowerShell スクリプト群です。

主な構成
- `main.ps1` : メインのエントリ。`new`, `test`, `open`, `fetch` などのコマンドを提供。
- `scripts/` : 実際の処理スクリプト（`New.ps1`, `Test.ps1`, `Fetch.ps1` など）。
- `templates/` : 問題テンプレート（`main.cpp`, `main.py` など）。
- `lib/` : 補助関数（VS Code 設定生成、README 生成等のヘルパ）。

前提
- Windows (PowerShell / pwsh) 環境
- Python 仮想環境（任意、`online-judge-tools` を使う場合は venv に入っていると簡単）
- `online-judge-tools` (`oj`) をインストール済み推奨
- `acc`（atcoder-cli / npm パッケージ）を使う場合は事前に npm でインストール済み

基本的なワークフロー
1. テンプレートからコンテストフォルダ作成
   ```powershell
   .\main.ps1 new 432 -VSCode -Fetch
   ```
   `-Fetch` を付けると `Fetch.ps1` が呼ばれてサンプルを `testcases/<Problem>/in_*.txt` に保存します。

2. サンプルのみダウンロード
   ```powershell
   .\scripts\Fetch.ps1 -ContestName 432 -Problem A:D
   ```

3. テスト実行（Python）
   ```powershell
   .\main.ps1 test 432 a py
   ```
   出力と期待出力の比較（PASS/FAIL）と実行時間が表示されます。

追加機能
- `Fetch.ps1` は `oj` を優先して使用し、無ければ `acc` にフォールバックします。
- 問題指定は `A`, `A,B,C`, `A-D`, `A:D` のように指定可能です。

トラブルシューティング
- `oj` の実行で `login` を求められた場合は、`
  `oj login https://atcoder.jp/`
  を実行してログインしてください（コンテスト期間中の非ログインアクセス制限のため）。

今後の改善案
- `Test.ps1` により厳密な差分表示（行別差分）を追加
- `acc` の環境差（コマンド名・引数）に合わせた最適化
- `lib/` の設定ジェネレータをより高機能にする

---
この README は自動生成の草案です。必要な追記やカスタマイズがあれば教えてください。
