from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

VERSION = "0.0.1"

setup(
    name = 'ryobigdopy',
    packages = ['my_python_package'],
    version = 'version number',  # Ideally should be same as your GitHub release tag varsion
    description = 'Library for communicating with Ryobi Garage Door Websocket and HTTP API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = 'Chris Wood',
    author_email = 'chris@chriswood.org',
    url = 'https://github.com/CJOWood/ryobigdopy',
    platforms='any',
    py_modules=['ryobigdopy'],
    install_requires=['websockets'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
    ],
)
