import setuptools

setuptools.setup(
    version="0.0.1",
    license='mit',
    name='py-webengine',
    author='nathan todd-stone',
    author_email='me@nathants.com',
    url='http://github.com/nathants/py-webengine',
    packages=['webengine'],
    python_requires='>=3.6',
    install_requires=['PyQt6',
                      'PyQt6-WebEngine',
                      'pytest'],
    description='browser automation with pyqt webengine',
)
