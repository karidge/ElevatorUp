#!/usr/bin/env bash
# Some Build.sh scripts don't need to build anything.  This is applicable for
# some high level languages such as Python or Ruby.  In this case, we 
# want to (at most) make sure that SIM doesn't contain carriage returns
# from a Windoze box and that it is ready for execution with chmod.

dos2unix SIM
chmod +x SIM