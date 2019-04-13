from setuptools import setup

exec(open("shmistogram/version.py").read())

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='shmistogram',
    version=__version__,
    author="Zach Kurtz",
    author_email="zkurtz@gmail.com",
    description="Piecewise-uniform univariate density estimation and visualization",
    url="https://github.com/zkurtz/shmistogram",
    license='MIT',
    long_description=long_description,
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
        'scipy',
    ],
)
