#!/bin/sh

python3 bootstrap/interpreter/sysmelbi.py \
    module-sources/Compiler/Phase1-Untyped/CoreHierarchy.sysmel \
    module-sources/Compiler/Phase1-Untyped/CoreSemantics.sysmel \
    module-sources/Compiler/Phase1-Untyped/SemanticAnalysisMapping.sysmel \
    module-sources/Compiler/Phase1-Untyped/TypeChecking.sysmel \
    module-sources/Compiler/Phase1-Untyped/TypeInference.sysmel \
    module-sources/Compiler/Phase1-Untyped/Symbol.sysmel \
    module-sources/Compiler/Phase1-Untyped/Environment.sysmel \
    module-sources/Compiler/Phase1-Untyped/MacroInvocationContext.sysmel \
    module-sources/Compiler/Phase1-Untyped/ASTAnalyzer.sysmel \
    module-sources/Compiler/Phase1-Untyped/ControlFlowNodes.sysmel \
    module-sources/Compiler/Phase1-Untyped/BasicConversionNodes.sysmel \
    module-sources/Compiler/Phase1-Untyped/ProgramEntity.sysmel \
    module-sources/Compiler/Phase1-Untyped/Namespace.sysmel \
    module-sources/Compiler/Phase1-Untyped/Variable.sysmel \
    module-sources/Compiler/Phase1-Untyped/ArgumentVariable.sysmel \
    module-sources/Compiler/Phase1-Untyped/BlockClosure.sysmel \
    module-sources/Compiler/Phase1-Untyped/LocalVariable.sysmel \
    module-sources/Compiler/Phase1-Untyped/TypeDefinition.sysmel \
    module-sources/Compiler/Phase1-Untyped/StructureDefinition.sysmel \
    module-sources/Compiler/Phase1-Untyped/Macros.sysmel \
    module-sources/Compiler/Phase1-Untyped/MetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/FlagMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/LetMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/NamespaceMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/TypeDefinitionMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/StructureDefinitionMetaBuilder.sysmel \
    module-sources/Compiler/Phase1-Untyped/ParseTreeMapping.sysmel \
    module-sources/Compiler/Phase1-Untyped/Tests.sysmel \
    module-sources/Compiler/Phase1-Untyped/Finish.sysmel \
    \
    module-sources/Compiler/Phase2-Typed/Tests.sysmel -- $@
