
from setuptools import setup, find_packages

install_requires = [
        "python-dateutil>=2.6.0",
        "boto3",
        "PyYAML",
        "requests",
        "cryptography",
        "redis",
        "sqlalchemy",
        "six",
        "future",
        "psycopg2",
        "websocket",
        "websocket-client"
    ]

setup_requires = [
    ]

docs_require = [
        "sphinx",
        "sphinx-autobuild",
        "sphinxcontrib-httpdomain",
        "sphinx_rtd_theme",
        "recommonmark",
    ]

tests_require = [
    #    "mock",    # only for Python < 3.3
    ]

long_description = 'See GitHub README.rst for more details.'
with open('README.rst') as file:
   long_description = file.read()

setup(
        name="predix",
        version="1.0.0",
        author="Jayson DeLancey",
        author_email="jayson.delancey@ge.com",
        description="Python Client SDK for Predix Services",
        long_description=long_description,
        setup_requires=setup_requires,
        install_requires=install_requires,
        package_data={
            '': ['*.md', '*.rst'],
            },
        packages=find_packages(exclude=['test', 'test.*']),
        test_suite="test",
        tests_require=tests_require,
        entry_points={
            'console_scripts': [
                ]
        },
        keywords=['predix', 'ge', 'asset', 'analytics'],
        url="https://github.com/PredixDev/predixpy",
        classifiers=[
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6',
            'License :: OSI Approved :: BSD License',
            'Development Status :: 3 - Alpha']
    )
