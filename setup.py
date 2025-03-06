from setuptools import setup, find_packages

setup(
    name="match-predictor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'numpy',
        'pandas',
        'scikit-learn'
    ],
) 