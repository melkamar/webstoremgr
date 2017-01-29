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

.. _command-mode:

Command mode
------------
Commands are invoked on the command line, such as: ``webstoremgr chrome create arguments...``.

List of commands differs based on the target browser. See their respective sections for more details:

- :ref:`chrome-commands`

- :ref:`firefox-commands`

.. _script-mode:

Script mode
-----------

