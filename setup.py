from setuptools import setup, find_packages

setup(
    name='karpentermig',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='A tool for Karpenter migration',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Pugar Jayanegara',
    license='MIT',
    install_requires=[
        'questionary',
        'boto3',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'karpentermig=karpentermig.cli:cli',
        ],
    },
)
