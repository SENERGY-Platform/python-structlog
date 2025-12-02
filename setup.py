import setuptools


def read_metadata(pkg_file):
    metadata = dict()
    with open(pkg_file, 'r') as init_file:
        for line in init_file.readlines():
            if line.startswith('__'):
                line = line.replace("'", '')
                line = line.replace('\n', '')
                key, value = line.split(' = ')
                metadata[key] = value
    return metadata


metadata = read_metadata('structlog/__init__.py')

setuptools.setup(
    name=metadata.get('__title__'),
    version=metadata.get('__version__'),
    author=metadata.get('__author__'),
    description=metadata.get('__description__'),
    license=metadata.get('__license__'),
    url=metadata.get('__url__'),
    copyright=metadata.get('__copyright__'),
    packages=setuptools.find_packages(exclude=("tests", "example")),
    python_requires='>=3.8,<4',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Natural Language :: English',
    ],
)
