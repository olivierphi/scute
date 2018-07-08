"""
Scute
-----
Scute is a Python version of the excellent PHP small Dependency Injection Container.

The code is merely a port of Pimple 1.1 (easier to implement), with the exception that services are shared by default
(as in last versions of Pimple)

````````````
Save in a hello.py:
.. code:: python
    from scute import Container

    container = Container()

    container['param'] = 'world'
    container['service_one'] = lambda cont: 'hello ' + cont['param']
    container.extend('service_one', lambda hi, cont: hi+'!')
    container['scuter'] = container.protect(lambda input_text: input_text.replace('WORLD', 'SCUTE'))

    def upper_cased(cont: Container):
        hello_text = cont['service_one']
        return hello_text.upper()

    container['upper_cased'] = upper_cased

    if __name__ == '__main__':
        upper_cased_content = container['upper_cased']
        scuter = container['scuter']
        print(scuter(upper_cased_content))

`````````````````
And run it:
.. code:: bash
    $ pip install scutes
    $ python hello.py
prints 'HELLO SCUTE!'
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scute',

    version='1.0.2',


    description='A small Dependency Injection Container, ported from PHP\'s Pimple',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/DrBenton/scute',

    author='Olivier Philippon',
    author_email='olivier@rougemine.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Dependency injection',

    packages=['scute'],
    package_dir={'scute': 'scute'},

    install_requires=[],
    python_requires='>=3.6',

    extras_require={
        'dev': [],
        'test': ['pytest', 'pylint'],
    },

    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
)
