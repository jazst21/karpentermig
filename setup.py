from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='karpentermig',
    version='0.2.2',
    author='Pugar Jayanegara',
    author_email='p.jayanegara@gmail.com',
    description='A tool for Karpenter migration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/karpentermig',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        'karpentermig': ['schema/*.yaml'],
    },
    data_files=[
        ('karpentermig/schema', ['src/karpentermig/schema/nodePool-1-0-0.yaml',
                                 'src/karpentermig/schema/ec2NodeClass-1-0-0.yaml'])
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'karpentermig=karpentermig.generate_karpenter:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
