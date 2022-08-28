from os import environ
from queue import Empty

from errors import *
from evalmachine import *

ActiveBootstrapCompiler = None
BasicTypeEnvironment = {}
SemanticAnalysisTypeMapping = {}

PrimitiveMethodTable = {}

NextRandomIdentityHash = 1

def generateNextRandomIdentityHash():
    # xorshift64 from https://en.wikipedia.org/wiki/Xorshift [27th July, 2022]
    global NextRandomIdentityHash
    NextRandomIdentityHash ^= NextRandomIdentityHash << 13
    NextRandomIdentityHash ^= NextRandomIdentityHash >> 7
    NextRandomIdentityHash ^= NextRandomIdentityHash << 17
    NextRandomIdentityHash &= (1<<64) - 1
    return NextRandomIdentityHash

def getSemanticAnalysisType(symbol):
    return SemanticAnalysisTypeMapping.at(symbol)

def makeAnyValueArraySlice(collection):
    return getBasicTypeNamed('AnyArraySlice').basicNewWithArraySliceElements(collection)

class ValueInterface:
    def performWithArguments(self, machine, selector, arguments):
        raise NotImplementedError()

    def setConstructionTemplateAndArguments(self, template, arguments):
        pass

    def onGlobalBindingWithSymbolAdded(self, symbol):
        pass

    def yourself(self):
        return self

    def asBooleanValue(self):
        raise NonBooleanEvaluableValue()

    def answersTo(self, selector):
        return False

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.printString()

    def toString(self):
        selector = Symbol.intern('toString')
        if self.answersTo(selector):
            return self.performWithArguments(EvaluationMachine.getActive(), selector, [])
        return self.defaultToString()

    def printString(self):
        selector = Symbol.intern('printString')
        if self.answersTo(selector):
            return self.performWithArguments(EvaluationMachine.getActive(), selector, [])
        return self.defaultPrintString()

    def defaultToString(self):
        return self.printString()

    def defaultPrintString(self):
        return 'a ' + str(self.__class__)

    def canonicalizeForAnyValue(self):
        return self

    def asInteger(self):
        raise NotImplementedError('asInteger() in %s' % repr(self.__class__))

    def shallowCopyValue(self):
        return self.shallowCopy()

    def asSymbolBindingWithName(self, name):
        if 'SymbolBinding' in BasicTypeEnvironment and 'MetaType' in BasicTypeEnvironment and self.getType().isSubtypeOf(getBasicTypeNamed('SymbolBinding')):
            return self
        return SymbolValueBinding(name, self)

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        raise SubclassResponsibility()

    def setSlotWithIndexAndName(self, slotIndex, slotName, value):
        raise SubclassResponsibility()

    def installedInType(self, type):
        pass

    def installedInMetaTypeOf(self, type):
        pass

    def asArraySlice(self):
        return self.performWithArguments(EvaluationMachine.getActive(), Symbol.intern('asArraySlice'), ())

    def asSharedArraySlice(self):
        return self.performWithArguments(EvaluationMachine.getActive(), Symbol.intern('asSharedArraySlice'), ())

    def isConversionMethod(self):
        return False

    def isConstructionMethod(self):
        return False

    def isExplicitMethod(self):
        return False

    def asCanonicalTypeForDependentTypeArgument(self):
        raise SubclassResponsibility()

    def asCanonicalTypeForDependentType(self):
        raise InterpreterError('Expected a type instead of %s' % repr(self))

    def identityHash(self):
        if not hasattr(self, '__identityHash__'):
            __identityHash__ = self.generateIdentityHash()
        return __identityHash__

    def generateIdentityHash(self):
        return generateNextRandomIdentityHash()

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.performWithArguments(machine, Symbol.intern('run:with:in:'), (selector, makeAnyValueArraySlice(arguments), receiver))

    def evaluateWithArguments(self, machine, arguments):
        return self.performWithArguments(machine, Symbol.intern('evaluateWithArguments:'), (makeAnyValueArraySlice(arguments),))

class TypedValue(ValueInterface):
    def getType(self):
        raise NotImplementedError('getType() in %s' % repr(self.__class__))

    def performWithArguments(self, machine, selector, arguments):
        return self.getType().runWithIn(machine, selector, arguments, self)

    def answersTo(self, selector):
        return self.getType().lookupLocalSelector(selector) is not None

    def shallowCopyValue(self):
        if self.getType().schema.hasPointerOrReferenceValueCopySemantics():
            return self

        return self.shallowCopy()

    def asCanonicalTypeForDependentTypeArgument(self):
        return getBasicTypeNamed('AnyValue')

class FunctionTypeValue(TypedValue):
    def __init__(self, type, bootstrapImplementation = None, implementation = None, functionTypeSpec = None):
        super().__init__()
        self.type = type
        self.functionTypeSpec = functionTypeSpec
        self.name = None
        self.bootstrapImplementation = bootstrapImplementation
        self.implementation = implementation
        self.rawOwnerType = None
        self.rawOwnerTypeIsMetaType = False

    def installedInType(self, type):
        self.rawOwnerType = type
        self.rawOwnerTypeIsMetaType = False

    def installedInMetaTypeOf(self, type):
        self.rawOwnerType = type
        self.rawOwnerTypeIsMetaType = True

    def shallowCopyValue(self):
        return self

    def getOwnerType(self):
        if self.rawOwnerTypeIsMetaType:
            return self.rawOwnerType.getType()
        else:
            return self.rawOwnerType

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'implementation':
            return self.implementation
        elif slotName == 'bootstrapImplementation':
            return self.bootstrapImplementation
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def getType(self):
        if self.type is None:
            self.type = FunctionType.constructFromTypeSpec(self.functionTypeSpec, self.getOwnerType())
            assert self.type is not None
        return self.type

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.evaluateWithArguments(machine, tuple([receiver] + list(arguments)))

    def evaluateWithArguments(self, machine, arguments):
        if self.bootstrapImplementation is not None:
            result = self.bootstrapImplementation.evaluateWithArguments(machine, arguments)
        else:
            result = self.implementation.evaluateWithArguments(machine, arguments)
        return self.applyResultTransform(machine, result)

    def hasMethodFlag(self, methodFlag):
        if self.bootstrapImplementation is not None:
            return self.bootstrapImplementation.hasMethodFlag(methodFlag)
        else:
            return self.implementation.performWithArguments(EvaluationMachine.getActive(), Symbol.intern('hasMethodFlag:'), (methodFlag,))

    def performWithArguments(self, machine, selector, arguments):
        if selector == '()':
            return self.evaluateWithArguments(machine, ())
        elif selector == '():':
            return self.evaluateWithArguments(machine, arguments[0])
        elif selector == 'memoized':
            return self.asMemoizedFunction()
        elif selector == 'templated':
            return self.asTemplatedFunction()
        return super().performWithArguments(machine, selector, arguments)

    def asMemoizedFunction(self):
        return MemoizedFunctionTypeValue(self)

    def asTemplatedFunction(self):
        return TemplatedFunctionTypeValue(self)

    def applyResultTransform(self, machine, result):
        return result

    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def defaultPrintString(self) -> str:
        if self.name is not None:
            return self.name
        return "a " + str(self.getType())

    def __call__(self, *args):
        return self.evaluateWithArguments(EvaluationMachine.getActive(), args)

class PrimitiveMethod(TypedValue):
    def __init__(self, method):
        self.method = method
        self.methodFlags = []

    @classmethod
    def makeFunction(cls, method, functionTypeSpec):
        return FunctionTypeValue(None, bootstrapImplementation = cls(method), functionTypeSpec = functionTypeSpec)

    def getType(self):
        return getBasicTypeNamed('BootstrapPrimitiveMethod')

    def evaluateWithArguments(self, machine, arguments):
        return coerceNoneToNil(self.method(*arguments))

    def runWithIn(self, machine, selector, arguments, receiver):
        return coerceNoneToNil(self.method(receiver, *arguments))

    def hasMethodFlag(self, methodFlag):
        return getBooleanValue(methodFlag in self.methodFlags)

def primitiveNamed(primitiveName, functionTypeSpec = None):
    def decorator(primitiveImplementation):
        primitiveMethod = PrimitiveMethod(primitiveImplementation)
        PrimitiveMethodTable[primitiveName] = primitiveMethod
        return primitiveImplementation
    return decorator

def setActiveBasicTypeEnvironment(basicTypeEnvironment):
    global BasicTypeEnvironment
    BasicTypeEnvironment = basicTypeEnvironment

def getBasicTypeNamed(symbol):
    return BasicTypeEnvironment[symbol]

def getBooleanValue(value):
    return getBasicTypeNamed('Boolean').basicNewWithTypeTheoryBoolean(value)

def getBoolean8Value(value):
    return getBasicTypeNamed('Boolean8').basicNewWithValue(int(value))

def getVoidValue():
    return getBasicTypeNamed('Void').basicNew()

def coerceValueToBoolean(value):
    if 'Boolean' in BasicTypeEnvironment:
        return getBasicTypeNamed('Boolean').coerceValue(value)
    return value

def getSizeValue(value):
    if 'Size' not in BasicTypeEnvironment:
        return Integer(value)
    return getBasicTypeNamed('Size').basicNewWithValue(int(value))

def coerceNoneToNil(value):
    if value is None and 'Undefined' in BasicTypeEnvironment:
        return getBasicTypeNamed('Undefined').basicNew()
    return value

class SymbolBinding(TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('SymbolBinding'))

    def getSymbolBindingReferenceValue(self):
        raise NotImplementedError()

    def asSymbolBindingWithName(self, name):
        return self

class SymbolValueBinding(SymbolBinding):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('SymbolValueBinding'))

    def getSymbolBindingReferenceValue(self):
        return self.value

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'value':
            return self.value
        elif slotName == 'name':
            return self.name
        return super().getSlotWithIndexAndName(slotIndex, slotName)

class ForAllPlaceholderBinding(SymbolBinding):
    def __init__(self, name, expectedType):
        self.name = name
        self.value = None
        self.expectedType = expectedType

    def getSymbolBindingReferenceValue(self):
        if self.value is None:
            return self
        else:
            return self.value

    def getType(self):
        return getSemanticAnalysisType(Symbol.intern('ForAllPlaceholderBinding'))

class TypeInterface:
    def canBeCoercedToType(self, targetType):
        return self is targetType

    def coerceValue(self, value):
        if value.getType() is self:
            return value
        raise CannotCoerceValueToType('Cannot coerce (%s:%s) into type "%s"' % (repr(value.getType()), repr(value), repr(self)))

    def runWithIn(self, machine, selector, arguments, receiver):
        raise NotImplementedError()

    @primitiveNamed('type.lookupLocalMacroSelector')
    def primitiveLookupLocalMacroSelector(self, selector):
        return self.lookupLocalMacroSelector(selector)

    @primitiveNamed('type.lookupMacroSelector')
    def primitiveLookupMacroSelector(self, selector):
        return self.lookupMacroSelector(selector)

    @primitiveNamed('type.lookupLocalSelector')
    def primitiveLookupLocalSelector(self, selector):
        return self.lookupLocalSelector(selector)

    @primitiveNamed('type.lookupSelector')
    def primitiveLookupSelector(self, selector):
        return self.lookupSelector(selector)

    @primitiveNamed('type.lookupLocalMacroFallbakSelector')
    def primitiveLookupLocalMacroFallbackSelector(self, selector):
        return self.lookupLocalMacroFallbackSelector(selector)

    @primitiveNamed('type.lookupMacroFallbackSelector')
    def primitiveLookupMacroFallbackSelector(self, selector):
        return self.lookupMacroFallbackSelector(selector)

    @primitiveNamed('type.supportsDynamicDispatch')
    def primitiveSupportsDynamicDispatch(self):
        return getBooleanValue(self.supportsDynamicDispatch())

    def supportsDynamicDispatch(self):
        return False

    def asCanonicalTypeForDependentType(self):
        return self

