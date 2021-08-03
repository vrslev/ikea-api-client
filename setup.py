from setuptools import setup

# For Dependency Graph on GitHub
setup(
    name="ikea_api",
    install_requires=[
        "aiohttp",
        "brotli",
        "requests",
    ],
    extras_require={
        "driver": [
            "chromedriver_autoinstaller",
            "selenium",
        ]
    },
)
