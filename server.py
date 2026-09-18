from mcp.server.fastmcp import FastMCP

import file_search

mcp = FastMCP("small-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数を足す"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """名前を挨拶に変換する"""
    return f"こんにちは、{name}さん!"


@mcp.tool()
def list_docs(folder: str = "") -> list[dict[str, str]]:
    """docsフォルダ配下(folder指定時はそのサブフォルダ)のファイル・フォルダ一覧を取得する。"""
    return file_search.list_files(folder)


@mcp.tool()
def search_docs(query: str, folder: str = "", max_results: int = 5) -> list[dict[str, str]]:
    """docsフォルダ配下のファイル(Word/Excel/PDF/テキスト)を検索し、一致箇所を返す。"""
    return file_search.search_files(query, folder, max_results)


@mcp.tool()
def read_doc(file_path: str) -> str:
    """docsフォルダ内の指定したファイルの内容をテキストとして取得する。"""
    return file_search.read_file(file_path)


if __name__ == "__main__":
    mcp.run()
