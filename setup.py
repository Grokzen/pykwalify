import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name="pykwalify",
    version="1.7.0",
    description='Python lib/cli for JSON/YAML schema validation',
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Johan Andersson",
    author_email="Grokzen@gmail.com",
    maintainer='Johan Andersson',
    maintainer_email='Grokzen@gmail.com',
    license='MIT',
    packages=['pykwalify'],
    url='http://github.com/grokzen/pykwalify',
    entry_points={
        'console_scripts': [
            'pykwalify = pykwalify.cli:cli_entrypoint',
        ],
    },
    install_requires=[
        'docopt>=0.6.2',
        'ruamel.yaml>=0.16.0',
        'python-dateutil>=2.8.0',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
