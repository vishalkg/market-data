#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="market-data",
    version="1.0.0",
    description="Enhanced Market Data MCP Server with Robinhood Options Integration",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastmcp",
        "aiohttp",
        "robin-stocks",
        "boto3",
        "cryptography",
    ],
    entry_points={
        "console_scripts": [
            "market-server=market_data.server:main",
        ],
    },
)