class Integer(int, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('Integer'))

    def defaultPrintString(self):
        return str(int(self))

    def defaultToString(self):
        return str(int(self))

    @primitiveNamed('integer.arithmetic.neg')
    def primitiveNeg(self):
        return Integer(-self)

    @primitiveNamed('integer.arithmetic.add')
    def primitiveAdd(self, other):
        return Integer(self + other)

    @primitiveNamed('integer.arithmetic.sub')
    def primitiveSub(self, other):
        return Integer(self - other)

    @primitiveNamed('integer.arithmetic.mul')
    def primitiveMul(self, other):
        return Integer(self * other)

    @primitiveNamed('integer.arithmetic.div')
    def primitiveDiv(self, other):
        return Integer(self / other)

    @primitiveNamed('integer.arithmetic.rem')
    def primitiveRem(self, other):
        return Integer(self % other)

    @primitiveNamed('integer.comparison.equals')
    def primitiveEquals(self, other):
        return getBooleanValue(self == other)

    @primitiveNamed('integer.comparison.notEquals')
    def primitiveNotEquals(self, other):
        return getBooleanValue(self != other)

    @primitiveNamed('integer.comparison.lessThan')
    def primitiveLessThan(self, other):
        return getBooleanValue(self < other)

    @primitiveNamed('integer.comparison.lessOrEqual')
    def primitiveLessOrEqual(self, other):
        return getBooleanValue(self <= other)

    @primitiveNamed('integer.comparison.greaterThan')
    def primitiveGreaterThan(self, other):
        return getBooleanValue(self > other)

    @primitiveNamed('integer.comparison.greaterOrEqual')
    def primitiveGreaterOrEqual(self, other):
        return getBooleanValue(self >= other)

    @primitiveNamed('integer.conversion.toString')
    def primitiveToString(self):
        return String(str(int(self)))

    def shallowCopy(self):
        return self

    def asInteger(self):
        return self
        
