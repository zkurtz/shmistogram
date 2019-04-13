from setuptools import setup

exec(open("shmistogram/version.py").read())

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='shmistogram',
    version=__version__,
    author="Zach Kurtz",
    author_email="zkurtz@gmail.com",
    description="Piecewise-uniform univariate density estimation and visualization",
    url="https://github.com/zkurtz/shmistogram",
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=[
        'shmistogram',
        'shmistogram.binners',
        'shmistogram.plot',
        'shmistogram.simulations'
    ],
    install_requires=[
        'astropy',
        'matplotlib',
        'pandas',
        'numpy',
        'pytz',
        'scipy',
        'six',
    ]
)
