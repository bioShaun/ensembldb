#!/usr/bin/env python

from setuptools import setup, find_packages


version = '0.1dev'


msg = '''------------------------------
Installing ensembldb version {}
------------------------------
'''.format(version)
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
    scripts=['scripts/ensembldb',
             'scripts/ensembldb_genome_dl',
             'scripts/ensembldb_metatable'],
    install_requires=[
        'click',
        'luigi',
        'pyyaml',
        'envoy',
        'pandas',
        'fire',
        'gtfparse',
        'aioftp'
    ],
)


msg = '''------------------------------
ensembldb installation complete!
------------------------------
'''
print(msg)
