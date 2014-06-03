try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = dict()

settings.update(
    name="pykwalify",
    version="0.1.2",
    description='Python lib/cli for JSON/YAML schema validation',
    long_description='Python lib/cli for JSON/YAML schema validation',
    author="Grokzen",
    author_email="Grokzen@gmail.com",
    packages=['pykwalify'],
    scripts=['scripts/pykwalify'],
    install_requires=[
        'docopt==0.6.0',
        'PyYAML==3.10',
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

setup(**settings)