class Character(int, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('Character'))

    def shallowCopy(self):
        return self

    @primitiveNamed('character.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

class Float(float, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('Float'))

    def defaultPrintString(self):
        return str(float(self))

    def defaultToString(self):
        return str(float(self))

    def shallowCopy(self):
        return self

    @primitiveNamed('float.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

class String(str, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('String'))

    def defaultToString(self):
        return self

    @primitiveNamed('string.conversion.printString')
    def defaultPrintString(self):
        result = '"'
        for c in self:
            if c == '"':
                result += '\"'
            elif c == '\n':
                result += '\n'
            elif c == '\r':
                result += '\r'
            elif c == '\t':
                result += '\t'
            else:
                result += c
        result += '"'
        return String(result)

    @primitiveNamed('string.concat')
    def primitiveConcat(self, other):
        return String(self + other)

    @primitiveNamed('string.format')
    def primitiveFormat(self, parameters):
        formattedString = ''
        i = 0
        while i < len(self):
            c = self[i]
            if c == '{':
                i += 1
                parameterIndex = ''
                while i < len(self) and self[i] != '}':
                    parameterIndex += self[i]
                    i += 1
                parameter = parameters[int(parameterIndex)]
                formattedString += str(parameter)
            else:
                formattedString += c
            i += 1
        return String(formattedString)

    @primitiveNamed('symbol.internString')
    def primitiveIntern(self):
        return Symbol.intern(self)

    def shallowCopy(self):
        return String(self)

    @primitiveNamed('string.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

    @primitiveNamed('string.manipulations.withoutSuffix')
    def primitiveWithoutSuffix(self, suffix):
        if len(self) >= len(suffix) and self[-len(suffix):] == suffix:
            return String(self[0:-len(suffix)])
        return self

InternedSymbolTable = {}

class Symbol(str, TypedValue):

    @classmethod
    def intern(cls, string):
        convertedSymbol = Symbol(string)
        if convertedSymbol in InternedSymbolTable:
            return InternedSymbolTable[convertedSymbol]
        InternedSymbolTable[convertedSymbol] = convertedSymbol
        return convertedSymbol

    def getType(self):
        return getBasicTypeNamed(Symbol.intern('Symbol'))

    @primitiveNamed('symbol.conversion.toString')
    def defaultToString(self):
        return String(self)

    def shallowCopy(self):
        return self

    @primitiveNamed('symbol.conversion.printString')
    def defaultPrintString(self):
        result = '#"'
        for c in self:
            if c == '"':
                result += '\"'
            elif c == '\n':
                result += '\n'
            elif c == '\r':
                result += '\r'
            elif c == '\t':
                result += '\t'
            else:
                result += c
        result += '"'
        return String(result)

    @primitiveNamed('symbol.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

class Array(tuple, TypedValue):
    def getElementType(self):
        if not hasattr(self, 'elementType'):
            self.elementType = getBasicTypeNamed(Symbol.intern('AnyValue'))
        return self.elementType

    def getType(self):
        if not hasattr(self, 'type'):
            self.type = getBasicTypeNamed(Symbol.intern('Array'))(self.getElementType(), getSizeValue(len(self)))
        return self.type

    def shallowCopy(self):
        copy = Array(map(lambda el: el.shallowCopyValue(), self))
        copy.elementType = self.getElementType()
        return copy

class Association(TypedValue):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def getType(self):
        return getBasicTypeNamed(Symbol.intern('AnyAssociation'))

    def getKey(self):
        return self.key

    def getValue(self):
        return self.value

    def defaultToString(self) -> str:
        return str(self.key) + ' : ' + str(self.value)

    def defaultPrintString(self) -> str:
        return repr(self.key) + ' : ' + repr(self.value)

    def shallowCopy(self):
        return Association(self.key.shallowCopy, self.value.shallowCopy)

class ListValueMock(list, TypedValue):
    pass

class Dictionary(list, TypedValue):

    @classmethod
    def fromDict(cls, d):
        return cls(map(lambda pair: Association(pair[0], pair[1]), d.items()))

    def getType(self):
        return getBasicTypeNamed(Symbol.intern('AnyArrayDictionary'))

    def getHashTable(self):
        if not hasattr(self, 'hashTable'):
            self.hashTable = {}
            for assoc in self:
                self.hashTable[assoc.getKey()] = assoc.getValue()
        return self.hashTable

    def at(self, key):
        return self.getHashTable()[key]

    def defaultPrintString(self):
        result = '#{'
        i = 0
        for element in self:
            if i > 0:
                result += '. '
            result += repr(element)
            i += 1
        result += '}'
        return result

SemanticAnalysisTypeMapping = Dictionary()

def getTupleTypeWithElements(tupleElements):
    elementsArray = Array(tupleElements)
    elementsArray.elementType = getBasicTypeNamed(Symbol.intern('Type'))
    return getBasicTypeNamed(Symbol.intern('Tuple'))(elementsArray)

def getEmptyTupleType():
    return getTupleTypeWithElements(())

def getEmptyTuple():
    return getEmptyTupleType().basicNew()

class Tuple(tuple, TypedValue):
    def getType(self):
        if not hasattr(self, 'type'):
            self.type = getTupleTypeWithElements(tuple(map(lambda x: x.getType(), self)))
        return self.type

class TypeSchemaPrimitiveMethod(PrimitiveMethod):
    def getType(self):
        return getBasicTypeNamed(Symbol.intern('TypeSchemaPrimitiveMethod'))

    def evaluateWithArguments(self, machine, arguments):
        return self.method(*arguments)

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.evaluateWithArguments([receiver] + list(*arguments))

class RecordTypeAccessorPrimitiveMethod(PrimitiveMethod):
    def __init__(self, selector, slotName, slotIndex, slotType):
        super().__init__(None)
        self.selector = selector
        self.slotName = slotName
        self.slotIndex = slotIndex
        self.slotType = slotType

class RecordTypeGetterPrimitiveMethod(RecordTypeAccessorPrimitiveMethod):
    def evaluateWithArguments(self, machine, arguments):
        return self.slotType.coerceValue(coerceNoneToNil(arguments[0].getSlotWithIndexAndName(self.slotIndex, self.slotName)))

class RecordTypeSetterPrimitiveMethod(RecordTypeAccessorPrimitiveMethod):
    def evaluateWithArguments(self, machine, arguments):
        return arguments[0].setSlotWithIndexAndName(self.slotIndex, self.slotName, arguments[1])

class BlockClosure(TypedValue):
    def __init__(self, node, environment, functionType, primitiveName = None, methodFlags = []):
        self.node = node
        self.environment = environment
        self.name = None
        self.primitiveName = primitiveName
        self.methodFlags = methodFlags
        self.functionType = functionType

    def isConversionMethod(self):
        return 'conversion' in self.methodFlags

    def isConstructionMethod(self):
        return 'construction' in self.methodFlags

    def isExplicitMethod(self):
        return 'explicit' in self.methodFlags

    def getType(self):
        return getBasicTypeNamed("BootstrapBlockClosure")

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.evaluateWithArguments(machine, tuple([receiver] + list(arguments)))

    def evaluateWithArguments(self, machine, arguments):
        if self.primitiveName is not None and self.primitiveName in PrimitiveMethodTable:
            return self.node.evaluateClosureResultCoercionWithEnvironmentAndArguments(machine, self.environment, arguments,
                PrimitiveMethodTable[self.primitiveName].evaluateWithArguments(machine, arguments))
        else:
            return self.node.evaluateClosureWithEnvironmentAndArguments(machine, self.environment, arguments)

    def hasMethodFlag(self, methodFlag):
        return getBooleanValue(methodFlag in self.methodFlags)

class TypeSchema(TypedValue):
    def __init__(self):
        self.methodDict = {}
        self.metaTypeMethodDict = {}
        self.ownerType = None
        self.buildPrimitiveMethodDictionary()

    def setSupertypeSchema(self, newSupertypeSchema):
        pass

    def getType(self):
        return getBasicTypeNamed('TypeSchema')

    def isDefaultConstructible(self):
        return False

    def installedInType(self, ownerType):
        assert (self.ownerType is None) or (self.ownerType is ownerType)
        self.ownerType = ownerType
        for method in self.methodDict.values():
            method.installedInType(ownerType)
        for method in self.metaTypeMethodDict.values():
            method.installedInMetaTypeOf(ownerType)

    def finishPendingPrimitiveMethods(self):
        pass

    def buildPrimitiveMethodDictionary(self):
        self.methodDict[Symbol.intern('shallowCopy')] = TypeSchemaPrimitiveMethod.makeFunction(self.primitiveShallowCopy, '(SelfType => SelfType)')
        self.methodDict[Symbol.intern('__type__')] = TypeSchemaPrimitiveMethod.makeFunction(self.getTypeFromValue, '(SelfType => SelfType __type__)')

    def lookupPrimitiveWithSelector(self, selector):
        self.finishPendingPrimitiveMethods()
        if selector in self.methodDict:
            return self.methodDict[selector]
        return None

    def lookupMetaTypePrimitiveWithSelector(self, selector):
        self.finishPendingPrimitiveMethods()
        if selector in self.metaTypeMethodDict:
            return self.metaTypeMethodDict[selector]
        return None

    def primitiveShallowCopy(self, value):
        return value.shallowCopy()

    def primitiveYourself(self, value):
        return value

    def getTypeFromValue(self, value):
        return value.getType()

    def basicNew(self, type):
        raise NonInstanceableType()

    def basicNewWithValue(self, type, value):
        raise NonInstanceableType()

    def basicNewWithSequentialSlots(self, type, namedSlots):
        raise NonInstanceableType()

    def basicNewWithNamedSlots(self, type, namedSlots):
        raise NonInstanceableType()

    def isTrivialTypeSchema(self):
        return False

    def canCoerceValueOfType(self, valueType):
        return False

    def coerceValueOfTypeIntoType(self, value, valueType, targetType):
        raise CannotCoerceValueToType('Cannot coerce value "(%s: %s)" into type "%s".' % (repr(valueType), repr(value), repr(targetType)))

    def hasDirectCoercionToPointerOf(self, baseType, addressSpace):
        return False

    def hasPointerOrReferenceValueCopySemantics(self):
        return False

    def supportsDynamicDispatch(self):
        return False

class TrivialTypedValue(TypedValue):
    def __init__(self, type):
        self.type = type
        self.globalBindingName = None

    def shallowCopy(self):
        return self

    def getType(self):
        return self.type

    def onGlobalBindingWithSymbolAdded(self, bindingName):
        self.globalBindingName = bindingName

    def defaultPrintString(self):
        if self.globalBindingName is not None:
            return self.globalBindingName
        return str(self.type) + '()'

    def __iter__(self):
        return iter([])

class OpaqueTypeSchema(TypeSchema):
    def getType(self):
        return getBasicTypeNamed('OpaqueTypeSchema')

class TraitTypeSchema(TypeSchema):
    def getType(self):
        return getBasicTypeNamed('TraitTypeSchema')

    def isTraitTypeSchema(self):
        return True

class TrivialTypeSchema(TypeSchema):
    def __init__(self):
        super().__init__()
        self.uniqueInstance = None

    def getType(self):
        return getBasicTypeNamed('TrivialTypeSchema')

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        if self.uniqueInstance is None:
            self.uniqueInstance = TrivialTypedValue(valueType)
        return self.uniqueInstance

    def isTrivialTypeSchema(self):
        return True

class AbsurdTypeSchema(TypeSchema):
    def buildPrimitiveMethodDictionary(self):
        pass

    def getType(self):
        return getBasicTypeNamed('AbsurdTypeSchema')

class PrimitiveNumberTypeValue(TypedValue):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def shallowCopy(self):
        return self

    def getType(self):
        return self.type

    def defaultPrintString(self):
        return '%s(%s)' % (str(self.type), str(self.value))

class PrimitiveBooleanTypeValue(PrimitiveNumberTypeValue):
    def asBooleanValue(self):
        return self.value != 0

class PrimitiveIntegerTypeValue(PrimitiveNumberTypeValue):
    @primitiveNamed('primitiveInteger.arithmetic.neg')
    def primitiveNegated(self):
        return self.type.basicNewWithValue(-self.value)

    @primitiveNamed('primitiveInteger.arithmetic.add')
    def primitiveAdd(self, other):
        return self.type.basicNewWithValue(self.value + other.value)

    @primitiveNamed('primitiveInteger.arithmetic.sub')
    def primitiveSubtract(self, other):
        return self.type.basicNewWithValue(self.value - other.value)

    @primitiveNamed('primitiveInteger.arithmetic.mul')
    def primitiveMultiply(self, other):
        return self.type.basicNewWithValue(self.value * other.value)

    @primitiveNamed('primitiveInteger.arithmetic.div')
    def primitiveDivide(self, other):
        return self.type.basicNewWithValue(self.value // other.value)

    @primitiveNamed('primitiveInteger.comparison.equals')
    def primitiveEquals(self, other):
        return getBooleanValue(self.value == other.value)

    @primitiveNamed('primitiveInteger.comparison.notEquals')
    def primitiveNotEquals(self, other):
        return getBooleanValue(self.value != other.value)

    @primitiveNamed('primitiveInteger.comparison.lessThan')
    def primitiveLessThan(self, other):
        return getBooleanValue(self.value < other.value)

    @primitiveNamed('primitiveInteger.comparison.lessOrEqual')
    def primitiveLessOrEqual(self, other):
        return getBooleanValue(self.value <= other.value)

    @primitiveNamed('primitiveInteger.comparison.greaterThan')
    def primitiveGreaterThan(self, other):
        return getBooleanValue(self.value > other.value)

    @primitiveNamed('primitiveInteger.comparison.greaterOrEqual')
    def primitiveGreaterOrEqual(self, other):
        return getBooleanValue(self.value >= other.value)

    @primitiveNamed('primitiveInteger.conversion.toString')
    def toString(self):
        return String(str(self.value))

    @primitiveNamed('primitiveInteger.conversion.toInteger')
    def asInteger(self):
        return Integer(self.value)

class PrimitiveFloatTypeValue(PrimitiveNumberTypeValue):
    @primitiveNamed('primitiveFloat.conversion.toString')
    def toString(self):
        return String(str(self.value))

    @primitiveNamed('primitiveFloat.conversion.toInteger')
    def asInteger(self):
        return Integer(self.value)

class PrimitiveTypeSchema(TypeSchema):
    def __init__(self, size, alignment):
        super().__init__()
        self.size = size
        self.alignment = alignment

    def getType(self):
        return getBasicTypeNamed('PrimitiveTypeSchema')

class PrimitiveNumberTypeSchema(PrimitiveTypeSchema):
    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNew:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)value :: self |}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return self.basicNewWithValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return self.primitiveNumberTypeValueClass()(valueType, self.normalizeValueToValidRange(initialValue))

    def primitiveNumberTypeValueClass(self):
        raise SubclassResponsibility()

    def normalizeValueToValidRange(self, value):
        return value

class PrimitiveIntegerTypeSchema(PrimitiveNumberTypeSchema):
    def __init__(self, size, alignment):
        super().__init__(size, alignment)
        self.memoryBits = size*8
        self.memoryBitMask = (1<<(self.memoryBits)) - 1

    def normalizeValueToValidRange(self, value):
        return int(value) & self.memoryBitMask

    def primitiveNumberTypeValueClass(self):
        return PrimitiveIntegerTypeValue

class PrimitiveUnsignedIntegerTypeSchema(PrimitiveIntegerTypeSchema):
    pass

class PrimitiveSignedIntegerTypeSchema(PrimitiveIntegerTypeSchema):
    def __init__(self, size, alignment):
        super().__init__(size, alignment)
        self.signBit = 1 << (self.memoryBits - 1)
        self.unsignedBitMask = self.memoryBitMask ^ self.signBit

    def normalizeValueToValidRange(self, value):
        intValue = int(value)
        return (intValue & self.unsignedBitMask) - (intValue & self.signBit)

class PrimitiveBooleanTypeSchema(PrimitiveIntegerTypeSchema):
    def normalizeValueToValidRange(self, value):
        if value == 0 or value == False:
            return 0
        else:
            return 1

    def primitiveNumberTypeValueClass(self):
        return PrimitiveBooleanTypeValue

class PrimitiveCharacterTypeSchema(PrimitiveIntegerTypeSchema):
    pass

class PrimitiveFloatTypeSchema(PrimitiveNumberTypeSchema):
    def normalizeValueToValidRange(self, value):
        return float(value)

    def primitiveNumberTypeValueClass(self):
        return PrimitiveFloatTypeValue

class SumTypeValue(TypedValue):
    def __init__(self, type, typeSelector, wrappedValue):
        self.type = type
        self.typeSelector = typeSelector
        self.wrappedValue = wrappedValue

    def asBooleanValue(self):
        if self.type.isTypeTheoryBoolean():
            return self.typeSelector.asInteger() == 1
        return super().asBooleanValue()

    def getType(self):
        return self.type
    
    def shallowCopy(self):
        return SumTypeValue(self.type, self.typeSelector, self.wrappedValue.shallowCopyValue())

    def defaultPrintString(self) -> str:
        return '%s(%s: %s)' % (repr(self.type), repr(self.typeSelector), repr(self.wrappedValue))

class SumTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        super().__init__()
        self.elementTypes = elementTypes

    def getType(self):
        return getBasicTypeNamed('SumTypeSchema')

    def isDefaultConstructible(self):
        return self.elementTypes[0].isDefaultConstructible()

    def buildPrimitiveMethodDictionary(self):
        self.methodDict[Symbol.intern('__typeSelector__')] = TypeSchemaPrimitiveMethod.makeFunction(self.getTypeSelector, '(SelfType) => Size')
        self.methodDict[Symbol.intern('get:')] = TypeSchemaPrimitiveMethod.makeFunction(self.getWithType, '{:(SelfType)self :(Type)expectedType :: expectedType |}')
        self.methodDict[Symbol.intern('is:')] = TypeSchemaPrimitiveMethod.makeFunction(self.isWithType, '{:(SelfType)self :(Type)expectedType :: Boolean |}')
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNew:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)initialValue :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNew:typeSelector:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithValueTypeSelector, '{:(SelfType)self :(AnyValue)initialValue :(Size)typeSelector :: self |}')
        return super().buildPrimitiveMethodDictionary()

    def getTypeSelector(self, sumValue):
        return sumValue.typeSelector

    def getWithType(self, sumValue, requiredType):
        requiredTypeIndex = self.elementTypes.index(requiredType)
        if sumValue.typeSelector.asInteger() != requiredTypeIndex:
            raise SumTypeNotMatched('Sum type value is not of the expected type (%s).' % repr(requiredType))
        return sumValue.wrappedValue

    def isWithType(self, sumValue, requiredType):
        requiredTypeIndex = self.elementTypes.index(requiredType)
        return getBooleanValue(sumValue.typeSelector.asInteger() == requiredTypeIndex)

    def basicNew(self, sumType):
        return SumTypeValue(sumType, getSizeValue(0), self.elementTypes[0].basicNew())

    def basicNewWithValue(self, sumType, value):
        if value.getType() is sumType:
            return value.shallowCopy()
        return self.coerceValueOfTypeIntoType(value, value.getType(), sumType)

    def basicNewWithValueTypeSelector(self, sumType, value, typeSelector):
        return SumTypeValue(sumType, typeSelector, value)

    def basicNewWithTypeTheoryBoolean(self, sumType, value):
        if value:
            return SumTypeValue(sumType, getSizeValue(1), self.elementTypes[1].basicNew())
        else:
            return SumTypeValue(sumType, getSizeValue(0), self.elementTypes[0].basicNew())

    def isTypeTheoryBoolean(self):
        return len(self.elementTypes) == 2 and self.elementTypes[0].hasTrivialTypeSchema() and self.elementTypes[1].hasTrivialTypeSchema()

    def canCoerceValueOfType(self, valueType):
        for elementType in self.elementTypes:
            if valueType.canBeCoercedToType(elementType):
                return True
        return super().canCoerceValueOfType(valueType)

    def coerceValueOfTypeIntoType(self, value, valueType, targetType):
        for i in range(len(self.elementTypes)):
            elementType = self.elementTypes[i]
            if valueType.canBeCoercedToType(elementType):
                return SumTypeValue(targetType, getSizeValue(i), value)
        return self.basicNewWithValue(targetType, value)

    @primitiveNamed('sumTypeSchema.containsType')
    def primitiveContainsType(self, elementTypeToCheck):
        return getBooleanValue(elementTypeToCheck in self.elementTypes)

    @primitiveNamed('sumTypeSchema.getTypeSelectorIndexFor')
    def primitiveGetTypeSelectorIndexFor(self, elementTypeToCheck):
        return getSizeValue(self.elementTypes.index(elementTypeToCheck))

class ProductTypeValue(TypedValue):
    def __init__(self, type, elements):
        self.type = type
        self.elements = elements

    def shallowCopy(self):
        return ProductTypeValue(self.type, list(map(lambda el: el.shallowCopyValue(), self.elements)))

    def getType(self):
        return self.type

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        return self.elements[slotIndex]

    def getSlotNamed(self, slotName):
        return self.elements[self.type.schema.getIndexOfSlotNamed(slotName)]

    def setSlotWithIndexAndName(self, slotIndex, slotName, value):
        expectedType = self.type.schema.getTypeOfSlotIndex(slotIndex)
        coercedValue = expectedType.coerceValue(coerceNoneToNil(value))
        self.elements[slotIndex] = coercedValue
        return coercedValue

    def defaultPrintString(self) -> str:
        result = str(self.type) + '('
        isFirst = True
        for element in self.elements:
            if isFirst:
                isFirst = False
            else:
                result += ', '
            result += repr(element)
        result += ')'
        return result

    def __getitem__(self, index):
        return self.elements[index.asInteger()]

    def __setitem__(self, index, value):
        expectedType = self.type.schema.getTypeOfSlotIndex(index)
        coercedValue = expectedType.coerceValue(coerceNoneToNil(value))
        self.elements[index.asInteger()] = coercedValue
        return coercedValue

    def __iter__(self):
        if self.type.hasArraySliceFlag:
            return iter(extractArraySliceElements(self))
        return iter(self.elements)

class ProductTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        super().__init__()
        self.elementTypes = elementTypes
        self.isDefaultConstructibleCache = None

    def getType(self):
        return getBasicTypeNamed('ProductTypeSchema')

    def getTypeOfSlotIndex(self, slotIndex):
        return self.elementTypes[slotIndex]

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self|}')
        self.metaTypeMethodDict[Symbol.intern('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)sequentialSlots :: self|}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, productType):
        productType.evaluatePendingBodyExpressions()
        self.finishPendingPrimitiveMethods()
        return ProductTypeValue(productType, list(map(lambda t: t.basicNew(), self.elementTypes)))

    def isDefaultConstructible(self):
        if self.isDefaultConstructibleCache is None:
            ## Set temporary result to False with the objective of avoiding cycles.
            self.isDefaultConstructibleCache = False
            for type in self.elementTypes:
                if not type.isDefaultConstructible():
                    return False
            self.isDefaultConstructibleCache = True
        return self.isDefaultConstructibleCache

    def basicNewWithSequentialSlots(self, productType, slots):
        if len(slots) != len(self.elementTypes):
            raise MissingSlotsForInstancingType()
        return ProductTypeValue(productType, list(slots))

class RecordTypeSchema(ProductTypeSchema):
    def __init__(self, slots, supertypeSchema = None, packed = False):
        self.slots = []
        super().__init__([])
        self.supertypeSchema = supertypeSchema
        self.packed = packed
        self.definePublicSlots(slots)

    def setSupertypeSchema(self, newSupertypeSchema):
        self.supertypeSchema = newSupertypeSchema
        self.hasPendingSlotLayoutComputation = True
        self.computeSlotsLayout()

    def definePublicSlots(self, slots):
        self.slots = list(slots)
        self.hasPendingSlotLayoutComputation = True
        self.computeSlotsLayout()

    @primitiveNamed('recordTypeSchema.addSlotWithTypeAndName')
    def addSlotWithTypeAndName(self, slotType, slotName):
        self.slots.append(Association(slotName, slotType))
        self.hasPendingSlotLayoutComputation = True
        return getVoidValue()

    def finishPendingPrimitiveMethods(self):
        super().finishPendingPrimitiveMethods()
        self.computeSlotsLayout()

    def computeSlotsLayout(self):
        if not self.hasPendingSlotLayoutComputation:
            return
        self.hasPendingSlotLayoutComputation = False

        self.startSlotIndex = 0
        self.allSlots = list(self.slots)
        if self.supertypeSchema is not None:
            self.supertypeSchema.computeSlotsLayout()
            self.startSlotIndex = len(self.supertypeSchema.allSlots)
            self.allSlots = self.supertypeSchema.allSlots + self.allSlots
        self.slotNameDictionary = {}
        self.slotNameTable = list(map(lambda s: s.key, self.allSlots))
        self.elementTypes = list(map(lambda s: s.value, self.allSlots))

        slotIndex = 0
        for assoc in self.allSlots:
            slotName = assoc.key
            self.slotNameDictionary[slotName] = slotIndex
            slotIndex += 1
        self.buildPrimitiveMethodDictionary()
        if self.ownerType is not None:
            self.installedInType(self.ownerType)

    def getType(self):
        return getBasicTypeNamed('RecordTypeSchema')

    def getIndexOfSlotNamed(self, slotName):
        return self.slotNameDictionary[slotName]

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)slots :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNewWithNamedSlots:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithNamedSlots, '{:(SelfType)self :(AnyValue)slots :: self |}')
        for slotIndex in range(len(self.slots)):
            slotAssociation = self.slots[slotIndex]
            slotName = slotAssociation.key
            getterName = Symbol.intern(slotName)
            setterName = Symbol.intern(slotName + ':')
            slotType = slotAssociation.getValue()
            self.methodDict[getterName] = FunctionTypeValue(None, bootstrapImplementation = RecordTypeGetterPrimitiveMethod(getterName, getterName, self.startSlotIndex + slotIndex, slotType), functionTypeSpec = (('SelfType'), slotType))
            self.methodDict[setterName] = FunctionTypeValue(None, bootstrapImplementation = RecordTypeSetterPrimitiveMethod(setterName, getterName, self.startSlotIndex + slotIndex, slotType), functionTypeSpec = (('SelfType', slotType), slotType))
        return super().buildPrimitiveMethodDictionary()

    def basicNewWithNamedSlots(self, recordType, namedSlots):
        recordType.evaluatePendingBodyExpressions()
        self.finishPendingPrimitiveMethods()
        linearSlots = [None,] * len(self.allSlots)
        for assoc in namedSlots:
            slotIndex = self.slotNameDictionary[assoc.getKey()]
            expectedSlotType = self.elementTypes[slotIndex]
            linearSlots[slotIndex] = expectedSlotType.coerceValue(coerceNoneToNil(assoc.getValue()))

        for i in range(len(linearSlots)):
            if linearSlots[i] is None:
                expectedSlotType = self.elementTypes[i]
                if not expectedSlotType.isDefaultConstructible():
                    raise MissingSlotsForInstancingType('MissingSlotsForInstancingType %s' % repr(recordType))
                linearSlots[i] = expectedSlotType.basicNew()

        return self.basicNewWithSequentialSlots(recordType, linearSlots)

    def basicNewWithArraySliceElements(self, recordType, elements):
        recordType.evaluatePendingBodyExpressions()
        self.finishPendingPrimitiveMethods()
        assert len(self.elementTypes) == 2 or len(self.elementTypes) == 3
        if len(self.elementTypes) == 2:
            return self.basicNewWithSequentialSlots(recordType, [
                self.elementTypes[0].basicNewWithValue(elements),
                self.elementTypes[1].basicNewWithValue(len(elements))
            ])
        return self.basicNewWithSequentialSlots(recordType, [
            self.elementTypes[0].basicNewWithValue(elements),
            self.elementTypes[1].basicNewWithValue(len(elements)),
            self.elementTypes[2].basicNewWithValue(elements),
        ])

