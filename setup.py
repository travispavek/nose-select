from setuptools import setup

VERSION = 'v0.1.3'

setup(
    name='nose-tags',
    version=VERSION,
    author='Travis Pavek',
    author_email='travis.pavek@gmail.com',
    keywords=['nose', 'attrib', 'attribute', 'select', 'exclude', 'tag', 'collect'],
    packages=['tag'],
    url='https://github.com/travispavek/nose-tags',
    download_url='https://github.com/travispavek/nose-tags/tarball/%s' % VERSION,
    install_requires='nose',
    description='A better nose attrib plugin.',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    entry_points = {
        'nose.plugins': ['tagselector = tag.plugin:TagSelector',
                         'tagcollector = tag.plugin:TagCollector'],
    },
)
