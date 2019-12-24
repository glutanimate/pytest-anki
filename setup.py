from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="anki_testing",
    version="0.2.0",
    description="A small utility for testing Anki 2.1 addons",
    author="Michal Krassowski, Aristotelis P. (Glutanimate)",
    url="https://github.com/krassowski/anki_testing",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="anki development testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["pytest", "pytest-forked", "pytest-xvfb"]
)
