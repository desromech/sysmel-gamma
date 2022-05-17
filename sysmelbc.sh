#!/bin/sh

python3 bootstrap/interpreter/sysmelbi.py \
    module-sources/Compiler/BootstrapEnvironment/Phase1-Untyped.sysmel \
    module-sources/Compiler/BootstrapEnvironment/Phase2-Typed.sysmel -- $@
