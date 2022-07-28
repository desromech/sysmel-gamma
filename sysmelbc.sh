#!/bin/sh

python3 bootstrap/interpreter/sysmelbi.py \
    module-sources/Compiler/Phase1-Untyped/CoreHierarchy.sysmel \
    module-sources/Compiler/Phase1-Untyped/Semantics.sysmel \
    module-sources/Compiler/Phase1-Untyped/Variable.sysmel \
    module-sources/Compiler/Phase1-Untyped/LocalVariable.sysmel \
    module-sources/Compiler/Phase1-Untyped/Macros.sysmel \
    module-sources/Compiler/Phase1-Untyped/MetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/LetMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/Tests.sysmel \
    module-sources/Compiler/Phase1-Untyped/Finish.sysmel \
    \
    module-sources/Compiler/Phase2-Typed/Tests.sysmel -- $@
