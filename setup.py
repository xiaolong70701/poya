from setuptools import setup, find_packages

setup(
    name="Poya Products Info Scraper",
    version="0.1",
    author="Anthony Sung",
    author_email="xiaolong70701@gmail.com",
    description="A web scraper for Poya products",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiaolong70701/poya",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
        "pandas>=1.2.0",
        "selenium>=4.0.0",
        "tqdm>=4.60.0",
        "webdriver-manager>=3.5.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)