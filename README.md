# small-mcp-server

最小構成のMCP(Model Context Protocol)サーバです。Python製のFastMCPを使い、stdio経由でJSON-RPCを話します。`add`や`greet`などの簡単なツールに加え、`docs`フォルダに置いたファイル(Word/Excel/PDF/テキスト)を検索・閲覧するツールを提供します。

## 前提条件(Windows)

- Docker (Docker Desktopなど)
- PowerShell
- Node.js (npx.cmdを使うため)

## クイックスタート(Windows)

ビルド方法:

```powershell
docker build -t small-mcp-server .
```

サーバ起動方法(MCP Inspectorで確認):

```powershell
npx.cmd @modelcontextprotocol/inspector docker run -i --rm small-mcp-server
```

Windowsでは`npx`ではなく`npx.cmd`を使うと確実に起動できます。詳細は[MCP Inspectorで試す](#mcp-inspectorで試すおすすめ)を参照してください。

## 構成

| ファイル | 役割 |
| --- | --- |
| `server.py` | サーバ本体。`@mcp.tool()`でツールを定義しています |
| `file_search.py` | `docs`フォルダ配下のファイルを検索・読み取りするヘルパー |
| `docs/` | 検索対象のファイル(マニュアルなど)を置くフォルダ |
| `requirements.txt` | 依存パッケージ(`mcp`, `python-docx`, `openpyxl`, `pypdf`) |
| `Dockerfile` | `python:3.12-slim`ベースのコンテナ定義 |

## 提供ツール

| ツール | 引数 | 戻り値 | 説明 |
| --- | --- | --- | --- |
| `add` | `a: int`, `b: int` | `int` | 2つの数を足す |
| `greet` | `name: str` | `str` | 名前を挨拶に変換する |
| `list_docs` | `folder: str = ""` | ファイル一覧 | `docs`フォルダ(またはそのサブフォルダ)の中身を一覧表示する |
| `search_docs` | `query: str`, `folder: str = ""`, `max_results: int = 5` | 一致箇所の一覧 | `docs`フォルダ配下のWord/Excel/PDF/テキストファイルを再帰的に検索し、ヒットしたファイル名と前後の文章(スニペット)を返す |
| `read_doc` | `file_path: str` | `str` | 指定したファイルの全文をテキストとして取得する(検索結果だけでは足りない、手順を細かく読みたいときに使う) |

### `docs`フォルダの使い方

Microsoft Teamsのチャネル「ファイル」タブから、設定マニュアルなどのファイルをダウンロードして`docs`フォルダ(サブフォルダを作っても可)に置いてください。対応形式は`.docx` `.xlsx` `.pdf` `.txt` `.md`です。

Teams上のファイルが更新されたら、都度ダウンロードし直して`docs`フォルダ内のファイルを置き換えてください。認証は不要ですが、その代わりファイルの最新性は手動での更新に依存します。

`docs`フォルダの場所は環境変数`DOCS_DIR`で変更できます(デフォルトはカレントディレクトリの`docs`)。

## 今後の予定

- Microsoft Teams(Graph API)に認証してアクセスするツールの追加を予定。現状の`docs`検索ツールは手動エクスポート運用だが、将来的にはTeamsチャネルのファイルを直接検索できるようにする(Azure ADアプリ登録+デバイスコードフローによる認証が必要になる見込み)。

## 動かし方

### Dockerで動かす

```bash
docker build -t small-mcp-server .
```

単体での起動確認(任意):

```bash
docker run -i --rm small-mcp-server
```

何も表示されずカーソルが止まって見えますが、これはstdioでJSON-RPCの入力を待っている正常な状態です。Ctrl+Cで終了してください。

`docs`フォルダにファイルを追加するたびに再ビルドしたくない場合は、ホスト側のフォルダをボリュームとしてマウントしてください。

```powershell
docker run -i --rm -v D:\riha\mcp\docs:/app/docs small-mcp-server
```

### Dockerを使わずに動かす

Python 3.12以降があれば、そのまま実行できます。

```bash
python -m venv .venv
.venv\Scripts\activate        # macOS / Linux は source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

## MCP Inspectorで試す(おすすめ)

Node.jsが入っていれば、次の1行でGUIの検証ツールが立ち上がります。

```bash
npx.cmd @modelcontextprotocol/inspector docker run -i --rm small-mcp-server
```

(Windows以外では`npx.cmd`の代わりに`npx`を使ってください)

ブラウザが開き(開かなければ表示されたURLにアクセス)、左側のToolsに`add`や`greet`、`search_docs`などが並びます。値を入れて実行ボタンを押すと、コンテナ内のサーバが実際に応答するのが確認できます。`docs`フォルダの中身を検証したい場合は、上記のボリュームマウント付きのコマンドを使ってください。

## Claude Desktopにつなげる

動作確認できたら、Claude Desktopの設定ファイル(`claude_desktop_config.json`)に以下を追加して再起動すると、Claudeから直接呼び出せるようになります。

```json
{
  "mcpServers": {
    "small-server": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "D:\\riha\\mcp\\docs:/app/docs",
        "small-mcp-server"
      ]
    }
  }
}
```

Dockerを使わない場合は、`command`を`python`、`args`を`["D:\\riha\\mcp\\server.py"]`のように絶対パスで指定します(仮想環境を使っているなら、その中のpythonの絶対パスを指定してください)。この場合`docs`フォルダはプロジェクト直下のものがそのまま使われます。

## Claude Codeにつなげる

```bash
claude mcp add small-server -- docker run -i --rm small-mcp-server
```

## ツールを増やすには

`server.py`に`@mcp.tool()`デコレータを付けた関数を追加するだけです。docstringがツールの説明、型ヒントが引数スキーマになります。

```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """2つの数を掛ける"""
    return a * b
```

Inspector側にも自動で反映されます。Dockerで動かしている場合は`docker build`をやり直してください。
