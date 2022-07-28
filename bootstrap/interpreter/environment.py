from lib2to3.pytree import convert
from parser import parseString
from types import MethodType

from typesystem import *
import typesystem

class IdentifierLookupScope(TypedValue):  
    def getType(self):
        return getSemanticAnalysisType(Symbol('IdentifierLookupScope'))

    def __init__(self, parentScope):
        super().__init__()
        self.parentScope = parentScope

    @primitiveNamed('identifierLookupScope.lookupSymbol')
    def lookupSymbol(self, symbol):
        return None

    @primitiveNamed('identifierLookupScope.lookupSymbolRecursively')
    def lookupSymbolRecursively(self, symbol):
        result = self.lookupSymbol(symbol)
        if result is not None:
            return result
        elif self.parentScope is not None:
            return self.parentScope.lookupSymbolRecursively(symbol)
        else:
            return None

    @primitiveNamed('identifierLookupScope.makeChildLexicalScope')
    def makeChildLexicalScope(self):
        return LexicalScope(self)

class LexicalScope(IdentifierLookupScope):
    def getType(self):
        return getSemanticAnalysisType(Symbol('LexicalScope'))

    def __init__(self, parentScope):
        super().__init__(parentScope)
        self.symbolTable = {}

    def setSymbolValueBinding(self, symbol, value):
        self.symbolTable[symbol] = value.asSymbolBindingWithName(symbol)

    def setSymbolImmutableValue(self, symbol, value):
        self.symbolTable[symbol] = SymbolValueBinding(symbol, value)

    def setSymbolBinding(self, symbol, binding):
        self.symbolTable[symbol] = binding

    @primitiveNamed('lexicalScope.setSymbolImmutableValue')
    def primitiveSetSymbolImmutableValue(self, symbol, value):
        self.setSymbolImmutableValue(symbol, value)
        return getVoidValue()

    @primitiveNamed('lexicalScope.setSymbolValueBinding')
    def primitiveSetSymbolValueBinding(self, symbol, value):
        self.setSymbolValueBinding(symbol, value)
        return getVoidValue()

    @primitiveNamed('lexicalScope.setSymbolBinding')
    def primitiveSetSymbolBinding(self, symbol, binding):
        self.setSymbolBinding(symbol, binding)
        return getVoidValue()

    def lookupSymbol(self, symbol):
        return self.symbolTable.get(symbol, None)

class NamespaceScope(LexicalScope):
    def getType(self):
        return getSemanticAnalysisType(Symbol('NamespaceScope'))

    def __init__(self, parentScope = None):
        super().__init__(parentScope)

    def setSymbolValueBinding(self, symbol, value):
        super().setSymbolValueBinding(symbol, value)
        value.onGlobalBindingWithSymbolAdded(symbol)

    def performWithArguments(self, machine, selector, arguments):
        if len(arguments) == 0:
            boundSymbol = self.lookupSymbol(selector)
            if boundSymbol is not None:
                return boundSymbol.getSymbolBindingReferenceValue()
        return super().performWithArguments(machine, selector, arguments)

class ScriptEvaluationScope(LexicalScope):
    def __init__(self, parentScope, bootstrapCompiler):
        super().__init__(parentScope)
        self.bootstrapCompiler = bootstrapCompiler

    def getType(self):
        return getSemanticAnalysisType(Symbol('ScriptEvaluationScope'))

    def evaluateScriptFile(self, evaluationMachine, scriptFile, scriptFilename, scriptDirectory):
        self.setSymbolValueBinding(Symbol('__CurrentScriptFilename__'), String(scriptFilename))
        self.setSymbolValueBinding(Symbol('__CurrentScriptDirectory__'), String(scriptDirectory))
        scriptSource = scriptFile.read()
        parseTree = parseString(scriptSource, scriptFilename)
        if self.bootstrapCompiler.isTypeSystemEnabled:
            convertedASTNode = parseTree.convertIntoGenericASTWith(self.bootstrapCompiler)
            resultValue = convertedASTNode.performWithArguments(evaluationMachine, Symbol('analyzeAndEvaluateNodeWithScriptEvaluationScope:'), [self])
        else:
            resultValue = parseTree.evaluateWithEnvironment(evaluationMachine, self)

        print(scriptFilename, resultValue)
        return resultValue

