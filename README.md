## Installation
To install `webstore-deployer` from Avast Artifactory, run the following command:

```python -m pip install --extra-index-url https://artifactory.srv.int.avast.com/artifactory/api/pypi/pypi-local/simple webstore-deployer```

## Usage
General usage to get Chrome extension uploaded is:
* Run ```webstore-deploy init <CLIENT_ID>``` and follow instructions on screen, then
* Run ```webstore-deploy auth <CLIENT_ID> <CLIENT_SECRET> <CODE>``` with `<CODE>` returned from the previous step. Save the `refresh_token` returned.
* Run ```webstore-deploy upload [--filetype=crx|zip] <CLIENT_ID> <CLIENT_SECRET> <REFRESH_TOKEN> <APP_ID> <FILENAME>```

### In Docker
Ideally use our Avast lightweight Python image:
```
docker run --rm docker.int.avast.com/avast/python:3.5 /bin/bash -c '
   pip install --extra-index-url https://artifactory.srv.int.avast.com/artifactory/api/pypi/pypi-local/simple webstore-deployer;
   webstore-deploy <...>'
```

## Packaging
To package and upload to Avast Artifactory:
* Edit `$HOME/.pypirc` and add:

```
[distutils]
index-servers=
    avast

[avast]
repository: https://artifactory.srv.int.avast.com/artifactory/api/pypi/pypi-local
username = <username>
```
* `python setup.py sdist`
* `pip install twine` (if not present)
* `twine upload -r avast .\dist\<file>.zip`