class ArrayTypeValue(ProductTypeValue):
    pass

class ArrayTypeSchema(TypeSchema):
    def __init__(self, elementType, bounds):
        self.elementType = elementType
        self.bounds = bounds.asInteger()
        super().__init__()

    def getType(self):
        return getBasicTypeNamed('ArrayTypeSchema')

    def getTypeOfSlotIndex(self, slotIndex):
        return self.elementType

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)slots :: self |}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return ArrayTypeValue(valueType, list(map(lambda x: self.elementType.basicNew(), [None] * self.bounds)))

    def basicNewWithSequentialSlots(self, valueType, slots):
        if len(slots) != self.bounds:
            raise InterpreterError('Array construction element count mismatch.')
        
        return ArrayTypeValue(valueType, list(map(lambda x: x.shallowCopyValue(), slots)))

    def hasDirectCoercionToPointerOf(self, baseType, addressSpace):
        return self.elementType == baseType

    def makeDirectPointerOfValueTo(self, value, valueType, targetType):
        return PointerTypeValue(targetType, value, 0)

class PointerTypeValue(TypedValue):
    def __init__(self, type, value, baseIndex = 0):
        self.type = type
        self.value = value
        self.baseIndex = baseIndex

    def shallowCopy(self):
        return self

    def getType(self):
        return self.type

    def defaultPrintString(self):
        if self.value is None:
            return str(self.type) + '(nil)'
        return '%s(0x%x:%d)' % (str(self.type), self.value.identityHash(), self.baseIndex)

    def __getitem__(self, index):
        return self.value[Integer(index.asInteger() + self.baseIndex)]

    def __setitem__(self, index, value):
        self.value[Integer(index.asInteger() + self.baseIndex)] = value

    def asPointerTypeValue(self, pointerType):
        return PointerTypeValue(pointerType, self.value, self.baseIndex)

    def asTemporaryReferenceTypeValue(self, temporaryReferenceType):
        return TemporaryReferenceTypeValue(temporaryReferenceType, self.value, self.baseIndex)

    def asReferenceTypeValue(self, referenceType):
        return ReferenceTypeValue(referenceType, self.value, self.baseIndex)

class ReferenceTypeValue(PointerTypeValue):
    pass

class TemporaryReferenceTypeValue(PointerTypeValue):
    pass

class PointerLikeTypeSchema(TypeSchema):
    def __init__(self, elementType, addressSpace):
        self.elementType = elementType
        self.addressSpace = addressSpace
        super().__init__()

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

class PointerTypeSchema(PointerLikeTypeSchema):
    def getType(self):
        return getBasicTypeNamed('PointerTypeSchema')

    def hasDirectCoercionToPointerOf(self, baseType, addressSpace):
        return self.elementType == baseType

    def makeDirectPointerOfValueTo(self, value, valueType, targetType):
        return value.asPointerTypeValue(targetType)

    def canCoerceValueOfType(self, valueType):
        if valueType.schema.hasDirectCoercionToPointerOf(self.elementType, self.addressSpace):
            return True

        return super().canCoerceValueOfType(valueType)

    def coerceValueOfTypeIntoType(self, value, valueType, targetType):
        if valueType.schema.hasDirectCoercionToPointerOf(self.elementType, self.addressSpace):
            return valueType.schema.makeDirectPointerOfValueTo(value, valueType, targetType)

        return super().coerceValueOfTypeIntoType(value, valueType, targetType)

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol.intern('basicNew')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNew, '{:(SelfType)self :: self |}')
        self.metaTypeMethodDict[Symbol.intern('basicNew:')] = TypeSchemaPrimitiveMethod.makeFunction(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)value :: self |}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return PointerTypeValue(valueType, None)

    def basicNewWithValue(self, valueType, initialValue):
        return PointerTypeValue(valueType, initialValue)

class ReferenceTypeSchema(PointerLikeTypeSchema):
    def getType(self):
        return getBasicTypeNamed('ReferenceTypeSchema')

    def canCoerceValueOfType(self, valueType):
        if valueType.schema.hasDirectCoercionToReferenceOf(self.elementType, self.addressSpace):
            return True

        return super().canCoerceValueOfType(valueType)

    def basicNew(self, valueType):
        return ReferenceTypeValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return ReferenceTypeValue(valueType, initialValue)

class TemporaryReferenceTypeSchema(TypeSchema):
    def __init__(self, elementType, addressSpace):
        self.elementType = elementType
        self.addressSpace = addressSpace
        super().__init__()

    def getType(self):
        return getBasicTypeNamed('TemporaryReferenceTypeSchema')

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

    def canCoerceValueOfType(self, valueType):
        if valueType.schema.hasDirectCoercionToTemporaryReferenceOfType(self.elementType, self.addressSpace):
            return True

        return super().canCoerceValueOfType(valueType)

    def basicAt(self, value, index):
        return value[index.asInteger()]

    def basicNew(self, valueType):
        return TemporaryReferenceTypeValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return TemporaryReferenceTypeValue(valueType, initialValue)

class UnionTypeSchema(RecordTypeSchema):
    def getType(self):
        return getBasicTypeNamed('UnionTypeSchema')

class GCClassTypeSchema(RecordTypeSchema):
    def getType(self):
        return getBasicTypeNamed('GCClassTypeSchema')

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

    def supportsDynamicDispatch(self):
        return True

