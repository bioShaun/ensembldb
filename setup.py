#!/usr/bin/env python

from setuptools import setup, find_packages


version = '0.1dev'


msg = f'''------------------------------
Installing RNAseq version {version}
------------------------------
'''
print(msg)

setup(
    name='ensembldb',
    version=version,
    author='lx Gui',
    author_email='guilixuan@gmail.com',
    keywords=['bioinformatics', 'NGS', 'RNAseq'],
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/mrna'],
    install_requires=[],
)


msg = '''------------------------------
RNAseq installation complete!
------------------------------
'''
print(msg)