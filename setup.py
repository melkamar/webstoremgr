from setuptools import setup, find_packages

long_description = """Publish browser extensions to their stores.
Currently only available for Google Chrome."""

setup(
    name='webstore_deployer',
    version='0.3.1',
    description='Publish browser extensions to their stores.',
    long_description=long_description,
    author='Martin Melka',
    author_email='melka@avast.com',
    license='MIT',
    keywords='extension, browser, chrome, store',
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
    url='<not available yet>',
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'webstore-deploy = webstore_deployer.deployer:main'
        ]
    },
    install_requires=['click>=6', 'requests', 'appdirs'],
    tests_require=['pytest']
)
