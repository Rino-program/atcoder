# Devcontainer: C++23 (GCC 15)

この `.devcontainer` 設定は、GCC 15 系（g++-15）を使った C++23 (gnu++23) 開発環境を提供します。

主な特徴:
- ベース: Ubuntu 24.04
- インストール: gcc-15 / g++-15（ubuntu-toolchain-r PPA 経由）
- 開発ツール: cmake, ninja, gdb, make, git
- 一部のライブラリ: libstdc++-15-dev, libboost-all-dev, libgmp-dev など（簡易的なセット）

注意事項 / 前提:
- Docker イメージ内で構築されます。ローカルで Docker または Dev Containers 機能が必要です。
- 正確に "GCC 15.2.0" のバイナリを厳密に保証するには、apt リポジトリのバージョン状況に依存します。
  必要であれば、特定の tarball をダウンロードしてインストールするよう Dockerfile を調整できます。
- 本リポジトリにある巨大な依存（ORTools, libtorch, SCIP 等）は全て含めていません。必要なライブラリがあれば追記します。

使い方（VS Code）:
1. VS Code でこのリポジトリを開く
2. コマンドパレットで「Dev Containers: Reopen in Container」を選択
3. コンテナが立ち上がったら、ターミナルで `g++ --version` や `g++ -std=gnu++23` でコンパイルを確認できます。

カスタマイズ:
- より多くのシステムライブラリが必要なら、`.devcontainer/Dockerfile` に apt パッケージを追記してください。
- リリースの厳密なバージョンが必要なら、GCC のソースや公式 tarball からビルドするよう Dockerfile を変更できます（ビルド時間は長くなります）。

小さな検証スクリプトは `post-create.sh` にあり、コンテナ作成後に実行されます。
