from os import environ
from queue import Empty

from errors import *
from evalmachine import *

ActiveBootstrapCompiler = None
BasicTypeEnvironment = None
SemanticAnalysisTypeMapping = None

PrimitiveMethodTable = {}

def getSemanticAnalysisType(symbol):
    return SemanticAnalysisTypeMapping.at(symbol)

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
        selector = Symbol('toString')
        if self.answersTo(selector):
            return self.performWithArguments(EvaluationMachine.getActive(), selector, [])
        return self.defaultToString()

    def printString(self):
        selector = Symbol('printString')
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
        return self.shalowCopy()

    def asSymbolBindingWithName(self, name):
        return SymbolValueBinding(name, self)

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        raise SubclassResponsibility()

    def installedInType(self, type):
        pass

    def installedInMetaTypeOf(self, type):
        pass

    def asArraySlice(self):
        return self.performWithArguments(EvaluationMachine.getActive(), Symbol('asArraySlice'), ())

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

class PrimitiveMethod(TypedValue):
    def __init__(self, method, functionTypeSpec):
        self.method = method
        self.methodFlags = []
        self.functionTypeSpec = functionTypeSpec
        self.functionType = None
        self.rawOwnerType = None
        self.rawOwnerTypeIsMetaType = False

    def installedInType(self, type):
        self.rawOwnerType = type
        self.rawOwnerTypeIsMetaType = False

    def installedInMetaTypeOf(self, type):
        self.rawOwnerType = type
        self.rawOwnerTypeIsMetaType = True

    def getOwnerType(self):
        if self.rawOwnerTypeIsMetaType:
            return self.rawOwnerType.getType()
        else:
            return self.rawOwnerType

    def getType(self):
        if self.functionType is None:
            self.functionType = FunctionType.constructFromTypeSpec(self.functionTypeSpec, self.getOwnerType())
            assert self.functionType is not None
        return self.functionType

    def runWithIn(self, machine, selector, arguments, receiver):
        return coerceNoneToNil(self.method(receiver, *arguments))

def primitiveNamed(primitiveName, functionTypeSpec = None):
    def decorator(primitiveImplementation):
        primitiveMethod = PrimitiveMethod(primitiveImplementation, functionTypeSpec)
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
        return getSemanticAnalysisType(Symbol('SymbolBinding'))

    def getSymbolBindingReferenceValue(self):
        raise NotImplementedError()

    def asSymbolBindingWithName(self, name):
        return self

class SymbolValueBinding(SymbolBinding):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def getType(self):
        return getSemanticAnalysisType(Symbol('SymbolValueBinding'))

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
        return getSemanticAnalysisType(Symbol('ForAllPlaceholderBinding'))

class TypeInterface:
    def canBeCoercedToType(self, targetType):
        return self is targetType

    def coerceValue(self, value):
        if value.getType() is self:
            return value
        raise CannotCoerceValueToType('Cannot coerce (%s:%s) into type "%s"' % (repr(value.getType()), repr(value), repr(self)))

    def runWithIn(self, machine, selector, arguments, receiver):
        raise NotImplementedError()

    @primitiveNamed('type.lookupSelector')
    def primitiveLookupSelector(self, selector):
        return self.lookupSelector(selector)

    @primitiveNamed('type.lookupLocalSelector')
    def primitiveLookupLocalSelector(self, selector):
        return self.lookupLocalSelector(selector)

    @primitiveNamed('type.supportsDynamicDispatch')
    def primitiveSupportsDynamicDispatch(self):
        return getBooleanValue(self.supportsDynamicDispatch())

    def supportsDynamicDispatch(self):
        return False

    def asCanonicalTypeForDependentType(self):
        return self

