from parser import parseString
from types import MethodType
from typesystem import *

class IdentifierLookupScope(BehaviorTypedObject):
    def __init__(self, parentScope):
        super().__init__()
        self.parentScope = parentScope

    def lookupSymbol(self, symbol):
        return None

    def lookupSymbolRecursively(self, symbol):
        result = self.lookupSymbol(symbol)
        if result is not None:
            return result
        elif self.parentScope is not None:
            return self.parentScope.lookupSymbolRecursively(symbol)
        else:
            return None

    def makeChildLexicalScope(self):
        return LexicalScope(self)

class LexicalScope(IdentifierLookupScope):
    def __init__(self, parentScope):
        super().__init__(parentScope)
        self.symbolTable = {}

    def setSymbolBinding(self, symbol, value):
        self.symbolTable[symbol] = value

    def lookupSymbol(self, symbol):
        return self.symbolTable.get(symbol, None)

class NamespaceLevelEnvironment(LexicalScope):
    def __init__(self, parentScope = None):
        super().__init__(parentScope)

    def setSymbolBinding(self, symbol, value):
        super().setSymbolBinding(symbol, value)
        value.onGlobalBindingWithSymbolAdded(symbol)

    def performWithArguments(self, machine, selector, arguments):
        if len(arguments) == 0:
            boundSymbol = self.lookupSymbol(selector)
            if boundSymbol is not None:
                return boundSymbol.getSymbolBindingReferenceValue()
        return super().performWithArguments(machine, selector, arguments)

class ScriptEvaluationEnvironment(LexicalScope):
    def __init__(self, parentScope):
        super().__init__(parentScope)

    def evaluateScriptFile(self, evaluationMachine, scriptFile, scriptFilename, scriptDirectory):
        self.setSymbolBinding(Symbol('__CurrentScriptFilename__'), String(scriptFilename))
        self.setSymbolBinding(Symbol('__CurrentScriptDirectory__'), String(scriptDirectory))
        scriptSource = scriptFile.read()
        parseTree = parseString(scriptSource, scriptFilename)
        return parseTree.evaluateWithEnvironment(evaluationMachine, self)

