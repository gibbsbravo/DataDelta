from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='datadelta',
    version='0.0.1',
    description='The best Python package for comparing two dataframes',
    packages=['datadelta'],
    package_dir={'datadelta': 'src/datadelta'},
    package_data={'datadelta': ['data/*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLV3)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy",
        "pandas",
        "jinja2",
    ],
    keywords=['python', 'dataops', 'devops', 'data', 'data analysis'],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    url="https://github.com/gibbsbravo/DataDelta",
    author="Andrew Gibbs-Bravo",
    author_email="andrewgbravo@gmail.com",
)