class Integer(int, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Integer'))

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
        return getBasicTypeNamed(Symbol('Character'))

    def shallowCopy(self):
        return self

    @primitiveNamed('character.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

class Float(float, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Float'))

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
        return getBasicTypeNamed(Symbol('String'))

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
        return Symbol(self)

    def shallowCopy(self):
        return String(self)

    @primitiveNamed('string.conversion.toInteger')
    def asInteger(self):
        return Integer(self)

class Symbol(str, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Symbol'))

    @primitiveNamed('symbol.conversion.toString')
    def defaultToString(self):
        return String(self)

    def shallowCopy(self):
        return Symbol(self)

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
            self.elementType = getBasicTypeNamed(Symbol('AnyValue'))
        return self.elementType

    def getType(self):
        if not hasattr(self, 'type'):
            self.type = getBasicTypeNamed(Symbol('Array'))(self.getElementType(), getSizeValue(len(self)))
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
        return getBasicTypeNamed(Symbol('AnyAssociation'))

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

class Dictionary(list, TypedValue):

    @classmethod
    def fromDict(cls, d):
        return cls(map(lambda pair: Association(pair[0], pair[1]), d.items()))

    def getType(self):
        return getBasicTypeNamed(Symbol('AnyArrayDictionary'))

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

def getTupleTypeWithElements(tupleElements):
    elementsArray = Array(tupleElements)
    elementsArray.elementType = getBasicTypeNamed(Symbol('Type'))
    return getBasicTypeNamed(Symbol('Tuple'))(elementsArray)

class Tuple(tuple, TypedValue):
    def getType(self):
        if not hasattr(self, 'type'):
            self.type = getTupleTypeWithElements(tuple(map(lambda x: x.getType(), self)))
        return self.type

class TypeSchemaPrimitiveMethod(PrimitiveMethod):
    def getType(self):
        return getBasicTypeNamed(Symbol('TypeSchemaPrimitiveMethod'))

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class RecordTypeAccessorPrimitiveMethod(PrimitiveMethod):
    def __init__(self, selector, slotName, slotIndex, slotType, functionTypeSpec):
        super().__init__(None, functionTypeSpec)
        self.selector = selector
        self.slotName = slotName
        self.slotIndex = slotIndex
        self.slotType = slotType

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class RecordTypeGetterPrimitiveMethod(RecordTypeAccessorPrimitiveMethod):
    def runWithIn(self, machine, selector, arguments, receiver):
        return self.slotType.coerceValue(coerceNoneToNil(receiver.getSlotWithIndexAndName(self.slotIndex, self.slotName)))

class RecordTypeSetterPrimitiveMethod(RecordTypeAccessorPrimitiveMethod):
    def runWithIn(self, machine, selector, arguments, receiver):
        return receiver.setSlotWithIndexAndName(self.slotIndex, self.slotName, arguments[0])

class BlockClosure(TypedValue):
    def __init__(self, node, environment, primitiveName = None, methodFlags = []):
        self.node = node
        self.environment = environment
        self.name = None
        self.primitiveName = primitiveName
        self.methodFlags = methodFlags
        self.functionType = None

    def isConversionMethod(self):
        return 'conversion' in self.methodFlags

    def isConstructionMethod(self):
        return 'construction' in self.methodFlags

    def isExplicitMethod(self):
        return 'explicit' in self.methodFlags

    def getType(self):
        if self.functionType is None:
            self.functionType = self.node.constructFunctionTypeWithEnvironment(self.environment)
        return self.functionType

    def performWithArguments(self, machine, selector, arguments):
        if selector == '()':
            return self.evaluateWithArguments(machine, arguments)
        elif selector == 'memoized':
            return self.asMemoizedBlockClosure()
        elif selector == 'templated':
            return self.asTemplatedBlockClosure()
        return super().performWithArguments(machine, selector, arguments)

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.evaluateWithArguments(machine, tuple([receiver] + list(arguments)))

    def evaluateWithArguments(self, machine, arguments):
        if self.primitiveName is not None and self.primitiveName in PrimitiveMethodTable:
            rawResult = self.node.evaluateClosureResultCoercionWithEnvironmentAndArguments(machine, self.environment, arguments,
                PrimitiveMethodTable[self.primitiveName].runWithIn(machine, Symbol('()'), arguments[1:], arguments[0]))
        else:
            rawResult = self.node.evaluateClosureWithEnvironmentAndArguments(machine, self.environment, arguments)
        return self.applyResultTransform(machine, rawResult)

    def asMemoizedBlockClosure(self):
        return MemoizedBlockClosure(self.node, self.environment)

    def asTemplatedBlockClosure(self):
        return TemplatedBlockClosure(self.node, self.environment)

    def applyResultTransform(self, machine, result):
        return result

    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def defaultPrintString(self) -> str:
        if self.name is not None:
            return self.name
        return 'BlockClosure(' + str(self.getType()) + ')'

    @primitiveNamed('function.hasMethodFlag')
    def hasMethodFlag(self, methodFlag):
        return getBooleanValue(methodFlag in self.methodFlags)

    def __call__(self, *args):
        return self.evaluateWithArguments(EvaluationMachine.getActive(), tuple(args))

class AbstractMemoizedBlockClosure(BlockClosure):
    def __init__(self, node, environment):
        super().__init__(node, environment)
        self.memoizationTable = {}

    def evaluateWithArguments(self, machine, arguments):
        if arguments in self.memoizationTable:
            return self.memoizationTable[arguments]

        result = super().evaluateWithArguments(machine, arguments)
        self.applyNameToResult(machine, arguments, result)
        self.memoizationTable[arguments] = result
        return result

    def applyNameToResult(self, machine, arguments, result):
        pass

class MemoizedBlockClosure(AbstractMemoizedBlockClosure):
    def asMemoizedBlockClosure(self):
        return self

class TemplatedBlockClosure(AbstractMemoizedBlockClosure):
    def __init__(self, node, environment):
        super().__init__(node, environment)
        self.resultExtensionList = []

    def asTemplatedBlockClosure(self):
        return self

    def applyResultTransform(self, machine, result):
        callSymbol = Symbol('()')
        callArguments = (result,)
        for resultExtension in self.resultExtensionList:
            resultExtension.performWithArguments(machine, callSymbol, callArguments)
        return result

    def extendWith(self, machine, extension):
        callSymbol = Symbol('()')
        for arguments, result in self.memoizationTable.items():
            extension.performWithArguments(machine, callSymbol, (result,))
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
        result.onGlobalBindingWithSymbolAdded(Symbol(valueName))

class TypeSchema(TypedValue):
    def __init__(self):
        self.methodDict = {}
        self.metaTypeMethodDict = {}
        self.buildPrimitiveMethodDictionary()

    def getType(self):
        return getBasicTypeNamed('TypeSchema')

    def isDefaultConstructible(self):
        return False

    def installedInType(self, type):
        for method in self.methodDict:
            method.installedInType(type)
        for method in self.metaTypeMethodDict:
            method.installedInMetaTypeOf(type)

    def buildPrimitiveMethodDictionary(self):
        self.methodDict[Symbol('shallowCopy')] = TypeSchemaPrimitiveMethod(self.primitiveShallowCopy, '(SelfType => SelfType)')
        self.methodDict[Symbol('yourself')] = TypeSchemaPrimitiveMethod(self.primitiveYourself, '(SelfType => SelfType)')
        self.methodDict[Symbol('__type__')] = TypeSchemaPrimitiveMethod(self.getTypeFromValue, '(SelfType => SelfType __type__)')

    def lookupPrimitiveWithSelector(self, selector):
        if selector in self.methodDict:
            return self.methodDict[selector]
        return None

    def lookupMetaTypePrimitiveWithSelector(self, selector):
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

    def hasDirectCoercionToPointerOf(self, baseType):
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

class OpaqueTypeSchema(TypeSchema):
    def getType(self):
        return getBasicTypeNamed('OpaqueTypeSchema')

class EmptyTypeSchema(TypeSchema):
    def __init__(self):
        super().__init__()
        self.uniqueInstance = None

    def getType(self):
        return getBasicTypeNamed('EmptyTypeSchema')

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
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
    def primitiveNegated(self, other):
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
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)value :: self}')
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
        self.methodDict[Symbol('__typeSelector__')] = TypeSchemaPrimitiveMethod(self.getTypeSelector, '(SelfType) => Size')
        self.methodDict[Symbol('get:')] = TypeSchemaPrimitiveMethod(self.getWithType, '{:(SelfType)self :(Type)expectedType :: expectedType}')
        self.methodDict[Symbol('is:')] = TypeSchemaPrimitiveMethod(self.isWithType, '{:(SelfType)self :(Type)expectedType :: Boolean}')
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)initialValue :: self}')
        self.metaTypeMethodDict[Symbol('basicNew:typeSelector:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValueTypeSelector, '{:(SelfType)self :(AnyValue)initialValue :(Size)typeSelector :: self}')
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
        expectedType = self.type.schema.elementTypes[slotIndex]
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

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)sequentialSlots :: self}')
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, productType):
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
    def __init__(self, slots, supertypeSchema = None):
        self.slots = []
        super().__init__([])
        self.supertypeSchema = supertypeSchema
        self.definePublicSlots(slots)

    def definePublicSlots(self, slots):
        self.slots = slots
        self.allSlots = slots
        self.startSlotIndex = 0
        if self.supertypeSchema is not None:
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

    def getType(self):
        return getBasicTypeNamed('RecordTypeSchema')

    def getIndexOfSlotNamed(self, slotName):
        return self.slotNameDictionary[slotName]

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)slots :: self}')
        self.metaTypeMethodDict[Symbol('basicNewWithNamedSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithNamedSlots, '{:(SelfType)self :(AnyValue)slots :: self}')
        for slotIndex in range(len(self.slots)):
            slotAssociation = self.slots[slotIndex]
            slotName = slotAssociation.key
            getterName = Symbol(slotName)
            setterName = Symbol(slotName + ':')
            slotType = self.allSlots[slotIndex]
            self.methodDict[getterName] = RecordTypeGetterPrimitiveMethod(getterName, getterName, self.startSlotIndex + slotIndex, slotAssociation.value, (('SelfType'), slotType))
            self.methodDict[setterName] = RecordTypeSetterPrimitiveMethod(setterName, getterName, self.startSlotIndex + slotIndex, slotAssociation.value, (('SelfType', slotType), slotType))
        return super().buildPrimitiveMethodDictionary()

    def basicNewWithNamedSlots(self, recordType, namedSlots):
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

    def basicNewWithArrayListElements(self, recordType, elements):
        return elements

    def basicNewWithArraySliceElements(self, recordType, elements):
        assert len(self.elementTypes) == 2
        return self.basicNewWithSequentialSlots(recordType, [
            self.elementTypes[0].basicNewWithValue(elements),
            self.elementTypes[1].basicNewWithValue(len(elements))
        ])

class ArrayTypeValue(ProductTypeValue):
    def __getitem__(self, index):
        return self.elements[index.asInteger()]

class ArrayTypeSchema(TypeSchema):
    def __init__(self, elementType, bounds):
        self.elementType = elementType
        self.bounds = bounds.asInteger()
        super().__init__()

    def getType(self):
        return getBasicTypeNamed('ArrayTypeSchema')

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithSequentialSlots, '{:(SelfType)self :(AnyValue)slots :: self}')
        self.methodDict[Symbol('basicAt:')] = TypeSchemaPrimitiveMethod(self.basicAt, (('SelfType', 'Size'), self.elementType))
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return ArrayTypeValue(valueType, list(map(lambda x: self.elementType.basicNew(), [None] * self.bounds)))

    def basicNewWithSequentialSlots(self, valueType, slots):
        if len(slots) != self.bounds:
            raise InterpreterError('Array construction element count mismatch.')
        
        return ArrayTypeValue(valueType, list(map(lambda x: x.shallowCopyValue(), slots)))

    def hasDirectCoercionToPointerOf(self, baseType):
        return self.elementType == baseType

    def makeDirectPointerOfValueTo(self, value, valueType, targetType):
        return PointerTypeValue(targetType, value, 0)

    def basicAt(self, value, index):
        return value[index.asInteger()]

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
        return '%s(%s:%d)' % (str(self.type), str(self.value), self.baseIndex)

    def __getitem__(self, index):
        return self.value[Integer(index.asInteger() + self.baseIndex)]

class PointerTypeSchema(TypeSchema):
    def __init__(self, elementType):
        self.elementType = elementType
        super().__init__()

    def getType(self):
        return getBasicTypeNamed('PointerTypeSchema')

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

    def canCoerceValueOfType(self, valueType):
        if valueType.schema.hasDirectCoercionToPointerOf(self.elementType):
            return True

        return super().canCoerceValueOfType(valueType)

    def coerceValueOfTypeIntoType(self, value, valueType, targetType):
        if valueType.schema.hasDirectCoercionToPointerOf(self.elementType):
            return valueType.schema.makeDirectPointerOfValueTo(value, valueType, targetType)

        return super().coerceValueOfTypeIntoType(value, valueType, targetType)

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew, '{:(SelfType)self :: self}')
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue, '{:(SelfType)self :(AnyValue)value :: self}')
        self.methodDict[Symbol('basicAt:')] = TypeSchemaPrimitiveMethod(self.basicAt, (('SelfType', 'Size'), self.elementType))
        return super().buildPrimitiveMethodDictionary()

    def basicAt(self, value, index):
        return value[index.asInteger()]

    def basicNew(self, valueType):
        return PointerTypeValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return PointerTypeValue(valueType, initialValue)

