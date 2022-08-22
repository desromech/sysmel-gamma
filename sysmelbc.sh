#!/bin/sh

python3 bootstrap/interpreter/sysmelbi.py \
    -sources module-sources/Compiler/Phase1-Untyped/Sources.lst \
    -sources module-sources/Compiler/Phase2-Typed/Sources.lst \
    -- $@
