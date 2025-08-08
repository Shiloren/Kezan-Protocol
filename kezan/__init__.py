"""Core package for the Kezan Protocol project.

This package bundles the modules that interact with the Blizzard API,
perform market analysis and expose helper utilities used throughout the
project.  Importing :mod:`kezan` provides access to these building blocks
without executing any side effects.

The package exposes no public functions by default but serves as a
namespace for submodules such as :mod:`kezan.analyzer` or
:mod:`kezan.logger`.
"""

# Keeping the file lightweight ensures that importing ``kezan`` is cheap
# and does not configure global state implicitly.
