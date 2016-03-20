# flowtool-githooks

Some functionality to use granular git hooks.

The main idea is, that instead of running one single hook script
`flowtool-githooks` will manage and 'run' a directory instead.

To accomplish that, a shell script is installed as the hook.

Scripts inside the hooks directory, `.git/hooks/pre-commit.d`
and `.git/hooks/commit-msg.d` currently, are only executed, if
the are executable. This is used as a way of activating and
deactivating the scripts by the management command.

## Installation

Once you have `flowtool-githooks` and it's requirements installed,
you can run
```shell
flowtool githooks-config --install
```
from inside a git repository to install the hooks.
When they are installed, they can be configred interactively
by running
```shell
flowtool githooks-config
```
The gaphical status representation can be attained via
```shell
flowtool githooks-status
```

## More to come

This part of the project and documentation will definitely
be improved in the future.
