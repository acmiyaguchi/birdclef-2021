from distutils.core import setup

setup(
    name="simple-mp",
    version="1.0",
    description="An implementation of the SiMPle algorithm",
    author="Anthony Miyaguchi",
    author_email="acmiyaguchi@gmail.com",
    url="https://github.com/acmiyaguchi/birdclef-2021",
    packages=["simple_mp"],
    install_requires=[
        "numpy",
    ],
)
