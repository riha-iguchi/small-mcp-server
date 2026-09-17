# small-mcp-server

最小構成のMCP(Model Context Protocol)サーバです。Python製のFastMCPを使い、stdio経由でJSON-RPCを話します。`add`と`greet`という2つの簡単なツールを提供します。

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
| `requirements.txt` | 依存パッケージ(`mcp<2`) |
| `Dockerfile` | `python:3.12-slim`ベースのコンテナ定義 |

## 提供ツール

| ツール | 引数 | 戻り値 | 説明 |
| --- | --- | --- | --- |
| `add` | `a: int`, `b: int` | `int` | 2つの数を足す |
| `greet` | `name: str` | `str` | 名前を挨拶に変換する |

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

ブラウザが開き(開かなければ表示されたURLにアクセス)、左側のToolsに`add`と`greet`が並びます。値を入れて実行ボタンを押すと、コンテナ内のサーバが実際に応答するのが確認できます。

## Claude Desktopにつなげる

動作確認できたら、Claude Desktopの設定ファイル(`claude_desktop_config.json`)に以下を追加して再起動すると、Claudeから直接呼び出せるようになります。

```json
{
  "mcpServers": {
    "small-server": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "small-mcp-server"]
    }
  }
}
```

Dockerを使わない場合は、`command`を`python`、`args`を`["D:\\riha\\mcp\\server.py"]`のように絶対パスで指定します(仮想環境を使っているなら、その中のpythonの絶対パスを指定してください)。

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
