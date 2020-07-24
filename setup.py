import setuptools

setuptools.setup(
    version="0.0.1",
    license='mit',
    name='py-webkit',
    author='nathan todd-stone',
    author_email='me@nathants.com',
    url='http://github.com/nathants/py-webkit',
    packages=['webkit'],
    python_requires='>=3.6',
    install_requires=['PyQt5',
                      'PyQtWebEngine'],
    description='browser automation with pyqt webkit',
)
