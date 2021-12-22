from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='datadelta',
    version='0.0.1',
    author="Andrew Gibbs-Bravo",
    author_email="andrewgbravo@gmail.com",
    description='The best Python package for comparing two dataframes',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLV3)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "pandas>=1.0.0",
        "numpy",
        "jinja2",
    ],
    keywords=['python', 'dataops', 'devops', 'data', 'data analysis'],
    extras_require={
        "dev": [
            "pytest",
            "check-manifest",
        ],
    },
    url="https://github.com/gibbsbravo/DataDelta",
    
)
