from setuptools import setup

exec(open("shmistogram/version.py").read())

setup(
    name='shmistogram',
    version=__version__,
    packages=['shmistogram', 'shmistogram.det'],
    install_requires=[
        'pandas',
        'scipy'
    ],
    license='See LICENSE.txt',
)
