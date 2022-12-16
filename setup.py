from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.0.4"

setup(
    name="tmdb",
    version=VERSION,
    description="A Commander APP for TMDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="tmdb commander",
    author="RhythmLian",
    url="https://github.com/Rhythmicc/tmdb",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["Qpro", "QuickStart_Rhy"],
    entry_points={
        "console_scripts": [
            "tmdb = tmdb.main:main",
        ]
    },
)
