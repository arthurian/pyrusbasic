from setuptools import setup, find_packages

setup(
    name='pyrusbasic',
    version='0.1',
    packages=find_packages(),
    license='MIT',
    author='Arthur Barrett',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>3.5.2',
    install_requires=[
        'pygtrie>=2.3',
    ],
)