class MethodDictionary(TypedValue):
    def getType(self):
        return getBasicTypeNamed('MethodDictionary')

class SymbolTable(TypedValue):
    def __init__(self):
        super().__init__()
        self.table = {}

    def getType(self):
        return getBasicTypeNamed('SymbolTable')

    def lookupSymbol(self, symbol):
        return self.table.get(symbol, None)

    def setSymbolValueBinding(self, symbol, value):
        self.table[symbol] = value.asSymbolBindingWithName(symbol)

    def setSymbolImmutableValue(self, symbol, value):
        self.table[symbol] = SymbolValueBinding(symbol, value)

    def setSymbolBinding(self, symbol, binding):
        self.table[symbol] = binding

    @primitiveNamed('symbolTable.lookupSymbol')
    def primitiveLookupSymbol(self, symbol):
        return self.lookupSymbol(symbol)

    @primitiveNamed('symbolTable.setSymbolImmutableValue')
    def primitiveSetSymbolImmutableValue(self, symbol, value):
        self.setSymbolImmutableValue(symbol, value)
        return getVoidValue()

    @primitiveNamed('symbolTable.setSymbolValueBinding')
    def primitiveSetSymbolValueBinding(self, symbol, value):
        self.setSymbolValueBinding(symbol, value)
        return getVoidValue()

    @primitiveNamed('symbolTable.setSymbolBinding')
    def primitiveSetSymbolBinding(self, symbol, binding):
        self.setSymbolBinding(symbol, binding)
        return getVoidValue()

class ProgramEntity(TypedValue):
    def __init__(self, parent = None, name = None):
        self.parent = parent
        self.name = name

    def getType(self):
        return getBasicTypeNamed('ProgramEntity')

    def setSlotWithIndexAndName(self, slotIndex, slotName, value):
        if slotName == 'parent':
            self.parent = value
            return self.parent
        elif slotName == 'name':
            self.name = value
            return self.parent
        return super().setSlotWithIndexAndName(slotIndex, slotName, value)

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'parent':
            return self.parent
        elif slotName == 'name':
            return self.name
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def lookupScopeSymbol(self, selector):
        return None

    def lookupPublicSymbol(self, selector):
        return None

    def performWithArguments(self, machine, selector, arguments):
        if len(arguments) == 0:
            boundSymbol = self.lookupPublicSymbol(selector)
            if boundSymbol is not None:
                return boundSymbol.getSymbolBindingReferenceValue()
        return super().performWithArguments(machine, selector, arguments)

class Namespace(ProgramEntity):
    def __init__(self, parent = None, name = None):
        super().__init__(parent = None, name = None)
        self.symbolTable = SymbolTable()

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'symbolTable':
            return self.symbolTable
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def lookupScopeSymbol(self, selector):
        return self.symbolTable.lookupSymbol(selector)

    def lookupPublicSymbol(self, selector):
        return self.symbolTable.lookupSymbol(selector)

    def getType(self):
        return getBasicTypeNamed('Namespace')

    def setSymbolValueBinding(self, symbol, value):
        self.symbolTable.setSymbolValueBinding(symbol, value)
        value.onGlobalBindingWithSymbolAdded(symbol)

    @primitiveNamed('namespace.getOrCreateChildNamespaceNamed')
    def getOrCreateChildNamespaceNamed(self, childName):
        childNamespace = self.symbolTable.lookupSymbol(childName)
        if childNamespace is None:
            childNamespace = Namespace(parent = self, name = childName)
            self.symbolTable.setSymbolValueBinding(childName, childNamespace)
        else:
            childNamespace = childNamespace.getSymbolBindingReferenceValue()
        return childNamespace

class BehaviorType(ProgramEntity, TypeInterface):
    def __init__(self, name = None, supertype = None, traits = [], schema = None, macroMethodDict = {}, methodDict = {}, macroFallbackMethodDict = {}):
        super().__init__(name = None)
        self.symbolTable = SymbolTable()
        self.macroMethodDict = dict(macroMethodDict)
        self.methodDict = dict(methodDict)
        self.macroFallbackMethodDict = dict(macroFallbackMethodDict)
        self.implicitConversionMethods = []
        self.explicitConversionMethods = []
        self.implicitConstructionMethods = []
        self.explicitConstructionMethods = []
        self.supertype = supertype
        self.traits = list(traits)
        self.installImplicitTraits()
        self.allTraits = None
        self.directTraits = None
        self.schema = schema
        self.schema.installedInType(self)
        self.type = None

        self.typeFlags = []
        self.hasAnyValueFlag = False
        self.hasArraySliceFlag = False

        self.constructionTemplate = None
        self.constructionTemplateArguments = None

        self.pendingSupertypeExpression = []
        self.pendingTraitExpressions = []
        self.pendingBodyExpressions = []

    def installImplicitTraits(self):
        if Symbol('AnyValueTrait') in BasicTypeEnvironment:
            self.traits.append(BasicTypeEnvironment[Symbol('AnyValueTrait')])

    def shallowCopyValue(self):
        return self

    def canBeCoercedToType(self, targetType):
        return self.isSubtypeOf(targetType)

    def coerceValue(self, value):
        if self.hasAnyValueFlag:
            return value.canonicalizeForAnyValue()

        valueType = value.getType()
        if valueType.isSubtypeOf(self):
            return value

        if self.schema.canCoerceValueOfType(valueType):
            return self.schema.coerceValueOfTypeIntoType(value, valueType, self)

        return super().coerceValue(value)

    def lookupScopeSymbol(self, selector):
        return self.symbolTable.lookupSymbol(selector)

    def lookupPublicSymbol(self, selector):
        return self.symbolTable.lookupSymbol(selector)

    @primitiveNamed('type.addPendingSupertypeExpression')
    def addPendingSupertypeExpression(self, supertypeExpression):
        self.pendingSupertypeExpression.append(supertypeExpression)
        EvaluationMachine.getActive().addPendingEvaluation(lambda: self.evaluatePendingSupertypeExpressions())
        return getVoidValue()

    def evaluatePendingSupertypeExpressions(self):
        while len(self.pendingSupertypeExpression) > 0:
            expressionToEvaluate = self.pendingSupertypeExpression.pop(0)
            self.setSupertype(expressionToEvaluate())

    @primitiveNamed('type.addPendingTraitExpression')
    def addPendingTraitExpression(self, traitExpression):
        self.pendingTraitExpressions.append(traitExpression)
        EvaluationMachine.getActive().addPendingEvaluation(lambda: self.evaluatePendingTraitExpressions())
        return getVoidValue()

    def evaluatePendingTraitExpressions(self):
        self.evaluatePendingSupertypeExpressions()
        while len(self.pendingTraitExpressions) > 0:
            self.addTrait(self.pendingTraitExpressions.pop(0)())

    @primitiveNamed('type.doesImplementTrait')
    def primitiveDoesImplementTrait(self, trait):
        return getBooleanValue(trait in self.getAllTraits())

    @primitiveNamed('type.addPendingBodyExpression')
    def addPendingBodyExpression(self, bodyExpression):
        self.pendingBodyExpressions.append(bodyExpression)
        EvaluationMachine.getActive().addPendingEvaluation(lambda: self.evaluatePendingBodyExpressions())
        return getVoidValue()

    def evaluatePendingBodyExpressions(self):
        self.evaluatePendingTraitExpressions()
        while len(self.pendingBodyExpressions) > 0:
            self.pendingBodyExpressions.pop(0)()

    def setSupertype(self, newSupertype):
        self.supertype = newSupertype
        if self.type is not None:
            if self.supertype is not None:
                self.type.setSupertype(self.supertype.getType())
            else:
                self.type.setSupertype(self.getMetaTypeRoot())
        if newSupertype is not None:
            self.schema.setSupertypeSchema(newSupertype.schema)
        else:
            self.schema.setSupertypeSchema(None)
        self.invalidateTraitCache()

    def addTrait(self, newTrait):
        if newTrait not in self.traits:
            self.traits.append(newTrait)
            self.invalidateTraitCache()

    def invalidateTraitCache(self):
        self.allTraits = None
        self.directTraits = None

    def getSupertype(self):
        self.evaluatePendingSupertypeExpressions()
        return self.supertype

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'supertype':
            return self.getSupertype()
        elif slotName == 'schema':
            return self.schema
        elif slotName == 'symbolTable':
            return self.symbolTable
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def isSubtypeOf(self, expectedSuperType):
        if self is expectedSuperType:
            return True;
        if self.getSupertype() is not None:
            return self.getSupertype().isSubtypeOf(expectedSuperType)
        return False
        
    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def setConstructionTemplateAndArguments(self, template, arguments):
        self.constructionTemplate = template
        self.constructionTemplateArguments = arguments

    def getAllTraits(self):
        if self.allTraits is None:
            self.allTraits = []
            if self.supertype is not None:
                self.allTraits = list(self.supertype.getAllTraits())
            exclusionSet = set(self.allTraits)
            for trait in self.traits:
                if trait not in exclusionSet:
                    self.allTraits.append(trait)
                    exclusionSet.add(trait)
                    for indirectTrait in trait.getAllTraits():
                        if indirectTrait not in exclusionSet:
                            self.allTraits.append(indirectTrait)
                            exclusionSet.add(indirectTrait)

        return self.allTraits

    def getDirectTraits(self):
        if self.directTraits is None:
            if self.supertype is not None:
                exclusionSet = set(self.supertype.getAllTraits())
                self.directTraits = []
                for trait in self.getAllTraits():
                    if trait not in exclusionSet:
                        self.directTraits.append(trait)
            else:
                self.directTraits = self.getAllTraits()
        return self.directTraits

    def lookupLocalSelector(self, selector):
        self.evaluatePendingBodyExpressions()
        found = self.methodDict.get(selector, None)
        if found is not None:
            return found

        ## Check a schema inserted primitive.
        found = self.schema.lookupPrimitiveWithSelector(selector)
        if found is not None:
            return found
        return None

    def lookupLocalMacroSelector(self, selector):
        self.evaluatePendingBodyExpressions()
        found = self.macroMethodDict.get(selector, None)
        if found is not None:
            return found
        return None

    def lookupLocalMacroFallbackSelector(self, selector):
        self.evaluatePendingBodyExpressions()
        found = self.macroFallbackMethodDict.get(selector, None)
        if found is not None:
            return found
        return None

    def lookupMacroSelector(self, selector):
        ## Check in the local method dictionary.
        found = self.lookupLocalMacroSelector(selector)
        if found is not None:
            return found

        ## Find in a direct trait.
        for trait in self.getDirectTraits():
            found = trait.lookupLocalMacroSelector(selector)
            if found is not None:
                return found

        ##  Find in the supertype.
        if self.supertype is not None:
            return self.supertype.lookupMacroSelector(selector)
        return None

    def lookupSelector(self, selector):
        ## Check in the local method dictionary.
        found = self.lookupLocalSelector(selector)
        if found is not None:
            return found

        ## Find in a direct trait.
        for trait in self.getDirectTraits():
            found = trait.lookupLocalSelector(selector)
            if found is not None:
                return found

        ##  Find in the supertype.
        if self.supertype is not None:
            return self.supertype.lookupSelector(selector)
        return None

    def lookupMacroFallbackSelector(self, selector):
        ## Check in the local method dictionary.
        found = self.lookupLocalMacroFallbackSelector(selector)
        if found is not None:
            return found

        ## Find in a direct trait.
        for trait in self.getDirectTraits():
            found = trait.lookupLocalMacroFallbackSelector(selector)
            if found is not None:
                return found

        ##  Find in the supertype.
        if self.supertype is not None:
            return self.supertype.lookupMacroFallbackSelector(selector)
        return None

    def runWithIn(self, machine, selector, arguments, receiver):
        method = self.lookupSelector(selector)
        if method is None:
            raise DoesNotUnderstand('%s does not understand message %s' % (str(receiver), repr(selector)))
        return method.runWithIn(machine, selector, arguments, receiver)

    def addMethodWithSelector(self, method, selector):
        self.methodDict[selector] = method
        self.registerInstalledMethod(method)

    def addMacroMethodWithSelector(self, method, selector):
        self.macroMethodDict[selector] = method
        self.registerInstalledMethod(method)

    def addMacroFallbackMethodWithSelector(self, method, selector):
        self.macroMethodDict[selector] = method
        self.registerInstalledMethod(method)

    def registerInstalledMethod(self, method):
        method.installedInType(self)

        if method.isConversionMethod():
            if method.isExplicitMethod():
                self.explicitConversionMethods.append(method)
            else:
                self.implicitConversionMethods.append(method)
        if method.isConstructionMethod():
            if method.isExplicitMethod():
                self.implicitConstructionMethods.append(method)
            else:
                self.explicitConstructionMethods.append(method)

    def setSymbolValueBinding(self, symbol, value):
        self.symbolTable.setSymbolValueBinding(symbol, value)
        value.onGlobalBindingWithSymbolAdded(symbol)

    @primitiveNamed('type.withSelectorAddMethod')
    def withSelectorAddMethod(self, selector, method):
        self.addMethodWithSelector(method, selector)

    @primitiveNamed('type.withSelectorAddMacroMethod')
    def withSelectorAddMacroMethod(self, selector, method):
        self.addMacroMethodWithSelector(method, selector)

    @primitiveNamed('type.withSelectorAddMacroFallbackMethod')
    def withSelectorAddMacroFallbackMethod(self, selector, method):
        self.addMacroFallbackMethodWithSelector(method, selector)

    @primitiveNamed('type.addFlag')
    def addTypeFlag(self, flagName):
        self.typeFlags.append(flagName)
        if flagName == 'anyValue':
            self.hasAnyValueFlag = True
        elif flagName == 'arraySlice': 
            self.hasArraySliceFlag = True

    @primitiveNamed('type.hasTypeFlag')
    def hasTypeFlag(self, typeFlag):
        return getBooleanValue(typeFlag in self.typeFlags)

    def addMethodsWithSelectors(self, methodsWithSelector):
        for method, selector in methodsWithSelector:
            self.addMethodWithSelector(method, Symbol.intern(selector))

    def addPrimitiveMethodsWithSelectors(self, methodsWithSelector):
        for method, selector, functionTypeSpec in methodsWithSelector:
            self.addMethodWithSelector(PrimitiveMethod.makeFunction(method, functionTypeSpec), Symbol.intern(selector))

    def getName(self):
        if self.name is not None:
            return self.name
        return 'a ' + self.getType().getDirectName()

    def getDirectName(self):
        return self.name

    def getType(self):
        if self.type is None:
            self.type = self.createMetaType()
        return self.type

    def getMetaTypeRoot(self):
        return getBasicTypeNamed(Symbol.intern('SimpleType'))

    def createMetaType(self):
        typeSupertype = None
        if self.getSupertype() is not None:
            typeSupertype = self.getSupertype().getType()
        else:
            typeSupertype = self.getMetaTypeRoot()
        return MetaType(thisType = self, supertype = typeSupertype, schema = OpaqueTypeSchema())

    @primitiveNamed('type.conversion.toString')
    def defaultToString(self):
        return String(self.getName())

    @primitiveNamed('type.conversion.printString')
    def defaultPrintString(self):
        return String(self.getName())

    def addTypeRootMethods(self):
        cls = self.__class__
        self.addPrimitiveMethodsWithSelectors([
            (cls.withSelectorAddMethod, 'withSelector:addMethod:', '(AnyValue -- AnyValue) => AnyValue'),
            (cls.withSelectorAddMacroMethod, 'withSelector:addMacroMethod:', '(AnyValue -- AnyValue) => AnyValue'),
            (cls.withSelectorAddMacroFallbackMethod, 'withSelector:addMacroFallbackMethod:', '(AnyValue -- AnyValue) => AnyValue'),
            (cls.addTypeFlag, 'addTypeFlag:', 'AnyValue => AnyValue'),
            (cls.definePublicSlots, 'definePublicSlots:', '(SelfType -- AnyValue) => Type'),
        ])

    @primitiveNamed('type.definePublicSlots')
    def definePublicSlots(self, slotDefinitions):
        return self.schema.definePublicSlots(slotDefinitions)

    def asArrayType(self):
        return self

    def basicNew(self):
        return self.schema.basicNew(self)

    def basicNewWithValue(self, value):
        return self.schema.basicNewWithValue(self, value)

    def basicNewWithSequentialSlots(self, slots):
        return self.schema.basicNewWithSequentialSlots(self, slots)

    def basicNewWithNamedSlots(self, namedSlots):
        return self.schema.basicNewWithNamedSlots(self, namedSlots)

    def basicNewWithArraySliceElements(self, elements):
        return self.schema.basicNewWithArraySliceElements(self, elements)

    def basicNewWithTypeTheoryBoolean(self, value):
        return self.schema.basicNewWithTypeTheoryBoolean(self, value)

    def hasTrivialTypeSchema(self):
        return self.schema.isTrivialTypeSchema()

    def isTypeTheoryBoolean(self):
        return self.schema.isTypeTheoryBoolean()

    def isDefaultConstructible(self):
        return self.schema.isDefaultConstructible()

    def supportsDynamicDispatch(self):
        return self.schema.supportsDynamicDispatch()

    def asCanonicalTypeForDependentType(self):
        return self

