from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Itemizer",
    version="0.1",
    author="Jose Vargas",
    author_email="josedvq@gmail.com",
    description="Preprocessing prose text for generation of itemset and feature datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/josedvq/itemizer.git",
    packages=setuptools.find_packages()
)
