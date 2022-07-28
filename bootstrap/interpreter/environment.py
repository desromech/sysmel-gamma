from lib2to3.pytree import convert
from parser import parseString
from types import MethodType

from typesystem import *
import typesystem

class IdentifierLookupScope(TypedValue):  
    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('IdentifierLookupScope'))

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'parent':
            return self.parent
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def lookupSymbol(self, symbol):
        return None

    def lookupSymbolRecursively(self, symbol):
        result = self.lookupSymbol(symbol)
        if result is not None:
            return result
        elif self.parent is not None:
            return self.parent.lookupSymbolRecursively(symbol)
        else:
            return None

    @primitiveNamed('identifierLookupScope.makeChildLexicalScope')
    def makeChildLexicalScope(self):
        return LexicalScope(self)

class LexicalScope(IdentifierLookupScope):
    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('LexicalScope'))

    def __init__(self, parent):
        super().__init__(parent)
        self.symbolTable = SymbolTable()

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'symbolTable':
            return self.symbolTable
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def setSymbolValueBinding(self, symbol, value):
        self.symbolTable.setSymbolValueBinding(symbol, value)

    def setSymbolImmutableValue(self, symbol, value):
        self.symbolTable.setSymbolImmutableValue(symbol, value)

    def setSymbolBinding(self, symbol, binding):
        self.symbolTable.setSymbolBinding(symbol, binding)

    def lookupSymbol(self, symbol):
        return self.symbolTable.lookupSymbol(symbol)

class ProgramEntityLookupScope(IdentifierLookupScope):
    def __init__(self, programEntity, parent):
        super().__init__(parent)
        self.programEntity = programEntity

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'programEntity':
            return self.programEntity
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    @primitiveNamed('programEntityLookupScope.lookupSymbol')
    def primitiveLookupSymbol(self, symbol):
        return self.lookupSymbol(symbol)
        
    def lookupSymbol(self, symbol):
        return self.programEntity.lookupScopeSymbol(symbol)

    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('ProgramEntityLookupScope'))

class NamespaceLookupScope(ProgramEntityLookupScope):
    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('NamespaceLookupScope'))

class ScriptEvaluationScope(LexicalScope):
    def __init__(self, parent, bootstrapCompiler):
        super().__init__(parent)
        self.bootstrapCompiler = bootstrapCompiler

    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('ScriptEvaluationScope'))

    def evaluateScriptFile(self, evaluationMachine, scriptFile, scriptFilename, scriptDirectory):
        self.setSymbolValueBinding(Symbol.intern('__CurrentScriptFilename__'), String(scriptFilename))
        self.setSymbolValueBinding(Symbol.intern('__CurrentScriptDirectory__'), String(scriptDirectory))
        scriptSource = scriptFile.read()
        parseTree = parseString(scriptSource, scriptFilename)
        if self.bootstrapCompiler.isTypeSystemEnabled:
            convertedASTNode = parseTree.convertIntoGenericASTWith(self.bootstrapCompiler)
            resultValue = convertedASTNode.performWithArguments(evaluationMachine, Symbol.intern('analyzeAndEvaluateNodeWithScriptEvaluationScope:'), [self])
        else:
            resultValue = parseTree.evaluateWithEnvironment(evaluationMachine, self)

        print(scriptFilename, resultValue)
        return resultValue

class BootstrapCompiler(BehaviorTypedObject):
    def __init__(self):
        super().__init__()
        self.topLevelNamespace = Namespace(parent = None, name = Symbol.intern('__global__'))

        self.topLevelEnvironment = LexicalScope(NamespaceLookupScope(self.topLevelNamespace, None))
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

            (cls.getTopLevelNamespace, 'getTopLevelEnvironment', '(SelfType) => Reflection Namespace'),
            (cls.getTopLevelEnvironment, 'getTopLevelEnvironment', '(SelfType) => Reflection Semantic IdentifierLookupScoe'),

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

    def getTopLevelNamespace(self):
        return self.topLevelNamespace

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
        self.activeNamespace = self.topLevelNamespace

    def enterNamespaceNamed(self, namespaceName):
        self.activeNamespace = self.activeNamespace.getOrCreateChildNamespaceNamed(Symbol.intern(namespaceName))

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
        typeNameSymbol = Symbol.intern(typeName)
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
        typeNameSymbol = Symbol.intern(className)
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