class BehaviorTypedObject(TypedValue):
    def __init__(self) -> None:
        super().__init__()
        self.behaviorType = BehaviorType(schema = TrivialTypeSchema())
        self.__class__.initializeBehaviorType(self.behaviorType)

    def getType(self):
        return self.behaviorType

    @classmethod
    def initializeBehaviorType(cls, type):
        pass

class Trait(BehaviorType):
    pass

class MetaType(BehaviorType):
    def __init__(self, thisType=None, name=None, supertype=None, traits=[], schema=None, methodDict={}):
        super().__init__(name, supertype, traits, schema, methodDict)
        self.thisType = thisType

    def asCanonicalTypeForDependentTypeArgument(self):
        if self.thisType is not None:
            return self.thisType
        return super().asCanonicalTypeForDependentTypeArgument()

    def lookupLocalSelector(self, selector):
        found = self.methodDict.get(selector, None)
        if found is not None:
            return found

        ## Check a schema inserted primitive.
        found = self.schema.lookupPrimitiveWithSelector(selector)
        if found is not None:
            return found

        ## Check a schema inserted meta primitive.
        if self.thisType is not None:
            found = self.thisType.schema.lookupMetaTypePrimitiveWithSelector(selector)
            if found is not None:
                return found
        return None

    def getMetaTypeRoot(self):
        return None

    def getDirectName(self):
        return 'MetaType'

    def getName(self):
        if self.thisType is not None:
            return String(self.thisType.getName() + ' __type__')
        return super().getName()

class SimpleType(BehaviorType):
    pass

class AbstractFunctionTypeArgument:
    def __init__(self, name, typeExpression):
        self.name = name
        self.typeExpression = typeExpression

    def evaluateCanonicalFormInEnvironment(self, environment):
        if self.typeExpression is None:
            argumentType = getBasicTypeNamed('AnyValue')
        else:
            argumentType = self.typeExpression.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)

        if self.name is not None:
            environment.setSymbolImmutableValue(self.name, argumentType.asCanonicalTypeForDependentTypeArgument())
        return argumentType

    def isForAllArgumentExpression(self):
        raise SubclassResponsibility()

class FunctionTypeForAllArgumentExpression(AbstractFunctionTypeArgument):
    def evaluateInEnvironment(self, environment):
        if self.typeExpression is None:
            placeholderType = getBasicTypeNamed('AnyValue')
        else:
            placeholderType = self.typeExpression.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)

        placeholder = ForAllPlaceholderBinding(self.name, placeholderType)
        if self.name is not None:
            environment.setSymbolValueBinding(self.name, placeholder)

    def isForAllArgumentExpression(self):
        return True

    def __repr__(self):
        if self.typeExpression is None:
            return ':*' + self.name
        else:
            return ':*(' + self.typeExpression.formatAST() + ')' + self.name

class FunctionTypeArgumentExpression(AbstractFunctionTypeArgument):
    def isForAllArgumentExpression(self):
        return False

    def evaluateSignatureInEnvironmentWithAnalyzedType(self, evaluationEnvironment, argumentAnalyzedType):
        canonicalType = argumentAnalyzedType.asCanonicalTypeForDependentTypeArgument()
        if self.name is not None:
            evaluationEnvironment.setSymbolValueBinding(self.name, canonicalType)
        return canonicalType

    def evaluateInEnvironment(self, environment):
        if self.typeExpression is None:
            return getBasicTypeNamed('AnyValue')
        else:
            return self.typeExpression.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)

    def __repr__(self):
        if self.typeExpression is None:
            return ':' + self.name
        else:
            return ':(' + self.typeExpression.formatAST() + ')' + self.name

class FunctionTypeResult:
    def __init__(self, expression):
        self.expression = expression

    def evaluateCanonicalFormInEnvironment(self, environment):
        if self.expression is None:
            return getBasicTypeNamed('AnyValue')
        else:
            return self.expression.evaluateWithEnvironment(EvaluationMachine.getActive(), environment).asCanonicalTypeForDependentType()

    def evaluateInEnvironment(self, environment):
        if self.expression is None:
            return getBasicTypeNamed('AnyValue')
        else:
            return self.expression.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)

    def __repr__(self):
        return self.expression.formatAST()

SimpleFunctionMemoizationTable = {}

class FunctionSignatureAnalyzer(TypedValue):
    def __init__(self, functionType) -> None:
        super().__init__()
        self.functionType = functionType

    def getType(self):
        return getSemanticAnalysisType('FunctionSignatureAnalyzer')

    @primitiveNamed('functionSignatureAnalyzer.hasPendingArguments')
    def primitiveHasPendingArguments(self):
        return self.hasPendingArguments()

    @primitiveNamed('functionSignatureAnalyzer.evaluateNextSignatureType')
    def primitiveEvaluateNextSignatureType(self):
        return self.evaluateNextSignatureType()

    @primitiveNamed('functionSignatureAnalyzer.advanceArgument')
    def primitiveAdvanceArgumentWithAnalyzedType(self, analyzedType):
        self.advanceArgumentWithAnalyzedType(analyzedType)
        return getBasicTypeNamed('Void').basicNew()

    @primitiveNamed('functionSignatureAnalyzer.computeResultType')
    def primitiveComputeResultType(self):
        return self.computeResultType()

class DependentFunctionSignatureAnalyzer(FunctionSignatureAnalyzer):
    def __init__(self, functionType):
        super().__init__(functionType)
        self.evaluationEnvironment = functionType.dependentDefinitionEnvironment.makeChildLexicalScope()
        self.currentArgumentIndex = 0
        self.currentDependentArgumentIndex = 0
        self.evaluatedSignatures = []

    def hasPendingArguments(self):
        return getBooleanValue(self.currentArgumentIndex < self.functionType.argumentCount)

    def evaluateNextSignatureType(self):
        while self.currentDependentArgumentIndex < len(self.functionType.dependentDefinitionArguments):
            argumentDefinition = self.functionType.dependentDefinitionArguments[self.currentDependentArgumentIndex]
            if argumentDefinition.isForAllArgumentExpression():
                self.evaluatedSignatures.append(argumentDefinition.evaluateInEnvironment(self.evaluationEnvironment))
                self.currentDependentArgumentIndex += 1
            else:
                self.lastArgumentEvaluationType = argumentDefinition.evaluateInEnvironment(self.evaluationEnvironment)
                return self.lastArgumentEvaluationType

        raise Exception("Failed to evaluate next dependent argument signature")

    def advanceArgumentWithAnalyzedType(self, analyzedType):
        argumentDefinition = self.functionType.dependentDefinitionArguments[self.currentDependentArgumentIndex]
        self.evaluatedSignatures.append(argumentDefinition.evaluateSignatureInEnvironmentWithAnalyzedType(self.evaluationEnvironment, analyzedType))

        self.currentArgumentIndex += 1
        self.currentDependentArgumentIndex += 1

    def computeResultType(self):
        if self.functionType.dependentDefinitionResultType is None:
            return getBasicTypeNamed('AnyValue')

        if self.hasPendingArguments().asBooleanValue():
            return getBasicTypeNamed('CompilationError')

        return self.functionType.dependentDefinitionResultType.evaluateInEnvironment(self.evaluationEnvironment)

