import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bbetter",
    version="0.0.1",
    author="C. Nakai McAddis",
    author_email="nakai.mcaddis@gmail.com",
    description="Command line interaction with BBLearn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cnakai/bbetter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        ("License :: OSI Approved :: GNU General Public License v3 or later"
         "(GPLv3+)"),
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",

    py_modules=['bbetter'],
    install_requires=[
        'Click',
        'splinter',
    ],
    packages=setuptools.find_packages(),
    entry_points="""
    [console_scripts]
    bbetter=bbetter.cli:cli
    """
)
