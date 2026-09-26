# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Python SDK for RetiQo infrastructure
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python SDK for RetiQo infrastructure"

setup(
    name='retiqo',
    version='0.1.0',
    description='Python SDK for RetiQo, the state layer for enterprise AI agent workflows',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Loreum Digital Inc',
    author_email='info@loreum.io',
    url='https://github.com/retiqoai/retiqo_sdk',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    python_requires='>=3.8',
    install_requires=[
        'websockets>=11.0',
        'aiohttp>=3.9.0',
        'cryptography>=41.0.0',
        'pycryptodome>=3.19.0',
        'pydantic>=2.0.0',
        'asyncio-throttle>=1.0.2',
        'eth-keys>=0.4.0',  # For ECDSA signature recovery
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'mypy>=1.5.0',
            'ruff>=0.1.0',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='rti retiqo infrastructure state channels distributed systems ai agents',
    project_urls={
        'Documentation': 'https://github.com/retiqoai/retiqo_sdk#readme',
        'Source': 'https://github.com/retiqoai/retiqo_sdk',
        'Tracker': 'https://github.com/retiqoai/retiqo_sdk/issues',
    },
)

