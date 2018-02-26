# Webstore Manager

[![Build Status](https://travis-ci.org/melkamar/webstoremgr.svg?branch=master)](https://travis-ci.org/melkamar/webstoremgr)
[![Documentation Status](https://readthedocs.org/projects/webstore-manager/badge/?version=latest)](http://webstore-manager.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/webstoremgr.svg)](https://badge.fury.io/py/webstoremgr)


This tool simplifies automated management of extensions for Chrome and Firefox. It provides a command line interface 
for performing most common tasks.

## Functions
### Chrome
* Authentication
* Creating a new extension entry (from crx or zip archive)
* Updating an existing extension
* Publishing extensions (public/trusted)

### Firefox
* Authentication
* Uploading an extension
* Downloading a processed and signed extension
    * _Useful when using a private CDN channel, as Firefox requires all extensions to be signed._


## Documentation
Detailed instructions can be found in the [documentation](http://webstore-manager.readthedocs.io/en/latest/?badge=latest).

### Usage Modes
* Command-line mode - all parameters specified on command-line, invoke one command at a time.
* Scripting mode - commands invoked in a batch - as a script file.

## Installation
Install `webstoremgr` from pypi: 

```python -m pip install webstoremgr```

### In Docker
I recommend using lightweight Alpine Linux Python3 image `frolvlad/alpine-python3`. Run using:
```
docker run -t --rm frolvlad/alpine-python3 /bin/sh -c '
    pip install pytest-runner
    pip install webstoremgr
    webstoremgr <commands>
'
```

Unfortunately, the lightweight image may have problems with downloading `pytest-runner` automatically as a dependency,
so it needs to be downloaded explicitly. I am not sure what causes this yet. Full-fledged images (`ubuntu` etc) don't 
have this problem.

## Building from source

To install from source, clone the repository and run `python setup.py install`. 

### Tests
Tests are written with `py.test`. To run them, use `python setup.py test`.

Alternatively, you may directly run pytest: `python -m pytest` in the root of the repository. In this case make sure you
have all testing dependencies installed.

##### Recording new Betamax cassettes
- To record new cassettes, delete existing `webstore_manager/tests/fixtures/cassettes/*`. Make sure that folder
`webstore_manager/tests/fixtures/cassettes` exists and is empty.

- Run tests with environment variables `refresh_token`, `client_secret`, `code`, `client_id`, `app_id`. You will need to 
get them by creating a Google account, API credentials, and running `init` command.

- `app_id` must point to an extension that is already uploaded and has language and region set.


### Documentation
Documentation lives in the `docs` folder. To build it, run `make html` or `make.bat html` on Linux or Windows, 
respectively.

# Uploading new version

- Bump version in `VERSION`
- Push a new git tag
- Travis will automatically deploy the new package
