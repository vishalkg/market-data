#!/usr/bin/env python3

import logging
import os
import sys
from pathlib import Path

# Lazy imports - only import when needed

# Setup enhanced logging
log_file = os.path.join(os.path.dirname(__file__), "..", "market-data.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a"),  # Append mode
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 60)
logger.info("Starting Enhanced Market Data MCP Server...")
logger.info(f"Log file: {log_file}")
logger.info("=" * 60)


def create_server():
    """Create and configure the MCP server with all tools"""

    logger.info("🚀 Initializing MCP server...")

    # Lazy imports
    from fastmcp import FastMCP

    from .providers.market_client import MultiProviderClient
    from .tools.options_tools import register_options_tools
    from .tools.stock_tools import register_stock_tools
    from .tools.technical_tools import register_technical_tools

    # Initialize MCP server and multi-provider client
    mcp = FastMCP("Finance Data Server")
    logger.info("✅ FastMCP server created")

    logger.info("🔧 Initializing multi-provider client...")
    multi_client = MultiProviderClient()
    logger.info("✅ Multi-provider client initialized")

    # Register all tool modules
    logger.info("📋 Registering stock tools...")
    register_stock_tools(mcp, multi_client)
    logger.info("✅ Stock tools registered")

    logger.info("📋 Registering options tools...")
    register_options_tools(mcp, multi_client)
    logger.info("✅ Options tools registered")

    logger.info("📋 Registering technical tools...")
    register_technical_tools(mcp, multi_client)
    logger.info("✅ Technical tools registered")

    logger.info("🎉 Enhanced Finance Data MCP Server configured successfully")
    logger.info("🌐 Server ready to accept connections")
    return mcp


# Create the server instance only when needed
mcp = None


def get_server():
    """Get or create the server instance"""
    global mcp
    if mcp is None:
        mcp = create_server()
    return mcp


def main():
    """Main entry point"""
    logger.info("🎯 Starting main server process...")
    logger.info("📡 Running MCP server in stdio mode")

    # Get server instance
    server = get_server()

    logger.info("🚀 Launching MCP server via stdio...")
    logger.info("✅ MCP Server is READY and accepting connections")

    # Flush logs to ensure they're written immediately
    import sys

    sys.stderr.flush()

    server.run()


if __name__ == "__main__":
    import time

    start_time = time.time()
    logger.info(f"⏱️  Server startup initiated at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    main()

    elapsed = time.time() - start_time
    logger.info(f"⏱️  Total startup time: {elapsed:.2f} seconds")
