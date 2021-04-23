from distutils.core import setup

setup(
    name="birdclef",
    version="1.0",
    description="Utilities for birdclef",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gmail.com",
    url="https://github.com/acmiyaguchi/birdclef-2021",
    packages=["birdclef"],
    install_requires=["numpy", "pandas", "matplotlib", "click", "pyarrow"],
)