class ReferenceTypeSchema(TypeSchema):
    def __init__(self, elementType):
        self.elementType = elementType
        super().__init__()

    def getType(self):
        return getBasicTypeNamed('ReferenceTypeSchema')

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

    def canCoerceValueOfType(self, valueType):
        if valueType.schema.hasDirectCoercionToPointerOf(self.elementType):
            return True

        return super().canCoerceValueOfType(valueType)

class GCClassTypeSchema(RecordTypeSchema):
    def getType(self):
        return getBasicTypeNamed('GCClassTypeSchema')

    def hasPointerOrReferenceValueCopySemantics(self):
        return True

    def supportsDynamicDispatch(self):
        return True

class BehaviorType(TypedValue, TypeInterface):
    def __init__(self, name = None, supertype = None, traits = [], schema = EmptyTypeSchema(), methodDict = {}):
        self.name = name
        self.methodDict = dict(methodDict)
        self.implicitConversionMethods = []
        self.explicitConversionMethods = []
        self.implicitConstructionMethods = []
        self.explicitConstructionMethods = []
        self.supertype = supertype
        self.traits = traits
        self.schema = schema
        self.schema.installedInType(self)
        self.type = None

        self.typeFlags = []
        self.hasAnyValueFlag = False
        self.hasArraySliceFlag = False

        self.constructionTemplate = None
        self.constructionTemplateArguments = None

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

    def getSlotWithIndexAndName(self, slotIndex, slotName):
        if slotName == 'supertype':
            return self.supertype
        elif slotName == 'schema':
            return self.schema
        elif slotName == 'name':
            return self.name
        return super().getSlotWithIndexAndName(slotIndex, slotName)

    def isSubtypeOf(self, expectedSuperType):
        if self is expectedSuperType:
            return True;
        if self.supertype is not None:
            return self.supertype.isSubtypeOf(expectedSuperType)
        return False
        
    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def setConstructionTemplateAndArguments(self, template, arguments):
        self.constructionTemplate = template
        self.constructionTemplateArguments = arguments

    def performWithArguments(self, machine, selector, arguments):
        return super().performWithArguments(machine, selector, arguments)

    def directTraits(self):
        return self.traits

    def lookupLocalSelector(self, selector):
        found = self.methodDict.get(selector, None)
        if found is not None:
            return found

        ## Check a schema inserted primitive.
        found = self.schema.lookupPrimitiveWithSelector(selector)
        if found is not None:
            return found
        return None

    def lookupSelector(self, selector):
        ## Check in the local method dictionary.
        found = self.lookupLocalSelector(selector)
        if found is not None:
            return found

        ## Find in a direct trait.
        for trait in self.directTraits():
            found = trait.lookupLocalSelector(found)
            if found is not None:
                return found

        ##  Find in the supertype.
        if self.supertype is not None:
            return self.supertype.lookupSelector(selector)
        return None

    def runWithIn(self, machine, selector, arguments, receiver):
        method = self.lookupSelector(selector)
        if method is None:
            raise DoesNotUnderstand('%s does not understand message %s' % (str(receiver), repr(selector)))
        return method.runWithIn(machine, selector, arguments, receiver)

    def addMethodWithSelector(self, method, selector):
        self.methodDict[selector] = method
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

    def withSelectorAddMethod(self, selector, method):
        self.addMethodWithSelector(method, selector)

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
            self.addMethodWithSelector(method, Symbol(selector))

    def addPrimitiveMethodsWithSelectors(self, methodsWithSelector):
        for method, selector, functionTypeSpec in methodsWithSelector:
            self.addMethodWithSelector(PrimitiveMethod(method, functionTypeSpec), Symbol(selector))

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
        return getBasicTypeNamed(Symbol('MetaType'))

    def createMetaType(self):
        typeSupertype = None
        if self.supertype is not None:
            typeSupertype = self.supertype.getType()
        else:
            typeSupertype = self.getMetaTypeRoot()
        return MetaType(thisType = self, supertype = typeSupertype, schema = OpaqueTypeSchema())

    @primitiveNamed('type.conversion.toString')
    def defaultToString(self):
        return String(self.getName())

    @primitiveNamed('type.conversion.printString')
    def defaultPrintString(self):
        return String(self.getName())

    def addMetaTypeRootMethods(self):
        cls = self.__class__
        self.addPrimitiveMethodsWithSelectors([
            (cls.withSelectorAddMethod, 'withSelector:addMethod:', '(AnyValue -- AnyValue) => AnyValue'),
            (cls.addTypeFlag, 'addTypeFlag:', 'AnyValue => AnyValue'),
            (cls.definePublicSlots, 'definePublicSlots:', '(SelfType -- AnyValue) => Type'),
        ])

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

    def basicNewWithArrayListElements(self, elements):
        return self.schema.basicNewWithArrayListElements(self, elements)

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
        self.behaviorType = BehaviorType()
        self.__class__.initializeBehaviorType(self.behaviorType)

    def getType(self):
        return self.behaviorType

    @classmethod
    def initializeBehaviorType(cls, type):
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
        super().__init__(supertype = getBasicTypeNamed('Function'))

    @classmethod
    def makeSimpleFunctionType(cls, argumentTypes, resultType):
        cacheKey = (argumentTypes, resultType)
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
        if isinstance(evaluatedTypeSpec, BlockClosure):
            return evaluatedTypeSpec.getType()
        return evaluatedTypeSpec

    @classmethod
    def constructTypeSpecParsingEnvironmentForType(cls, ownerType):
        environment = ActiveBootstrapCompiler.getTopLevelEnvironment()
        if ownerType is not None:
            environment = environment.makeChildLexicalScope()
            environment.setSymbolImmutableValue(Symbol('SelfType'), ownerType)
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
            (cls.newAbsurdType, 'newAbsurdType', '(SelfType) => Type'),
            (cls.newTrivialType, 'newTrivialType', '(SelfType) => Type'),
            (cls.newProductType, 'newProductTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newSumTypeWith, 'newSumTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newRecordTypeWith, 'newRecordTypeWith:', '(SelfType -- AnyValue) => Type'),
            (cls.newArrayTypeForWithBounds, 'newArrayTypeFor:withBounds:', '(SelfType -- AnyValue -- Integer) => Type'),
            (cls.newPointerTypeFor, 'newPointerTypeFor:', '(SelfType -- AnyValue -- Integer) => Type'),
            (cls.newReferenceTypeFor, 'newReferenceTypeFor:', '(SelfType -- AnyValue -- Integer) => Type'),

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

    def newAbsurdType(self):
        return SimpleType(schema = AbsurdTypeSchema())

    def newTrivialType(self):
        return SimpleType(schema = EmptyTypeSchema())

    def newProductType(self, elementTypes):
        elementTypeList = list(elementTypes)
        if len(elementTypeList) == 0:
            return self.newTrivialType()
        return SimpleType(schema = ProductTypeSchema(elementTypeList))

    def newSumTypeWith(self, elementTypes):
        elementTypeList = list(elementTypes)
        return SimpleType(schema = SumTypeSchema(elementTypeList))

    def newRecordTypeWith(self, slots):
        return SimpleType(schema = RecordTypeSchema(slots))

    def newArrayTypeForWithBounds(self, elementType, bounds):
        return SimpleType(schema = ArrayTypeSchema(elementType, bounds))

    def newPointerTypeFor(self, elementType):
        return SimpleType(schema = PointerTypeSchema(elementType))

    def newReferenceTypeFor(self, elementType):
        return SimpleType(schema = ReferenceTypeSchema(elementType))

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
        return self.doNewSimpleFunctionTypeWithArgumentsAndResultType(tuple(argumentsTypes.schema.elementTypes), resultType)

    def doNewSimpleFunctionTypeWithArgumentsAndResultType(self, argumentsTypes, resultType):
        return FunctionType.makeSimpleFunctionType(argumentsTypes, resultType)

