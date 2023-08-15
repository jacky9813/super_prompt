################################
Super Prompt for Shell Interface
################################

Keep track of the current Git branch, Terraform workspace an so on with a fast,
easy and extensible way.

.. note::
    
    This program is in early stage of development and is subject to change.

    However, good ideas are always welcome. Use issue to give me some feedback.


System Requirements
===================

- Python 3.7+


Install
=======

This project has not been published to PyPI yet.

Thus, you can install by referencing this Git repo:

.. code-block:: shell

    pip3 install git+https://github.com/jacky9813/super_prompt
    # Install and enable plugins


Usage
=====

Open the shell resource file (for example: ``~/.bashrc``) and modify the ``PS1`` prompt variable like:

.. code-block:: shell

    # Original: PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]($(super-prompt run))\$ '
    # Added Part:                                                                                        ^^^^^^^^^^^^^^^^^^^^^

After restarting the shell or reload resource file with ``source ~/.bashrc``, we should get a prompt like:

.. code-block::

    user@my-workstation:~/super_prompt(🜉 master)$

Supported Plugins
=================

.. _Git Plugin: https://github.com/jacky9813/super_prompt_plugin_git
.. _Google Cloud SDK Plugin: https://github.com/jacky9813/super_prompt_plugin_gcloud
.. _Terraform Plugin: https://github.com/jacky9813/super_prompt_plugin_terraform

- `Git Plugin`_
- `Google Cloud SDK Plugin`_
- `Terraform Plugin`_

The plugin needs to be enable manually after installation:

.. code-block:: shell

    super-prompt config enable-plugin PLUGIN_NAME

You can also disable the plugin:

.. code-block:: shell

    super-prompt config disable-plugin PLUGIN_NAME

You can check installed plugins with command:

.. code-block:: shell
    
    super-prompt config list-plugins


Configuration
=============

The configuration is saved at ``~/.config/super-prompt.toml``.

Although you can edit it manually, the program also provides basic configuration Interface
for users not familiar with toml file.

For example:

.. code-block:: shell

    super-prompt config set core.context_color 31


Options
-------

.. _ANSI 3-bit color code: https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit

+--------------------+-------+--------------------------------------------------------------------+
| Option Name        | Type  | Description                                                        |
+====================+=======+====================================================================+
| core.context_color | color | The text color for showing current context. You can either use     |
|                    |       | `ANSI 3-bit color code`_ or RGB color if your terminal support it. |
|                    |       |                                                                    |
|                    |       | For example:                                                       |
|                    |       | - ``31`` means red foreground in ANSI.                             |
|                    |       | - ``[255, 0, 0]`` means red in RGB.                                |
+--------------------+-------+--------------------------------------------------------------------+
