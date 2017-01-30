Webstore Manager usage
======================

There are two basic modes of function:

- :ref:`command-mode`
    A single "target" of the manager is executed. Automatization involving multiple steps needs to be handled by
    an external script (i.e. bash).

- :ref:`script-mode`
    Targets of the manager tool are specified in a script file. This may involve several steps, variable assignment
    and more.

    The upside of this mode is no presence of sensitive information (auth details) in the terminal history, as all
    such information may be passed along using environment variables.


Installing Webstore Manager creates an executable script, `webstoremgr`. It serves as a shortcut, it is functionally
identical to running `python -m webstore_manager`. Through the documentation, `webstoremgr` is used.

Generic arguments
-----------------
The following arguments are applicable for all running modes:

- ``-v`` - **verbose**
    Increases the level of verbosity. By default only *warn* and more critical messages are logged. This parameter may
    be repeated (``-vv``) to achieve even more detailed output. See :ref:`logging` for details.


.. _logging:

Logging
-------
Logs are printed to standard output and to a file. The location is platform- and distribution-dependent.
    - **Windows**: ``%LOCALAPPDATA%\melkamar\webstore_manager\Logs\``
    - **Linux**: Depending on distribution. Examples:
        - ``/var/tmp/webstore_manager``
        - ``/user/.cache/webstore_manager/log``

You can find the log location by enabling the verbose output.


.. _command-mode:

Command mode
------------
Commands are invoked on the command line, such as: ``webstoremgr chrome create <arguments>``.

List of commands differs based on the target browser. See the platform-specific documentation
:doc:`here <browsers/index>`.

.. _script-mode:

Script mode
-----------

Webstore Manager's scripting mode consumes a single script file that defines its function. The general invocation
syntax is ::

    webstoremgr script <filename>

where ``filename`` is the script to execute.