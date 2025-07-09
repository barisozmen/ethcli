from setuptools import setup, find_packages

setup(
    name='ethcli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'web3',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'eth=ethcli.cli:ethcli',
        ],
    },
    author='Baris Ozmen',
    author_email='', # Please provide if you want to include
    description='A comprehensive command-line interface for interacting with the Ethereum blockchain',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/barisozmen/ethcli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Assuming MIT, please confirm
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
