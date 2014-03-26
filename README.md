flowtoolkit
===========

Some basic functionality to execute stuff here and there.

what's in the box?
------------------

This library aims to ease the implementation of custom git flows.

For that purpose a libary to manage name prefixes and the like is provided.
And since a lot of code flows are part of a deployment strategy, object wrappers for remote hosts and directories are also included.

A flow can be implemented as a separate module, and used flexibly (like dry-running) if that module is made available to the packaged commandline-tool, and requested in the flow configuration (via the 'module' section/key). Shaping out that is part of the current development, as well as adding more the object mapper classes (git branches/remotes, local/remote files, etc).

Check out the github repository for more related code, like the tests and the two (still raw) flow modules that already exist.
