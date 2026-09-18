# 作業ログ

このプロジェクトで行った作業の記録。日付ごとに追記していく。

## 2026-09-18

### やったこと

1. **Microsoft Teamsのファイルを検索できるようにしたい、という相談**
   - 当初は「Teams APIをラップできるか」という相談から開始。
   - Teams(Microsoft Graph API)経由でチャネルの「ファイル」タブを検索する案を検討したが、
     Graph APIを使う以上、Azure ADへのアプリ登録+デバイスコードフローによる認証が
     どうしても必要になることが判明。
   - 対象ファイルがOneDriveにローカル同期されておらず、Teamsアプリ上でのみ編集・閲覧している
     とのことだったため、今回は認証を伴わない簡易な方法を採用することにした。
   - **決定**: Teamsからマニュアル等のファイルを手動でエクスポートし、`docs`フォルダに置いて
     ローカル検索する方式でまず実装する。Graph API連携は将来の拡張として`README.md`の
     「今後の予定」に記載。

2. **ローカルファイル検索ツールの実装**
   - `file_search.py` を新規作成。`docs`フォルダ配下のファイルを一覧・検索・全文取得する
     ロジックをまとめた(対応形式: `.docx` `.xlsx` `.pdf` `.txt` `.md`)。
   - `server.py` に3つのMCPツールを追加:
     - `list_docs(folder="")` — フォルダ内一覧
     - `search_docs(query, folder="", max_results=5)` — キーワード検索(前後の文章を抜粋)
     - `read_doc(file_path)` — 1ファイルの全文取得
   - `requirements.txt` に `python-docx` `openpyxl` `pypdf` を追加。
   - `Dockerfile` に `file_search.py` と `docs/` フォルダのコピーを追加。

3. **動作確認**
   - `docker build -t small-mcp-server .` でビルド成功を確認。
   - コンテナ内で `file_search` モジュールを直接実行し、`list_files` / `search_files` /
     `read_file` が正しく動くことを確認。
   - `docs`フォルダに実際に置かれていた自治体プロジェクトの資料
     (`厚木市_プロジェクト作業ガイド.docx` 等、11MB超のファイル)を使って、
     実データでの検索・全文取得も確認。
   - 標準入出力でJSON-RPCメッセージを直接やり取りし、MCPプロトコル越しに
     `tools/list` / `tools/call`(`search_docs`)が正しく応答することも確認。

4. **機密ファイルの取り扱い(重要)**
   - `docs`フォルダには自治体案件など機密性のある実データが置かれることが判明したため、
     `.gitignore` に `docs/*`(`docs/.gitkeep`は除く)を追加し、
     **公開(Public)のGitHubリポジトリに誤って上げないよう対処**した。
   - `git check-ignore` で実際に該当ファイルが除外されることを確認済み。

5. **README.md の更新**
   - 提供ツール一覧に `list_docs` / `search_docs` / `read_doc` を追加。
   - `docs`フォルダの使い方(Teamsからの手動エクスポート運用であること、
     `DOCS_DIR`環境変数で場所を変更できること)を追記。
   - Dockerボリュームマウント(`-v D:\riha\mcp\docs:/app/docs`)の説明を追加。
   - 「今後の予定」セクションを追加し、Teams(Graph API)認証付きツールの追加を
     将来的に検討している旨を明記。

6. **Claude Codeへの登録**
   - `claude mcp add` で `small-server` を登録。
     ```bash
     claude mcp add small-server -- docker run -i --rm -v D:/riha/mcp/docs:/app/docs small-mcp-server
     ```
   - 初回、パスをバックスラッシュ(`D:\riha\mcp\docs`)で指定したところ、
     bash側でエスケープされてパスが壊れる不具合が発生。
     スラッシュ区切り(`D:/riha/mcp/docs`)に直して解決。
   - `claude mcp list` で `small-server ✔ Connected` を確認。
   - **注意**: MCPサーバの登録は次回のClaude Code起動時から有効になる
     (登録した既存セッションには即時反映されない)。

