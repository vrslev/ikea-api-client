from setuptools import (  # pyright: reportMissingTypeStubs=false
    find_packages,
    setup,
)

from ikea_api import __version__ as VERSION

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="ikea_api",
    version=VERSION,
    description="IKEA Api Client",
    url="https://github.com/vrslev/ikea-api-client",
    author="vrslev",
    author_email="5225148+vrslev@users.noreply.github.com",
    license="MIT",
    packages=find_packages(),
    install_requires=install_requires,
)
