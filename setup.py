
from setuptools import setup, find_packages

install_requires = [
        "python-dateutil",
        "PyYAML",
        "requests",
        "websocket"
    ]

setup_requires = [
        "coverage",
        "flake8",
        "nose",
        "pylint",
        "tox"
    ]

setup(
        name="predix",
        version="0.0.5",
        author="Jayson DeLancey",
        author_email="jayson.delancey@ge.com",
        description="Python Client SDK for Predix Services",
        setup_requires=setup_requires,
        install_requires=install_requires,
        package_data={},
        packages=find_packages(exclude=['test', 'test.*']),
        test_suite="test",
        entry_points={
            'console_scripts': [
                ]
        },
        tests_require=['tox'],
        keywords=['predix', 'ge', 'time', 'asset', 'analytics'],
        url="https://github.com/predixpy/predixpy",
        classifiers=[
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.7',
            'License :: Other/Proprietary License',
            'Development Status :: 3 - Alpha']
    )
