from setuptools import setup

exec(open("shmistogram/version.py").read())

setup(
    name='shmistogram',
    version=__version__,
    packages=['shmistogram'],
    license='See LICENSE.txt',
)