7. **アーキテクチャの整理**
   - このMCPサーバー自体にはLLM/AIロジックは含まれておらず、`file_search.py`は
     単純な文字列一致検索を行う「ただのツール」であることを整理。
   - 自然言語での検索は、MCPクライアント側のLLM(今回の場合はClaude Code経由でClaude)が担っている:
     ユーザーの質問(自然文) → LLMが意図を解釈しツール呼び出し(`search_docs`等)に変換
     → MCPプロトコル経由でサーバーのツールを実行 → 検索結果(スニペット)をLLMに返却
     → LLMが結果を読んで自然言語の回答を組み立てる、という役割分担。
   - 将来Teams文書検索APIをMCPツールとして実装した場合も同じアーキテクチャが適用され、
     「質問 → LLM → MCP → Teams文書検索API → LLM(→回答)」という流れになる想定。
   - **具体的なフロー(プロトコル込み)**:
     ```
     Claude Codeから入力(自然言語の質問)
       → LLM(Claude)が意図を解釈しツール呼び出し(引数)を組み立てる
       → MCPプロトコル(JSON-RPC 2.0、標準入出力(stdio)経由)でMCPサーバに
         tools/callリクエストを送信
       → MCPサーバがtool呼び出しを受信・実行(search_docs等)
       → file_search.pyが文書検索(部分一致)
       → 検索結果をMCPプロトコル(JSON-RPC 2.0のレスポンス、content/structuredContent)
         で返却
       → LLM(Claude)が結果を読んで自然言語の回答を作成
       → Claude Codeの画面に表示
     ```
     このサーバーは`claude mcp add ... -- docker run -i --rm ...`で登録しており、
     `-i`(標準入力を開く)フラグの通り、通信はHTTP/SSEではなく標準入出力(stdio)上の
     JSON-RPCメッセージのやり取りで行われている(`WORKLOG.md`の動作確認項目3でも確認済み)。

### 現在の状態

- `small-mcp-server` イメージはビルド済み、`small-server` はClaude Codeに登録済み。
- 次回Claude Code起動後、`search_docs` 等のツールが使えるようになっているはず(要確認)。
- Claude Desktopにはまだ登録していない(希望があれば`README.md`の手順で追加可能)。

### 未着手・今後の課題

- Teams(Graph API)への認証付きアクセス(Azure ADアプリ登録+デバイスコードフロー)。
- `docs`フォルダ内ファイルの更新運用(手動エクスポートし直す必要がある)の仕組み化。
- `search_docs`の検索精度向上(`file_search.py`内の実装、現状は単純な部分一致検索)。
  - 軽量な改善: 全角/半角・大文字小文字の正規化、複数キーワードAND検索、
    日本語形態素解析(Janome/Sudachi等)による分かち書き、複数一致箇所のスコアリング表示。
  - RAG化: ドキュメントをチャンク分割して埋め込み(Embedding)し、ベクトル類似度検索する方式。
    同義語・言い換えにも対応できるが、埋め込みモデル呼び出しとベクトルインデックスの
    構築・更新運用が新たに必要になり、サーバーの依存関係が増える。
  - まずは軽量な改善から着手する方針で検討中。
  - **選択肢として、自前でRAGを実装するのではなく、Teams/Microsoft 365公式のMCPサーバーを
    使う案もある**。Microsoft Graphの検索基盤(Microsoft Search)は単純な部分一致ではなく、
    関連度ランキング・表記ゆれ吸収・意味的な検索の恩恵をすでに持っているため、自前でRAG
    (埋め込み・ベクトルインデックス)を構築しなくても精度向上が見込める。権限もログイン
    ユーザーの閲覧可能範囲に自動的にスコープされる。ただし認証(Azure ADアプリ登録+
    ユーザーごとのサインイン)は公式MCPサーバーを使っても不要にはならない。
