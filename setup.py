
from setuptools import setup, find_packages

install_requires = [
        "python-dateutil",
        "PyYAML",
        "requests",
        "boto3",
        "cryptography",
        "redis",
        "websocket",
        "websocket-client"
    ]

setup_requires = [
    ]

long_description = 'See GitHub README.rst for more details.'
with open('README.rst') as file:
   long_description = file.read()

setup(
        name="predix",
        version="0.0.x3",
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
        entry_points={
            'console_scripts': [
                ]
        },
        tests_require=[],
        keywords=['predix', 'ge', 'asset', 'analytics'],
        url="https://github.com/PredixDev/predixpy",
        classifiers=[
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'License :: OSI Approved :: BSD License',
            'Development Status :: 3 - Alpha']
    )