class ArraySlicePrimitives:
    @primitiveNamed('arraySlice.collect')
    def collect(arraySlice, aBlock):
        elements = arraySlice.getSlotNamed('elements')
        size = arraySlice.getSlotNamed('size')

        resultElementType = aBlock.getType().getCanonicalResultType()
        resultArrayType = getBasicTypeNamed(Symbol('Array'))(resultElementType, size)

        collectedElements = resultArrayType.basicNewWithSequentialSlots(list(map(lambda index: aBlock(elements[Integer(index)]), range(size.asInteger()))))
        return collectedElements.asArraySlice()

    @primitiveNamed('arraySlice.collectWithIndex')
    def collectWithIndex(arraySlice, aBlock):
        elements = arraySlice.getSlotNamed('elements')
        size = arraySlice.getSlotNamed('size')

        resultElementType = aBlock.getType().getCanonicalResultType()
        indexType = aBlock.getType().getCanonicalArgumentTypes()[1]
        resultArrayType = getBasicTypeNamed(Symbol('Array'))(resultElementType, size)

        collectedElements = resultArrayType.basicNewWithSequentialSlots(list(map(lambda index: aBlock(elements[Integer(index)], indexType.basicNewWithValue(index)), range(size.asInteger()))))
        return collectedElements.asArraySlice()

    @primitiveNamed('arraySlice.do')
    def do(arraySlice, aBlock):
        elements = arraySlice.getSlotNamed('elements')
        size = arraySlice.getSlotNamed('size')

        result = getBasicTypeNamed(Symbol('Void')).basicNew()
        for i in range(size.asInteger()):
            result = aBlock(elements[Integer(i)])
        return result

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

    @primitiveNamed('object.runWithIn')
    def primitiveRunWithIn(self, selector, arguments, receiver):
        return self.runWithIn(EvaluationMachine.getActive(), selector, extractArraySliceElements(arguments), receiver)
