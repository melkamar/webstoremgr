# Webstore Manager

This tool simplifies automated management of extensions for Chrome and Firefox. 

It is a semester project at Czech Technical University in MI-PYT, Advanced Python.

## Functions
### Chrome
* Unpack .crx archive and zip it (to prepare for uploading to Webstore)
* Authenticate (OAuth)
* Upload a new extension or update an existing one
* Publish an extension to testers or to public

### Firefox
* Authenticate
* Upload an extension
* Download a processed and signed extension for manual distribution

### Usage modes
* Command-line mode - all parameters specified on command-line, invoke one command at a time
* Scripting mode - commands may be passed to the tool as a script file
