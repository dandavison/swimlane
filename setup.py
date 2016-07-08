import os

from setuptools import find_packages
from setuptools import setup


setup(
    name='swimlane',
    version=(open(os.path.join(os.path.dirname(__file__),
                               'swimlane',
                               'version.txt'))
             .read().strip()),
    author='Dan Davison',
    author_email='dandavison7@gmail.com',
    description="Define swimlane diagrams in JSON",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'svgwrite',
    ],
    entry_points={
        'console_scripts': [
            'swimlane = swimlane.swimlane:main',
        ],
    },
)