class BootstrapCompiler(BehaviorTypedObject):
    def __init__(self):
        super().__init__()
        self.topLevelEnvironment = NamespaceLevelEnvironment()
        self.topLevelEnvironment.setSymbolBinding('__BootstrapCompiler__', self)
        self.topLevelEnvironment.setSymbolBinding('__TypeBuilder__', TypeBuilder())
        self.basicTypeEnvironment = {}
        self.isTypeSystemEnabled = False
        self.enterTopLevelNamespace()

    def makeScriptEvaluationEnvironment(self):
        return ScriptEvaluationEnvironment(self.topLevelEnvironment)

    @classmethod
    def initializeBehaviorType(cls, type):
        BehaviorTypedObject.initializeBehaviorType(type)
        type.addPrimitiveMethodsWithSelectors([
            (cls.addBasicTypeNamedWith, 'addBasicTypeNamed:with:'),
            (cls.addBindingNamedWith, 'addBindingNamed:with:'),
            (cls.addKeywordBindingNamedWith, 'addKeywordBindingNamed:with:'),

            (cls.setParseTreeASTMaping, 'setParseTreeASTMaping:'),
            (cls.setSemanticAnalysisMapping, 'setSemanticAnalysisMapping:'),

            (cls.enableTypeSystem, 'enableTypeSystem'),
            (cls.enterTopLevelNamespace, 'enterTopLevelNamespace'),
            (cls.enterNamespaceNamed, 'enterNamespaceNamed:'),

            (cls.primitiveFailed, 'primitiveFailed'),
            (cls.subclassResponsibility, 'subclassResponsibility'),

            ## Utility
            (cls.print, 'print:')
        ])

    def activate(self):
        setActiveBasicTypeEnvironment(self.basicTypeEnvironment)

    def enterTopLevelNamespace(self):
        self.activeNamespace = self.topLevelEnvironment

    def enterNamespaceNamed(self, namespaceName):
        childNamespace = self.activeNamespace.lookupSymbol(namespaceName)
        if childNamespace is None:
            childNamespace = NamespaceLevelEnvironment(self.activeNamespace)
            self.activeNamespace.setSymbolBinding(namespaceName, childNamespace)
        self.activeNamespace = childNamespace

    def addBindingNamedWith(self, bindingName, bindingValue):
        self.activeNamespace.setSymbolBinding(bindingName, bindingValue)

    def addKeywordBindingNamedWith(self, bindingName, bindingValue):
        self.addBindingNamedWith(bindingName, bindingValue)

    def addBasicTypeNamedWith(self, bindingName, basicType):
        self.addBindingNamedWith(bindingName, basicType)
        self.basicTypeEnvironment[bindingName] = basicType
        if bindingName == 'MetaType':
            basicType.addMetaTypeRootMethods()

    def addBasicTypeWithName(self, basicType, basicTypeName):
        self.basicTypeEnvironment[basicTypeName] = basicType
        self.activeNamespace.setSymbolBinding(basicTypeName, basicType)
        if basicTypeName == 'MetaType':
            basicType.addMetaTypeRootMethods()

    def addPrimitiveTypeNamedWithSchema(self, typeName, schema):
        typeNameSymbol = Symbol(typeName)
        type = SimpleType(name = typeNameSymbol, schema = schema)
        self.addBasicTypeWithName(type, typeNameSymbol)

    def addPrimitiveBooleanTypeNamedWithSizeAlignment(self, typeName, typeSize, typeAlignment):
        self.addPrimitiveTypeNamedWithSchema(typeName, PrimitiveBooleanTypeSchema(typeSize, typeAlignment))

    def addPrimitiveUnsignedIntegerTypeNamedWithSizeAlignment(self, typeName, typeSize, typeAlignment):
        self.addPrimitiveTypeNamedWithSchema(typeName, PrimitiveUnsignedIntegerTypeSchema(typeSize, typeAlignment))

    def addPrimitiveSignedIntegerTypeNamedWithSizeAlignment(self, typeName, typeSize, typeAlignment):
        self.addPrimitiveTypeNamedWithSchema(typeName, PrimitiveSignedIntegerTypeSchema(typeSize, typeAlignment))

    def addPrimitiveCharacterTypeNamedWithSizeAlignment(self, typeName, typeSize, typeAlignment):
        self.addPrimitiveTypeNamedWithSchema(typeName, PrimitiveCharacterTypeSchema(typeSize, typeAlignment))

    def addPrimitiveFloatTypeNamedWithSizeAlignment(self, typeName, typeSize, typeAlignment):
        self.addPrimitiveTypeNamedWithSchema(typeName, PrimitiveFloatTypeSchema(typeSize, typeAlignment))

    def addGCClassNamedWithInstanceVariables(self, className, instanceVariables):
        self.addGCClassNamedWithSuperclassInstanceVariables(className, self.basicTypeEnvironment.get('Object', None), instanceVariables)

    def addGCClassNamedWithSuperclassInstanceVariables(self, className, superclass, instanceVariables):
        typeNameSymbol = Symbol(className)
        type = SimpleType(name = typeNameSymbol, supertype = superclass, schema = GCClassTypeSchema(instanceVariables))
        self.addBasicTypeWithName(type, typeNameSymbol)

    def setParseTreeASTMaping(self, parseTreeASTMapping):
        self.parseTreeASTMapping = parseTreeASTMapping
        print(parseTreeASTMapping)

    def setSemanticAnalysisMapping(self, semanticAnalysisMapping):
        self.semanticAnalysisMapping = semanticAnalysisMapping
        print(semanticAnalysisMapping)

    def enableTypeSystem(self):
        self.isTypeSystemEnabled = True

    def print(self, string):
        print(string)

    def subclassResponsibility(self):
        raise SubclassResponsibility()

    def primitiveFailed(self):
        raise PrimitiveFailed()
