Chrome and Webstore Manager
===========================

.. _chrome-commands:

Commands
--------

Operations for Chrome are invoked as ``$ webstoremgr chrome <command>``. Supported Chrome Webstore commands are:

    - ``init``
        Prints information for the user on how to begin authentication. Chrome webstore requires an OAuth
        authentication which requires opening of the provided link in a web browser whilst signed in to Google.

        Opening the provided link will prompt the user with a request for access to their webstore. Upon approving the
        request, a code is provided. This code may be used to generate a refresh token using the ``auth`` command.

        *Having access to the webstore is necessary for the function of this tool. It does not send any personal
        information anywhere.*

    - ``auth``



    - ``gen_token``


    - ``upload``


    - ``create``


    - ``publish``


    - ``repack``
