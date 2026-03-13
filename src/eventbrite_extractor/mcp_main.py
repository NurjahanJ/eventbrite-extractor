"""Entry point for the Eventbrite Extractor MCP server."""

from __future__ import annotations

from eventbrite_extractor.mcp_server import mcp


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
