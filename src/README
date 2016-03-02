flowtoolkit
===========

Some functionality to execute stuff here and there.

Development will continue
-------------------------

Thanks to my new employer (Zalando SE) i will be able to continue developing
this tool(-kit) as open source software. The first round of development is
scheduled to March 4th, so you can expect movement here soon.


what's in the box?
------------------

This library aims to ease the implementation of custom git flows.

For that purpose an extensible commandline-tool was created, as well as a libary to handle name prefixes and the like.
You can see how it is used in the included example, a simple git flow, that only has feature branches and a master branch.

Since a lot of code flows are part of a deployment strategy, object wrappers for remote hosts and directories are also included.

A flow can be implemented as a separate module, and used flexibly (like dry-running) if that module is made available to the tool.
Once available for import, the new module must be requested in the flow configuration (via the 'modules' section/key).
Shaping out that is part of the current development, as well as adding more to the object mapper classes (get/put/cmd interface for hosts, git branches/remotes, local/remote files, etc).

The flowtool
------------

The main user interface to this kit is it's command-line tool `ft.py`, which can easily be installed from the Python Package Index (pypi) like so:

    pip install flowlib

Once you install `flowlib` (as superuser, or as a user in a `virutalenv`), the tool should become available in your `PATH` enviroment.
Now you can run it by simply typing this into your terminal:

    ft.py

Also try these:

    ft.py -h
    ft.py -l
    ft.py -v
    ft.py -vv -v



Simple git flow
---------------

The simple git flow is the first example to look at, if you are considering to use this kit.
It is distributed with the the python package (`src/flib/flows/simple.cfg`).
To use it, specify it with the `-c` argument or copy it to `flow.cfg` in the directory
where you launch the tool or copy it to `flow.cfg` in any parent directory and use the `-r`
command line option.

