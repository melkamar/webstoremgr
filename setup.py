from setuptools import setup, find_packages

long_description = """Publish Chrome and Firefox extensions."""

version_file = open('VERSION')
ver = version_file.read().strip()
version_file.close()

setup(
    name='webstoremgr',
    version=ver,
    description=long_description,
    long_description=long_description,
    author='Martin Melka',
    author_email='melka@avast.com',
    license='MIT',
    keywords='extension, browser, chrome, firefox, store',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development'
    ],
    url='https://github.com/melkamar/webstoremgr',
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'webstoremgr = webstore_manager.manager:main'
        ]
    },
    install_requires=['click>=6', 'requests', 'appdirs', 'PyJWT'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax', 'flexmock']
)
