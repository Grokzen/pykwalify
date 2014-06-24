try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
    readme = f.read()
with open('ReleaseNotes.rst') as f:
    history = f.read()

setup(
    name="pykwalify",
    version="14.06.1",
    description='Python lib/cli for JSON/YAML schema validation',
    long_description=readme + '\n\n' + history,
    author="Grokzen",
    author_email="Grokzen@gmail.com",
    packages=['pykwalify'],
    scripts=['scripts/pykwalify'],
    install_requires=[
        'docopt==0.6.1',
        'PyYAML==3.11',
    ],
    classifiers=(
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    )
)
