from distutils.core import setup


with open('requirements.txt', 'r') as handle:
    required = handle.read().splitlines()

setup(
    name="PyVaporation",
    packages=["PyVaporation"],
    version="0.1.0",
    license="Apache license 2.0",
    description="Set of tools for modelling membrane pervaporations",
    author="Denis Sapegin, Aleksei Chekmachev",
    author_email="a.checkmachev@gmail.com",
    url="https://github.com/Membrizard/PyVaporation",
    download_url="https://github.com/Membrizard/PyVaporation/archive/refs/tags/v0.1.0.tar.gz",
    keywords=[
        "pervaporation",
        "membrane",
        "chemistry",
        "modelling",
    ],
    install_requires=required,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: Apache license 2.0",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)