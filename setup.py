from setuptools import setup


with open('README.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='naucse_render',
    version='1.3',
    description='Converts course material to naucse.python.cz API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='naucse.python.cz contributors',
    author_email='encukou@gmail.com',
    maintainer='Petr Viktorin',
    maintainer_email='encukou@gmail.com',
    license='MIT',
    url='https://github.com/pyvec/naucse_render',
    packages=['naucse_render'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    install_requires=[
        'ansi2html',
        'mistune',
        'nbconvert',
        'traitlets',
        'click',
        'PyYAML',
        'Jinja2',
        'Pygments>=2.3.1',
    ],
    extras_require={
        'dev': ['pytest'],
    },
    zip_safe=False,
)
