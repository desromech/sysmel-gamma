#!/bin/sh

python3 bootstrap/interpreter/sysmelbi.py \
    -sources module-sources/Compiler/BootstrapUntypedPhase/Sources.lst \
    -sources module-sources/Compiler/SSA/Sources.lst \
    -sources module-sources/Compiler/Phase2-Typed/Sources.lst \
    -- $@