class SimpleFunctionSignatureAnalyzer(FunctionSignatureAnalyzer):
    def __init__(self, functionType):
        super().__init__(functionType)
        self.currentArgumentIndex = 0
    
    def hasPendingArguments(self):
        return getBooleanValue(self.currentArgumentIndex < self.functionType.argumentCount)

    def evaluateNextSignatureType(self):
        return self.functionType.canonicalArgumentTypes[self.currentArgumentIndex]

    def advanceArgumentWithAnalyzedType(self, analyzedType):
        self.currentArgumentIndex += 1

    def computeResultType(self):
        if self.hasPendingArguments().asBooleanValue():
            return getBasicTypeNamed('CompilationError')
        return self.functionType.canonicalResultType

class AbstractMemoizedFunctionTypeValue(FunctionTypeValue):
    def __init__(self, baseFunctionTypeValue):
        super().__init__(baseFunctionTypeValue.type, bootstrapImplementation = baseFunctionTypeValue.bootstrapImplementation, implementation = baseFunctionTypeValue.implementation)
        self.memoizationTable = {}

    def evaluateWithArguments(self, machine, arguments):
        allArguments = tuple(arguments)
        if allArguments in self.memoizationTable:
            return self.memoizationTable[allArguments]

        result = super().evaluateWithArguments(machine, arguments)
        self.applyNameToResult(machine, allArguments, result)
        self.memoizationTable[allArguments] = result
        return result

    def applyNameToResult(self, machine, arguments, result):
        pass

class MemoizedFunctionTypeValue(AbstractMemoizedFunctionTypeValue):
    def asMemoizedFunction(self):
        return self

class TemplatedFunctionTypeValue(AbstractMemoizedFunctionTypeValue):
    def __init__(self, baseFunctionTypeValue):
        super().__init__(baseFunctionTypeValue)
        self.resultExtensionList = []

    def asTemplatedFunction(self):
        return self

    def applyResultTransform(self, machine, result):
        callArguments = (result,)
        for resultExtension in self.resultExtensionList:
            resultExtension.evaluateWithArguments(machine, callArguments)
        return result

    def extendWith(self, machine, extension):
        for arguments, result in self.memoizationTable.items():
            extension.evaluateWithArguments(machine, arguments)
        self.resultExtensionList.append(extension)

    def performWithArguments(self, machine, selector, arguments):
        if selector == 'extendWith:':
            return self.extendWith(machine, arguments[0])
        return super().performWithArguments(machine, selector, arguments)

    def applyNameToResult(self, machine, arguments, result):
        if self.name is None:
            return

        valueName = self.name + '('
        i = 0
        for arg in arguments:
            if i > 0:
                valueName += ', '
            valueName += repr(arg)
            i += 1
        valueName += ')'
        result.setConstructionTemplateAndArguments(self, arguments)
        result.onGlobalBindingWithSymbolAdded(Symbol.intern(valueName))

class FunctionType(SimpleType):
    def __init__(self):
        self.isDependentFunctionType = False
        self.isSimpleFunctionType = False
        self.canonicalSimpleFunctionType = None
        self.dependentDefinitionEnvironment = None
        self.dependentDefinitionArguments = None
        self.dependentDefinitionResultType = None
        self.canonicalArgumentTypes = None
        self.canonicalResultType = None
        self.canonicalArgumentsArraySlice = None
        self.hasForAllArgument = False
        self.argumentCount = 0
        super().__init__(schema = TrivialTypeSchema(), supertype = getBasicTypeNamed('Function'))

    def newWithBootstrapImplementation(self, bootstrapImplementation):
        return FunctionTypeValue(self, bootstrapImplementation = bootstrapImplementation)

    @primitiveNamed("function.newWithImplementation")
    def newWithImplementation(self, implementation):
        return FunctionTypeValue(self, implementation = implementation)

    @classmethod
    def makeSimpleFunctionType(cls, argumentTypes, resultType):
        cacheKey = (tuple(argumentTypes), resultType)
        if cacheKey in SimpleFunctionMemoizationTable:
            return SimpleFunctionMemoizationTable[cacheKey]

        self = cls()
        SimpleFunctionMemoizationTable[cacheKey] = self

        self.isSimpleFunctionType = True
        self.canonicalArgumentTypes = argumentTypes
        self.canonicalResultType = resultType
        self.canonicalArgumentsArraySlice = None
        self.canonicalSimpleFunctionType = self
        self.computeFunctionTypeClassification()
        return self

    @classmethod
    def makeDependentFunctionType(cls, environment, arguments, resultType):
        self = cls()
        self.isDependentFunctionType = True
        self.dependentDefinitionEnvironment = environment
        self.dependentDefinitionArguments = arguments
        self.dependentDefinitionResultType = resultType
        self.computeFunctionTypeClassification()
        return self

    @classmethod
    def constructFromTypeSpec(cls, functionSpec, ownerType = None):
        if isinstance(functionSpec, tuple):
            return cls.constructFromTupleTypeSpec(functionSpec, ownerType)
        else:
            return cls.constructFromStringTypeSpec(functionSpec, ownerType)

    @classmethod
    def constructFromStringTypeSpec(cls, functionSpec, ownerType):
        from parser import parseString
        environment = cls.constructTypeSpecParsingEnvironmentForType(ownerType)
        parsedTypeSpec = parseString(functionSpec)
        evaluatedTypeSpec = parsedTypeSpec.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)
        if isinstance(evaluatedTypeSpec, FunctionTypeValue):
            return evaluatedTypeSpec.getType()
        return evaluatedTypeSpec

    @classmethod
    def constructFromTupleTypeSpec(cls, functionSpec, ownerType):
        environment = cls.constructTypeSpecParsingEnvironmentForType(ownerType)
        argumentsSpec, resultTypeSpec = functionSpec
        if isinstance(argumentsSpec, str):
            argumentsSpec = (argumentsSpec,)

        argumentTypes = list(map(lambda argSpec: cls.evaluateParameterOrResultSpecWithEnvironment(argSpec, environment), argumentsSpec))
        resultType = cls.evaluateParameterOrResultSpecWithEnvironment(resultTypeSpec, environment)
        return cls.makeSimpleFunctionType(argumentTypes, resultType)

    @classmethod
    def evaluateParameterOrResultSpecWithEnvironment(cls, typespec, environment):
        if isinstance(typespec, str):
            from parser import parseString
            parsedTypeSpec = parseString(typespec)
            return parsedTypeSpec.evaluateWithEnvironment(EvaluationMachine.getActive(), environment)
        else:
            return typespec

    @classmethod
    def constructTypeSpecParsingEnvironmentForType(cls, ownerType):
        environment = ActiveBootstrapCompiler.getTopLevelEnvironment().makeChildLexicalScope()
        if ownerType is not None:
            environment.setSymbolImmutableValue(Symbol.intern('SelfType'), ownerType)
        return environment

    def computeFunctionTypeClassification(self):
        ## Check the presence of a for all argument.
        self.hasForAllArgument = False
        if self.isSimpleFunctionType:
            self.argumentCount = len(self.canonicalArgumentTypes)
            return

        self.argumentCount = 0
        for argument in self.dependentDefinitionArguments:
            if argument.isForAllArgumentExpression():
                self.hasForAllArgument = True
            else:
                self.argumentCount += 1

        ## TODO: Check on whether this is a dependent function type, or not.

    def getName(self):
        if self.name is None:
            if self.isSimpleFunctionType:
                self.name = '('
                argumentIndex = 0
                for argument in self.canonicalArgumentTypes:
                    if argumentIndex > 0:
                        self.name += ' -- '
                    self.name += repr(argument)
                    argumentIndex += 1
                if argumentIndex == 0:
                    self.name += 'Void'
                self.name += ') => '
                self.name += repr(self.canonicalResultType)
            else:
                self.name = '{'
                argumentIndex = 0
                for argument in self.dependentDefinitionArguments:
                    if argumentIndex > 0:
                        self.name += ' '
                    self.name += repr(argument)
                    argumentIndex += 1
                self.name += ' :: ('
                self.name += repr(self.dependentDefinitionResultType)
                self.name += ')} __type__'
        return self.name

    def ensureCanonicalTypeIsEvaluated(self):
        if not self.isDependentFunctionType:
            return
        if self.canonicalArgumentTypes is not None:
            return

        self.canonicalArgumentTypes = []
        canonicalEvaluationEnvironment = self.dependentDefinitionEnvironment.makeChildLexicalScope()
        for argument in self.dependentDefinitionArguments:
            argumentType = argument.evaluateCanonicalFormInEnvironment(canonicalEvaluationEnvironment)
            if not argument.isForAllArgumentExpression():
                self.canonicalArgumentTypes.append(argumentType)

        self.canonicalResultType = self.dependentDefinitionResultType.evaluateCanonicalFormInEnvironment(canonicalEvaluationEnvironment)

    def getCanonicalArgumentTypes(self):
        self.ensureCanonicalTypeIsEvaluated()
        return self.canonicalArgumentTypes

    @primitiveNamed('functionType.getCanonicalResultType')
    def getCanonicalResultType(self):
        self.ensureCanonicalTypeIsEvaluated()
        return self.canonicalResultType

    @primitiveNamed('functionType.getCanonicalArgumentTypes')
    def primitiveGetCanonicalArgumentTypes(self):
        if self.canonicalArgumentsArraySlice is None:
            self.canonicalArgumentsArraySlice = getBasicTypeNamed('ArraySlice')(getBasicTypeNamed('Type')).basicNewWithSequentialSlots(self.getCanonicalArgumentTypes())
        return self.canonicalArgumentsArraySlice

    @primitiveNamed('functionType.getArgumentCount')
    def primitiveGetArgumentCount(self):
        return getSizeValue(self.argumentCount)

    @primitiveNamed('functionType.makeFunctionSignatureAnalyzer')
    def makeFunctionSignatureAnalyzer(self):
        if self.isSimpleFunctionType:
            return SimpleFunctionSignatureAnalyzer(self)
        else:
            return DependentFunctionSignatureAnalyzer(self)

