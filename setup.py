from setuptools import setup
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# Probably should be changed, __init__.py is no longer required for Python 3
for dirpath, dirnames, filenames in os.walk('perdu'):
    # Ignore dirnames that start with '.'
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


setup(
    name='perdu',
    version="0.1",
    packages=packages,
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license="BSD 3-clause",
    package_data={
        '': ['*.bz2'],
        'perdu': [
            'assets/css/*.css',
            'assets/templates/*.html',
            'assets/images/favicon.ico'
        ]
    },
    entry_points = {
        'console_scripts': [
            'perdu_webapp = perdu.bin.perdu_webapp:main',
        ]
    },
    install_requires=[
        'appdirs',
        'docopt',
        'whoosh',
        'flask',
    ],
    url="https://github.com/cmutel/perdu",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    description='Python library and webapp for searching standard industry and product classifiers',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
