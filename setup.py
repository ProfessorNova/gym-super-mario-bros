"""The setup script for installing the package."""
from setuptools import setup, find_packages


# read the contents of the README
with open('README.md') as README_md:
    README = README_md.read()


setup(
    name='gym_super_mario_bros',
    version='7.4.0',
    description='Super Mario Bros. for Gymnasium',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords=' '.join([
        'Gymnasium',
        'Reinforcement-Learning',
        'NES',
        'Super-Mario-Bros',
        'Lost-Levels',
    ]),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Free For Educational Use',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.10',
    url='https://github.com/Kautenja/gym-super-mario-bros',
    author='Christian Kauten',
    author_email='kautencreations@gmail.com',
    license='Proprietary',
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    package_data={'gym_super_mario_bros': ['_roms/*.nes']},
    install_requires=[
        'gymnasium>=0.26.0',
    ],
    entry_points={
        'console_scripts': [
            'gym_super_mario_bros = gym_super_mario_bros._app.cli:main',
        ],
    },
)