class TypeBuilder(BehaviorTypedObject):
    def __init__(self):
        super().__init__()

    @classmethod
    def initializeBehaviorType(cls, type):
        BehaviorTypedObject.initializeBehaviorType(type)
        type.addPrimitiveMethodsWithSelectors([
            (cls.newTrait, 'newTrait', '(SelfType) => Trait'),
            (cls.newAbsurdType, 'newAbsurdType', '(SelfType) => Type'),
            (cls.newTrivialType, 'newTrivialType', '(SelfType) => Type'),
            (cls.newProductType, 'newProductTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newSumTypeWith, 'newSumTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newEnumTypeWith, 'newEnumTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newEmptyPackedRecordType, 'newEmptyPackedRecordType', '(SelfType) => Type'),
            (cls.newEmptyRecordType, 'newEmptyRecordType', '(SelfType) => Type'),
            (cls.newEmptyUnionType, 'newEmptyUnionType', '(SelfType) => Type'),
            (cls.newEmptyGCClassType, 'newEmptyGCClassType', '(SelfType) => Type'),
            (cls.newRecordTypeWithSupertypeWith, 'newRecordTypeWithSupertype:with:', '(SelfType -- Type -- AnyValue) => Type'),
            (cls.newRecordTypeWith, 'newRecordTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newArrayTypeForWithBounds, 'newArrayTypeFor:withBounds:', '(SelfType -- Type -- Integer) => Type'),
            (cls.newPointerTypeFor, 'newPointerTypeFor:addressSpace:', '(SelfType -- Type -- Symbol) => Type'),
            (cls.newReferenceTypeFor, 'newReferenceTypeFor:', '(SelfType -- Type -- Symbol) => Type'),

            (cls.newBooleanTypeWithSizeAndAlignment, 'newBooleanTypeWithSize:alignment:', '(SelfType -- Integer -- Integer) => Type'),
            (cls.newUnsignedIntegerTypeWithSizeAndAlignment, 'newUnsignedIntegerTypeWithSize:alignment:', '(SelfType -- Integer -- Integer) => Type'),
            (cls.newSignedIntegerTypeWithSizeAndAlignment, 'newSignedIntegerTypeWithSize:alignment:', '(SelfType -- Integer -- Integer) => Type'),
            (cls.newCharacterTypeWithSizeAndAlignment, 'newCharacterTypeWithSize:alignment:', '(SelfType -- Integer -- Integer) => Type'),
            (cls.newFloatTypeWithSizeAndAlignment, 'newFloatTypeWithSize:alignment:', '(SelfType -- Integer -- Integer) => Type'),

            (cls.newGCClassWithSlots, 'newGCClassWithSlots:', '(SelfType -- AnyValue) => Type'),
            (cls.newGCClassWithSuperclassSlots, 'newGCClassWithSuperclass:slots:', '(SelfType -- Type -- AnyValue) => Type'),
            (cls.newGCClassWithPublicSlots, 'newGCClassWithPublicSlots:', '(SelfType -- AnyValue) => Type'),
            (cls.newGCClassWithSuperclassPublicSlots, 'newGCClassWithSuperclass:publicSlots:', '(SelfType -- Type -- AnyValue) => Type'),

            (cls.newPairTypeWith, 'newPairType:with:', '(SelfType -- Type -- Type) => Type'),
            (cls.extendTupleTypeWith, 'extendTupleType:with:', '(SelfType -- Type -- Type) => Type'),
            (cls.newSimpleFunctionTypeWithResultType, 'newSimpleFunctionTypeWithResultType:', '(SelfType -- Type -- Type) => Type'),
            (cls.newSimpleFunctionTypeWithArgumentAndResultType, 'newSimpleFunctionTypeWithArgument:resultType:', '(SelfType -- Type -- Type) => Type'),
            (cls.newSimpleFunctionTypeWithArgumentsAndResultType, 'newSimpleFunctionTypeWithArguments:resultType:', '(SelfType -- Type -- Type) => Type')
        ])

    def newTrait(self):
        return Trait(schema = TraitTypeSchema())

    def newAbsurdType(self):
        return SimpleType(schema = AbsurdTypeSchema())

    def newTrivialType(self):
        return SimpleType(schema = TrivialTypeSchema())

    def newProductType(self, elementTypes):
        elementTypeList = list(elementTypes)
        if len(elementTypeList) == 0:
            return self.newTrivialType()
        return SimpleType(schema = ProductTypeSchema(elementTypeList))

    def newSumTypeWith(self, elementTypes):
        elementTypeList = list(elementTypes)
        return SimpleType(schema = SumTypeSchema(elementTypeList))

    def newEnumTypeWith(self, memberValueDictionary):
        elementTypeList = []

        for assoc in memberValueDictionary:
            symbolValue = assoc.getValue()
            elementTypeList.append(symbolValue)

        sumType = SimpleType(schema = SumTypeSchema(elementTypeList))
        for assoc in memberValueDictionary:
            symbolName = assoc.getKey()
            symbolValue = assoc.getValue()
            sumType.setSymbolValueBinding(symbolName, symbolValue)
        return sumType

    def newEmptyRecordType(self):
        return SimpleType(schema = RecordTypeSchema([]))

    def newEmptyPackedRecordType(self):
        return SimpleType(schema = RecordTypeSchema([], packed = True))

    def newEmptyUnionType(self):
        return SimpleType(schema = UnionTypeSchema([]))

    def newEmptyGCClassType(self):
        return SimpleType(schema = GCClassTypeSchema([]))

    def newRecordTypeWithSupertypeWith(self, supertype, slots):
        return SimpleType(supertype = supertype, schema = RecordTypeSchema(slots, supertypeSchema = supertype.schema))

    def newRecordTypeWith(self, slots):
        return SimpleType(schema = RecordTypeSchema(slots))

    def newArrayTypeForWithBounds(self, elementType, bounds):
        return SimpleType(schema = ArrayTypeSchema(elementType, bounds))

    def newPointerTypeFor(self, elementType, addressSpace):
        return SimpleType(schema = PointerTypeSchema(elementType, addressSpace))

    def newReferenceTypeFor(self, elementType, addressSpace):
        return SimpleType(schema = ReferenceTypeSchema(elementType, addressSpace))

    def newGCClassWithSuperclassSlots(self, supertype, instanceVariable):
        return SimpleType(supertype = supertype, schema = GCClassTypeSchema(instanceVariable, supertypeSchema = supertype.schema))

    def newGCClassWithSlots(self, instanceVariable):
        return SimpleType(schema = GCClassTypeSchema(instanceVariable))

    def newGCClassWithSuperclassPublicSlots(self, supertype, instanceVariable):
        return SimpleType(supertype = supertype, schema = GCClassTypeSchema(instanceVariable, supertypeSchema = supertype.schema))

    def newGCClassWithPublicSlots(self, instanceVariable):
        return SimpleType(schema = GCClassTypeSchema(instanceVariable))

    def newBooleanTypeWithSizeAndAlignment(self, size, alignment):
        return SimpleType(schema = PrimitiveBooleanTypeSchema(size, alignment))

    def newUnsignedIntegerTypeWithSizeAndAlignment(self, size, alignment):
        return SimpleType(schema = PrimitiveUnsignedIntegerTypeSchema(size, alignment))

    def newSignedIntegerTypeWithSizeAndAlignment(self, size, alignment):
        return SimpleType(schema = PrimitiveSignedIntegerTypeSchema(size, alignment))

    def newCharacterTypeWithSizeAndAlignment(self, size, alignment):
        return SimpleType(schema = PrimitiveCharacterTypeSchema(size, alignment))

    def newFloatTypeWithSizeAndAlignment(self, size, alignment):
        return SimpleType(schema = PrimitiveFloatTypeSchema(size, alignment))

    def newPairTypeWith(self, first, second):
        return getTupleTypeWithElements((first, second))

    def extendTupleTypeWith(self, tupleType, next):
        return getTupleTypeWithElements(tuple(list(tupleType.schema.elementTypes) + [next]))

    def newSimpleFunctionTypeWithResultType(self, resultType):
        return self.newSimpleFunctionTypeWithArgumentAndResultType((), resultType)

    def newSimpleFunctionTypeWithArgumentAndResultType(self, argumentType, resultType):
        return self.doNewSimpleFunctionTypeWithArgumentsAndResultType((argumentType,), resultType)

    def newSimpleFunctionTypeWithArgumentsAndResultType(self, argumentsTypes, resultType):
        if hasattr(argumentsTypes, 'schema'):
            return self.doNewSimpleFunctionTypeWithArgumentsAndResultType(tuple(argumentsTypes.schema.elementTypes), resultType)
        else:
            return self.doNewSimpleFunctionTypeWithArgumentsAndResultType(tuple(list(argumentsTypes)), resultType)

    def doNewSimpleFunctionTypeWithArgumentsAndResultType(self, argumentsTypes, resultType):
        return FunctionType.makeSimpleFunctionType(argumentsTypes, resultType)

class ArraySlicePrimitives:
    @primitiveNamed('arraySlice.collect')
    def collect(arraySlice, aBlock):
        elements = arraySlice.getSlotNamed('elements')
        size = arraySlice.getSlotNamed('size')

        resultElementType = aBlock.getType().getCanonicalResultType()
        resultArrayType = getBasicTypeNamed(Symbol.intern('Array'))(resultElementType, size)

        collectedElements = resultArrayType.basicNewWithSequentialSlots(list(map(lambda index: aBlock(elements[Integer(index)]), range(size.asInteger()))))
        return collectedElements.asSharedArraySlice()

    @primitiveNamed('arraySlice.collectWithIndex')
    def collectWithIndex(arraySlice, aBlock):
        elements = arraySlice.getSlotNamed('elements')
        size = arraySlice.getSlotNamed('size')

        resultElementType = aBlock.getType().getCanonicalResultType()
        indexType = aBlock.getType().getCanonicalArgumentTypes()[1]
        resultArrayType = getBasicTypeNamed(Symbol.intern('Array'))(resultElementType, size)

        collectedElements = resultArrayType.basicNewWithSequentialSlots(list(map(lambda index: aBlock(elements[Integer(index)], indexType.basicNewWithValue(index)), range(size.asInteger()))))
        return collectedElements.asSharedArraySlice()

def extractArraySliceElements(arraySlice):
    elements = arraySlice.getSlotNamed('elements')
    size = arraySlice.getSlotNamed('size')
    return list(map(lambda index: elements[Integer(index)], range(size.asInteger())))

class ObjectPrimitives:
    @primitiveNamed('object.comparison.identityEquals')
    def primitiveIdentityEquals(self, other):
        return getBooleanValue(self is other)

    @primitiveNamed('object.comparison.identityNotEquals')
    def primitiveIdentityNotEquals(self, other):
        return getBooleanValue(self is not other)

    @primitiveNamed('object.comparison.identityHash')
    def primitiveIdentityNotEquals(self):
        return getSizeValue(self.identityHash())

    @primitiveNamed('object.runWithIn')
    def primitiveRunWithIn(self, selector, arguments, receiver):
        return self.runWithIn(EvaluationMachine.getActive(), selector, extractArraySliceElements(arguments), receiver)

    @primitiveNamed('object.evaluateWithArguments')
    def primitiveEvaluateWithArguments(self, arguments):
        return self.evaluateWithArguments(EvaluationMachine.getActive(), extractArraySliceElements(arguments))

class ArrayPrimitives:
    @primitiveNamed('array.basicAt')
    def primitiveArrayBasicAt(self, index):
        return self[index.asInteger()]

    @primitiveNamed('array.basicAtPut')
    def primitiveArrayBasicAtPut(self, index, value):
        self[index.asInteger()] = value
        return self[index.asInteger()]

class PointerPrimitives:
    @primitiveNamed('pointer.allocateWithCount')
    def primitiveIdentityEquals(self, countValue):
        count = countValue.asInteger()
        if count == 0:
            return self.basicNew()

        pointedType = self.schema.elementType
        return self.basicNewWithValue(ListValueMock([None] * count))

    @primitiveNamed('pointer.basicAt')
    def primitivePointerBasicAt(self, index):
        return self[index.asInteger()]

    @primitiveNamed('pointer.basicAtPut')
    def primitivePointerBasicAtPut(self, index, value):
        self[index.asInteger()] = value
        return self[index.asInteger()]

class TypePrimitives:
    @primitiveNamed('type.newSimpleFunctionType')
    def newSimpleFunctionTypeWithArgumentsAndResultType(self, argumentsTypes, resultType):
        return FunctionType.makeSimpleFunctionType(tuple(list(argumentsTypes)), resultType)

class FunctionPrimitives:
    @primitiveNamed('function.hasMethodFlag')
    def hasMethodFlag(self, methodFlag):
        return self.hasMethodFlag(methodFlag)
