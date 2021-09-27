from setuptools import setup

if __name__ == "__main__":
    setup(
        name="ikea_api",
        install_requires=[
            "aiohttp==3.7.4",
            "pyppeteer==0.2.6",
            "requests==2.26.0",
            "typing-extensions==3.10.0.2",
        ],
        extras_require={
            "dev": [
                "black==21.8b0",
                "pre-commit==2.15.0",
            ]
        },
    )
