from setuptools import setup

if __name__ == "__main__":
    setup(
        name="ikea_api",
        install_requires=[
            "aiohttp==3.7.4.post0",
            "requests==2.26.0",
            "typing-extensions==4.0.0",
        ],
        extras_require={
            "dev": [
                "black==21.9b0",
                "pre-commit==2.15.0",
            ]
        },
    )