class BootstrapCompiler(BehaviorTypedObject):
    def __init__(self):
        super().__init__()
        self.topLevelEnvironment = NamespaceScope()
        self.topLevelEnvironment.setSymbolValueBinding('__BootstrapCompiler__', self)
        self.topLevelEnvironment.setSymbolValueBinding('__TypeBuilder__', TypeBuilder())
        self.basicTypeEnvironment = {}
        self.isTypeSystemEnabled = False
        self.parseTreeASTMapping = None
        self.semanticAnalysisMapping = None
        self.sourcePositionMemoizationTable = {}
        self.sourceCollectionMemoizationTable = {}
        self.emptySourcePosition = None
        self.sizeType = None
        self.enterTopLevelNamespace()
        typesystem.ActiveBootstrapCompiler = self

    def makeScriptEvaluationScope(self):
        return ScriptEvaluationScope(self.topLevelEnvironment, self)

    @classmethod
    def initializeBehaviorType(cls, type):
        BehaviorTypedObject.initializeBehaviorType(type)
        type.addPrimitiveMethodsWithSelectors([
            (cls.addBasicTypeNamedWith, 'addBasicTypeNamed:with:', '(SelfType -- AnyValue -- AnyValue) => Void'),
            (cls.addBindingNamedWith, 'addBindingNamed:with:', '(SelfType -- AnyValue -- AnyValue) => Void'),
            (cls.addKeywordBindingNamedWith, 'addKeywordBindingNamed:with:', '(SelfType -- AnyValue -- AnyValue) => Void'),

            (cls.setParseTreeASTMaping, 'setParseTreeASTMaping:', '(SelfType -- AnyValue) => Void'),
            (cls.setSemanticAnalysisMapping, 'setSemanticAnalysisMapping:', '(SelfType -- AnyValue) => Void'),

            (cls.enableTypeSystem, 'enableTypeSystem', '(SelfType) => Void'),
            (cls.enterTopLevelNamespace, 'enterTopLevelNamespace', '(SelfType) => Void'),
            (cls.enterNamespaceNamed, 'enterNamespaceNamed:', '(SelfType -- AnyValue) => Void'),

            (cls.primitiveFailed, 'primitiveFailed', '(SelfType) => Void'),
            (cls.subclassResponsibility, 'subclassResponsibility', '(SelfType) => Void'),

            (cls.getTopLevelEnvironment, 'getTopLevelEnvironment', '(SelfType) => Void'),

            (cls.parseErrorAt, 'parseError:at:', '(SelfType -- String -- AnyValue) => Void'),
            (cls.semanticAnalysisErrorAt, 'semanticAnalysisError:at:', '(SelfType -- String -- AnyValue) => Void'),

            ## Target platform
            (cls.getPointerSize, 'getPointerSize', '(SelfType) => Integer'),

            ## Utility
            (cls.print, 'print:', '(SelfType -- AnyValue) => Void')
        ])

    def getEmptySourcePosition(self):
        if self.emptySourcePosition is None:
            self.emptySourcePosition = self.makeASTNodeWithSlots('EmptySourcePosition')
        return self.emptySourcePosition

    def getTopLevelEnvironment(self):
        return self.topLevelEnvironment

    def convertASTSourcePosition(self, sourcePosition):
        if sourcePosition in self.sourcePositionMemoizationTable:
            return self.sourcePositionMemoizationTable[sourcePosition]

        convertedSourcePosition = sourcePosition.convertIntoTargetSourcePositionWith(self)
        self.sourcePositionMemoizationTable[sourcePosition] = convertedSourcePosition
        return convertedSourcePosition

    def convertASTSourceCollection(self, sourceCollection):
        if sourceCollection in self.sourceCollectionMemoizationTable:
            return self.sourceCollectionMemoizationTable[sourceCollection]

        convertedSourceCollection = sourceCollection.convertIntoTargetSourceCollectionWith(self)
        self.sourceCollectionMemoizationTable[sourceCollection] = convertedSourceCollection
        return convertedSourceCollection

    def convertSize(self, size):
        if self.sizeType is None:
            self.sizeType = getBasicTypeNamed('Size')
        return self.sizeType.basicNewWithValue(size)

    def makeASTNodeArraySlice(self, elements):
        arraySliceType = self.parseTreeASTMapping.at('NodeSharedArraySlice')
        return arraySliceType.basicNewWithArraySliceElements(ListValueMock(elements))

    def makeASTNodeWithSlots(self, nodeName, **namedSlots):
        nodeType = self.parseTreeASTMapping.at(nodeName)
        return nodeType.basicNewWithNamedSlots(Dictionary.fromDict(namedSlots))

    def activate(self):
        setActiveBasicTypeEnvironment(self.basicTypeEnvironment)

    def enterTopLevelNamespace(self):
        self.activeNamespace = self.topLevelEnvironment

    def enterNamespaceNamed(self, namespaceName):
        childNamespace = self.activeNamespace.lookupSymbol(namespaceName)
        if childNamespace is None:
            childNamespace = NamespaceScope(self.activeNamespace)
            self.activeNamespace.setSymbolValueBinding(namespaceName, childNamespace)
        else:
            childNamespace = childNamespace.getSymbolBindingReferenceValue()
        self.activeNamespace = childNamespace

    def addBindingNamedWith(self, bindingName, bindingValue):
        self.activeNamespace.setSymbolValueBinding(bindingName, bindingValue)

    def addKeywordBindingNamedWith(self, bindingName, bindingValue):
        self.addBindingNamedWith(bindingName, bindingValue)

    def addBasicTypeNamedWith(self, bindingName, basicType):
        self.addBindingNamedWith(bindingName, basicType)
        self.basicTypeEnvironment[bindingName] = basicType
        if bindingName == 'MetaType':
            basicType.addMetaTypeRootMethods()

    def addBasicTypeWithName(self, basicType, basicTypeName):
        self.basicTypeEnvironment[basicTypeName] = basicType
        self.activeNamespace.setSymbolValueBinding(basicTypeName, basicType)
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
        ##print(parseTreeASTMapping)

    def setSemanticAnalysisMapping(self, semanticAnalysisMapping):
        self.semanticAnalysisMapping = semanticAnalysisMapping
        typesystem.SemanticAnalysisTypeMapping = semanticAnalysisMapping
        ##print(semanticAnalysisMapping)

    def enableTypeSystem(self):
        self.isTypeSystemEnabled = True

    def print(self, string):
        print(string)

    def subclassResponsibility(self):
        raise SubclassResponsibility('Subclass responsibility')

    def primitiveFailed(self):
        raise PrimitiveFailed('Primitive failed')

    def getPointerSize(self):
        return Integer(8)

    def parseErrorAt(self, errorMessage, sourcePosition):
        raise InterpreterParseError(sourcePosition, errorMessage)

    def semanticAnalysisErrorAt(self, errorMessage, sourcePosition):
        raise InterpreterSemanticAnalysisError(sourcePosition, errorMessage)
