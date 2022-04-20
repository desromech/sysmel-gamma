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

    def performWithArguments(self, selector, arguments):
        if len(arguments) == 0:
            boundSymbol = self.lookupSymbol(selector)
            if boundSymbol is not None:
                return boundSymbol.getSymbolBindingReferenceValue()
        return super().performWithArguments(selector, arguments)

class ScriptEvaluationEnvironment(LexicalScope):
    def __init__(self, parentScope):
        super().__init__(parentScope)

    def evaluateScriptFile(self, scriptFile, scriptFilename, scriptDirectory):
        self.setSymbolBinding(Symbol('__CurrentScriptFilename__'), String(scriptFilename))
        self.setSymbolBinding(Symbol('__CurrentScriptDirectory__'), String(scriptDirectory))
        scriptSource = scriptFile.read()
        parseTree = parseString(scriptSource, scriptFilename)
        return parseTree.evaluateWithEnvironment(self)

class BootstrapCompiler(BehaviorTypedObject):
    def __init__(self):
        super().__init__()
        self.topLevelEnvironment = NamespaceLevelEnvironment()
        self.topLevelEnvironment.setSymbolBinding('__BootstrapCompiler__', self)
        self.basicTypeEnvironment = {}
        self.isTypeSystemEnabled = False
        self.enterTopLevelNamespace()

    def makeScriptEvaluationEnvironment(self):
        return ScriptEvaluationEnvironment(self.topLevelEnvironment)

    @classmethod
    def initializeBehaviorType(cls, type):
        BehaviorTypedObject.initializeBehaviorType(type)
        type.addPrimitiveMethodsWithSelectors([
            ## Type system
            (cls.addBasicTypeWithName, 'addBasicType:withName:'),
            (cls.addPrimitiveBooleanTypeNamedWithSizeAlignment, 'addPrimitiveBooleanTypeNamed:size:alignment:'),
            (cls.addPrimitiveUnsignedIntegerTypeNamedWithSizeAlignment, 'addPrimitiveUnsignedIntegerTypeNamed:size:alignment:'),
            (cls.addPrimitiveSignedIntegerTypeNamedWithSizeAlignment, 'addPrimitiveSignedIntegerTypeNamed:size:alignment:'),
            (cls.addPrimitiveCharacterTypeNamedWithSizeAlignment, 'addPrimitiveCharacterTypeNamed:size:alignment:'),
            (cls.addPrimitiveFloatTypeNamedWithSizeAlignment, 'addPrimitiveFloatTypeNamed:size:alignment:'),
            (cls.addGCClassNamedWithInstanceVariables, 'addGCClassNamed:instanceVariables:'),
            (cls.addGCClassNamedWithSuperclassInstanceVariables, 'addGCClassNamed:superclass:instanceVariables:'),

            (cls.enableTypeSystem, 'enableTypeSystem'),
            (cls.enterTopLevelNamespace, 'enterTopLevelNamespace'),
            (cls.enterNamespaceNamed, 'enterNamespaceNamed:'),

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

    def addBasicTypeWithName(self, basicType, basicTypeName):
        self.basicTypeEnvironment[basicTypeName] = basicType
        self.activeNamespace.setSymbolBinding(basicTypeName, basicType)

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

    def enableTypeSystem(self):
        self.isTypeSystemEnabled = True

    def print(self, string):
        print(string)