from setuptools import setup

VERSION = '0.1.0'

setup(
    name='nose-attribute',
    version=VERSION,
    author='Travis Pavek',
    auther_email='travis.pavek@gmail.com',
    keywords=['nose', 'attrib', 'attribute', 'select', 'exclude', 'tag'],
    url='https://github.com/travispavek/nose-attribute',
    download_url='https://github.com/travispavek/nose-attribute/tarball/%s' % VERSION,
    install_requires='nose',
    description='A better nose attrib plugin.',
    entry_points = {
        'nose.plugins': ['attribute = attribute:AttributeSelector'],
    },
)
