from mcp.server.fastmcp import FastMCP

mcp = FastMCP("small-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数を足す"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """名前を挨拶に変換する"""
    return f"こんにちは、{name}さん!"


if __name__ == "__main__":
    mcp.run()
