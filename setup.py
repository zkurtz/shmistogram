from setuptools import setup

exec(open("shmistogram/version.py").read())

setup(
    name='shmistogram',
    version=__version__,
    packages=['shmistogram'],
    install_requires=[
        'pandas',
    ],
    license='See LICENSE.txt',
)
