Google Chrome
=============

.. _chrome-commands:

Commands
--------

Operations for Chrome are invoked as ``$ webstoremgr chrome <command>``. Parameters used in this section are:

    - ``client_id``, ``client_secret``
        - Your client API id obtained in the Google Developers Console. Refer to `using webstore`_.

    - ``code``
        - One-time code used to generate a refresh token. Obtained through the ``init`` command.

    - ``refresh_token``
        - Reusable token which is used for generating access tokens. It is obtained through the ``auth`` command.

    - ``app_id``
        - ID of an extension as listed in the Dashboard. Click on More Info next to the extension to find out.
          Its format is e.g. ``abcdefghijklmnopqrstuvwxyzabcdef``.

    - ``filename``
        - Name of an extension file (.zip, .crx) on your filesystem.

    - ``target``
        - Audience for publishing. Two accepted values: ``public`` and ``trusted``.


Supported Chrome Webstore commands are:

    - ``init``
        **Invocation:** ``webstoremgr chrome init <client_id>``

        Prints information for the user on how to begin authentication. Chrome webstore requires an OAuth
        authentication which requires opening of the provided link in a web browser whilst signed in to Google.

        Opening the provided link will prompt the user with a request for access to their webstore. Upon approving the
        request, a code is provided. This code may be used to generate a refresh token using the ``auth`` command.

        *Having access to the webstore is necessary for the function of this tool. It does not send any personal
        information anywhere.*

    - ``auth``
        **Invocation:** ``webstoremgr chrome auth <client_id> <client_secret> <code>``

        Exchanges your one-time code for a reusable ``refresh token`` which can be later used for authentication.

        These three parameters should be stored securely, as they grant automated access to your webstore identity.


    - ``gen-token``
        **Invocation:** ``webstoremgr chrome gen-token <client_id> <client_secret> <refresh_token>``

        Use refresh token to generate an access token. The access token has a limited lifespan (1 hour).

    - ``create``
        **Invocation:** ``webstoremgr chrome create [-t,--filetype] <client_id> <client_secret> <refresh_token> <filename>``

        Optional parameter ``-t`` or ``--filetype`` specifies what type of archive the given file is.
        Accepted values are ``crx`` (default) or ``zip``.

        Create (upload) a new extension to the webstore. It will not be published.

        It will be assigned a new ``app_id``, this will be printed on the standard output.

    - ``upload``
        **Invocation:** ``webstoremgr chrome upload [-t,--filetype] <client_id> <client_secret> <refresh_token> <app_id> <filename>``

        Optional parameter ``-t`` or ``--filetype`` specifies what type of archive the given file is.
        Accepted values are ``crx`` (default) or ``zip``.

        Upload a new version of an existing extension to the webstore. It will not be published.


    - ``publish``
        **Invocation:** ``webstoremgr chrome publish --target <target> <client_id> <client_secret> <refresh_token> <app_id>``

        Parameter target specifies the audience of users to publish to. Accepted values are ``public`` or ``trusted``.

        Publish an extension to a given audience.


    - ``repack``
        **Invocation:** ``webstoremgr chrome repack <filename>``

        Transform a crx archive into a zip.

        crx archive is obtained through Chrome developer tools (pack an extension). When uploading to the Webstore,
        zip is needed.

        *This tool accepts both zip and crx for uploading tasks. This is a convenience method if used in combination
        with other tools.*



Script mode
-----------
    Script mode for Chrome offers all functions of the command line tool. Heading of each list item is an example of
    how to call the given function in a script. The given parameters correspond to command mode parameters, see
    section above for details.

    - ``chrome.init client_id client_secret refresh_token``
        Initialize the Chrome store. Saves the given parameters as a global state which is used in subsequent steps.

        **You must call this function before any others that require authentication.**

    - ``chrome.setapp app_id``
        Set the app_id parameter for future method calls.


    - ``chrome.new filename``
        Create a new extension from the archive pointed to by ``filename``. Calling this function will set the
        internal ``app_id`` variable.

        Only accepts ZIP archives. To upload a CRX, you need to run ``chrome.unpack`` and ``zip`` functions.
        See :ref:`generic-functions`.


    - ``chrome.update filename``
        Update an existing extension. Its ID must be set by calling ``chrome.setapp`` first. Details are identical to
        ``chrome.new`` function.

    - ``chrome.publish target``
        Publish an extension to the given target (``public`` or ``trusted``).

        Its ID must be set by calling ``chrome.setapp`` first.


    - ``chrome.check_version expected_version timeout``
        Assertion function to check if the published version is the same as expected.

        The currently published app is compared to the ``expected_version`` parameter. If they are not equal,
        the comparison is repeated after several seconds until the ``timeout`` duration expires. If they are still
        not equal, script terminates with a nonzero exit code.


    - ``chrome.unpack archive target_dir``
        Unpack a CRX file to the given target directory.



.. _using webstore: https://developer.chrome.com/webstore/using_webstore_api#beforeyoubegin