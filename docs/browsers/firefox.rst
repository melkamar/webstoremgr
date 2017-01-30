Mozilla Firefox
===============

.. _firefox-commands:

Command mode
------------

Operations for Mozilla Firefox are invoked as ``$ webstoremgr firefox <command>``. Parameters used in this section are:

    - ``id, secret``
        - API key and secret obtained from Mozilla. See `Access credentials`_ for details.

    - ``filename``
        - Filename of the extension file (.xpi) on your filesystem.

    - ``addon-id, version``
        - Extension ID and Version. Specified in the ``install.rdf`` manifest file as ``<em:id>``
          and ``<em:version>`` fields, respectively. For more information, refer to `Install Manifests`_.

The usecase for Firefox now only supports self-distributed extensions. Mozilla needs to sign such extensions,
which is what Webstore Manager offers.

Supported Firefox addon commands are:
    - ``gen-token``
        **Invocation:** ::

            webstoremgr firefox gen-token --id <id> --secret <secret>

        Generates a JSON Web Token from the given parameters. This token is used to authenticate for all secured
        methods. For further details, see `Mozilla API authentication`_.

    - ``upload``
        **Invocation:** ::

            webstoremgr firefox upload --id
                                       --secret
                                       --filename
                                       [--addon_id]
                                       [--version]

        Uploads the given extension to Mozilla store for signing. The signing is not done instantaneously, the client
        is responsible for downloading the file when ready.

        Both ``addon_id`` and ``version`` parameters are optional. If they are not set, their value will be parsed
        from the given extension file. If specified, they *must* be the same as the values in manifest file. If
        the values differ, the task will fail. This may be used as a safeguard that a correct version is being
        uploaded, but omitting them is generally recommended.

    - ``download``
        **Invocation:** ::

            webstoremgr firefox download --id
                                         --secret
                                         --addon_id
                                         --version
                                         [--interval]
                                         [--attempts]
                                         [--folder]
                                         [--target-name]

        Downloads an extension identified by ``addon_id`` and ``version`` from the Mozilla store if its
        processing (verification, signing) is successfully completed.

        If the processing is not yet completed, its download will be reattempted ``attempts`` times with ``interval``
        seconds between each attempt. Default values are 10 attempts in 30-second intervals.

        Downloaded file(s) are placed in the current working directory. To override this, set the ``--folder``
        argument.

        Optionally, if the extension entry consists of a single file (usual case), supply the ``--target-name``
        parameter to set the name of the downloaded file.

    - ``sign``
        **Invocation:** ::

            ``webstoremgr firefox sign --id
                                       --secret
                                       --filename
                                       --addon-id
                                       --version
                                       [--interval]
                                       [--attempts]
                                       [--folder]
                                       [--target-name]``

        Combines upload and download tasks into a single command. The parameters are directly related to the
        parameters of commands above, see them for explanation.


Script mode
-----------

Scripting mode is currently not supported for Firefox.

.. _Mozilla API authentication: http://addons-server.readthedocs.io/en/latest/topics/api/auth.html
.. _Access credentials: http://addons-server.readthedocs.io/en/latest/topics/api/auth.html#access-credentials
.. _Install Manifests: https://developer.mozilla.org/en-US/Add-ons/Install_Manifests