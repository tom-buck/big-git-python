from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 0.0.1 - Alpha",
    "Intended Audience :: No Audience",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Programming Language :: secret"] 
setup(
    name="big_git_python",
    version="0.0.1",
    description="A Python library for managing git repositories with a simple interface.",
    long_description=open("README.md").read() + "\n\n" + open("CHANGELOG.txt").read(),
    author="bing bong",
    author_email="bing.bong@example.com",
    packages=find_packages(where="src"),
    classifiers=classifiers,
    license="MIT",
    install_requires=['']
)