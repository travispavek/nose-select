from setuptools import setup

VERSION = 'v0.1.0'

setup(
    name='nose-attribute',
    version=VERSION,
    author='Travis Pavek',
    auther_email='travis.pavek@gmail.com',
    keywords=['nose', 'attrib', 'attribute', 'select', 'exclude', 'tag', 'collect'],
    packages=['attribute'],
    url='https://github.com/travispavek/nose-attribute',
    download_url='https://github.com/travispavek/nose-attribute/tarball/%s' % VERSION,
    install_requires='nose',
    description='A better nose attrib plugin.',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    entry_points = {
        'nose.plugins': ['attrselect = attribute.plugin:AttributeSelector',
                         'attrcollect = attribute.plugin:AttributeCollector'],
    },
)
