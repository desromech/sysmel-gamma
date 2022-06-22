from queue import Empty

from numpy import record
from errors import *

BasicTypeEnvironment = None

def setActiveBasicTypeEnvironment(basicTypeEnvironment):
    global BasicTypeEnvironment
    BasicTypeEnvironment = basicTypeEnvironment

def getBasicTypeNamed(symbol):
    return BasicTypeEnvironment[symbol]

class SymbolBinding:
    def getSymbolBindingReferenceValue(self):
        raise NotImplementedError()

class SymbolImmutableValueBinding(SymbolBinding):
    def __init__(self, value):
        self.value = value

    def getSymbolBindingReferenceValue(self):
        return self.value

class ValueInterface:
    def performWithArguments(self, machine, selector, arguments):
        raise NotImplementedError()

    def getSymbolBindingReferenceValue(self):
        return self

    def onGlobalBindingWithSymbolAdded(self, symbol):
        pass

    def yourself(self):
        return self

    def asBooleanValue(self):
        raise NonBooleanEvaluableValue()

class TypeInterface:
    def runWithIn(self, machine, selector, arguments, receiver):
        raise NotImplementedError()

class TypedValue(ValueInterface):
    def getType(self):
        raise NotImplementedError()

    def performWithArguments(self, machine, selector, arguments):
        return self.getType().runWithIn(machine, selector, arguments, self)

class Integer(int, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Integer'))

class Character(int, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Character'))

class Float(float, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Float'))

class String(str, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('String'))

class Symbol(str, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Symbol'))

class Array(list, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('AnyArrayList'))

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

    def __str__(self) -> str:
        return str(self.key) + ' : ' + str(self.value)

    def __repr__(self) -> str:
        return repr(self.key) + ' : ' + repr(self.value)

class Dictionary(list, TypedValue):

    @classmethod
    def fromDict(cls, d):
        return cls(map(lambda pair: Association(pair[0], pair[1]), d.items()))

    def getType(self):
        return getBasicTypeNamed(Symbol('AnyDictionary'))

    def getHashTable(self):
        if not hasattr(self, 'hashTable'):
            self.hashTable = {}
            for assoc in self:
                self.hashTable[assoc.getKey()] = assoc.getValue()
        return self.hashTable

    def at(self, key):
        return self.getHashTable()[key]

class PrimitiveMethod:
    def __init__(self, method):
        self.method = method

    def getType(self):
        return getBasicTypeNamed(Symbol('PrimitiveMethod'))

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class TypeSchemaPrimitiveMethod:
    def __init__(self, method):
        self.method = method

    def getType(self):
        return getBasicTypeNamed(Symbol('TypeSchemaPrimitiveMethod'))

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class BlockClosure(TypedValue):
    def __init__(self, node, environment):
        self.node = node
        self.environment = environment
        self.name = None

    def performWithArguments(self, machine, selector, arguments):
        if selector == '()':
            return self.evaluateWithArguments(machine, arguments)
        elif selector == 'memoized':
            return self.asMemoizedBlockClosure()
        elif selector == 'templated':
            return self.asTemplatedBlockClosure()
        return super().performWithArguments(machine, selector, arguments)

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.evaluateWithArguments(machine, [receiver] + arguments)

    def evaluateWithArguments(self, machine, arguments):
        return self.applyResultTransform(machine, self.node.evaluateClosureWithEnvironmentAndArguments(machine, self.environment, arguments))

    def asMemoizedBlockClosure(self):
        return MemoizedBlockClosure(self.node, self.environment)

    def asTemplatedBlockClosure(self):
        return TemplatedBlockClosure(self.node, self.environment)

    def applyResultTransform(self, machine, result):
        return result

    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def __repr__(self) -> str:
        if self.name is not None:
            return self.name
        return super().__repr__()

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
        result.onGlobalBindingWithSymbolAdded(Symbol(valueName))

class TypeSchema:
    def __init__(self):
        self.methodDict = {}
        self.metaTypeMethodDict = {}
        self.buildPrimitiveMethodDictionary()

    def isDefaultConstructible(self):
        return False

    def buildPrimitiveMethodDictionary(self):
        pass

    def lookupPrimitiveWithSelector(self, selector):
        if selector in self.methodDict:
            return self.methodDict[selector]
        return None

    def lookupMetaTypePrimitiveWithSelector(self, selector):
        if selector in self.metaTypeMethodDict:
            return self.metaTypeMethodDict[selector]
        return None

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

class TrivialTypedValue(TypedValue):
    def __init__(self, type):
        self.type = type
        self.globalBindingName = None

    def getType(self):
        return self.type

    def onGlobalBindingWithSymbolAdded(self, bindingName):
        self.globalBindingName = bindingName

    def __repr__(self):
        if self.globalBindingName is not None:
            return self.globalBindingName
        return str(self.type) + '()'

class OpaqueTypeSchema(TypeSchema):
    pass

class EmptyTypeSchema(TypeSchema):
    def __init__(self):
        super().__init__()
        self.uniqueInstance = None

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        if self.uniqueInstance is None:
            self.uniqueInstance = TrivialTypedValue(valueType)
        return self.uniqueInstance

    def isTrivialTypeSchema(self):
        return True

class AbsurdTypeSchema(TypeSchema):
    pass

class PrimitiveNumberTypeValue(TypedValue):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def getType(self):
        return self.type

    def __repr__(self):
        return '%s(%s)' % (str(self.type), str(self.value))

class PrimitiveTypeSchema(TypeSchema):
    def __init__(self, size, alignment):
        super().__init__()
        self.size = size
        self.alignment = alignment

class PrimitiveNumberTypeSchema(PrimitiveTypeSchema):
    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue)
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return self.basicNewWithValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return PrimitiveNumberTypeValue(valueType, self.normalizeValueToValidRange(initialValue))

    def normalizeValueToValidRange(self, value):
        return value

class PrimitiveIntegerTypeSchema(PrimitiveNumberTypeSchema):
    def __init__(self, size, alignment):
        super().__init__(size, alignment)
        self.memoryBits = size*8
        self.memoryBitMask = (1<<(self.memoryBits)) - 1

    def normalizeValueToValidRange(self, value):
        return int(value) & self.memoryBitMask

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

class PrimitiveCharacterTypeSchema(PrimitiveIntegerTypeSchema):
    pass

class PrimitiveFloatTypeSchema(PrimitiveNumberTypeSchema):
    def normalizeValueToValidRange(self, value):
        return float(value)

class SumTypeValue(TypedValue):
    def __init__(self, type, typeSelector, wrappedValue):
        self.type = type
        self.typeSelector = typeSelector
        self.wrappedValue = wrappedValue

    def asBooleanValue(self):
        if self.type.isTypeTheoryBoolean():
            return self.typeSelector == 1
        super().asBooleanValue()

    def getType(self):
        return self.type

    def __repr__(self) -> str:
        return '%s(%d: %s)' % (repr(self.type), self.typeSelector, repr(self.wrappedValue))

class SumTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        super().__init__()
        self.elementTypes = elementTypes

    def isDefaultConstructible(self):
        return self.elementTypes[0].isDefaultConstructible()

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue)
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, sumType):
        return SumTypeValue(sumType, 0, self.elementTypes[0].basicNew())

    def basicNewWithValue(self, sumType, value):
        wrappedValueType = value.getType()
        return SumTypeValue(sumType, self.elementTypes.index(wrappedValueType), value)

    def isTypeTheoryBoolean(self):
        return len(self.elementTypes) == 2 and self.elementTypes[0].hasTrivialTypeSchema() and self.elementTypes[1].hasTrivialTypeSchema()

class ProductTypeValue(TypedValue):
    def __init__(self, type, elements):
        self.type = type
        self.elements = elements

    def getType(self):
        return self.type

    def __repr__(self) -> str:
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

class ProductTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        super().__init__()
        self.elementTypes = elementTypes
        self.isDefaultConstructibleCache = None

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        self.metaTypeMethodDict[Symbol('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithSequentialSlots)
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
        self.slots = slots
        self.allSlots = slots
        if supertypeSchema is not None:
            self.allSlots = supertypeSchema.allSlots + self.allSlots
        self.slotNameDictionary = {}
        self.slotNameTable = list(map(lambda s: s.key, self.allSlots))

        super().__init__(list(map(lambda s: s.value, self.allSlots)))

        slotIndex = 0
        for assoc in self.allSlots:
            slotName = assoc.key
            self.slotNameDictionary[slotName] = slotIndex
            slotIndex += 1


    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        self.metaTypeMethodDict[Symbol('basicNewWithSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithSequentialSlots)
        self.metaTypeMethodDict[Symbol('basicNewWithNamedSlots:')] = TypeSchemaPrimitiveMethod(self.basicNewWithNamedSlots)
        return super().buildPrimitiveMethodDictionary()

    def basicNewWithNamedSlots(self, recordType, namedSlots):
        linearSlots = [None,] * len(self.allSlots)
        for assoc in namedSlots:
            linearSlots[self.slotNameDictionary[assoc.getKey()]] = assoc.getValue()

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

class ArrayTypeSchema(TypeSchema):
    def __init__(self, elementType, bounds):
        super().__init__()
        self.elementType = elementType
        self.bounds = bounds

class PointerTypeValue(TypedValue):
    def __init__(self, type, value, baseIndex = 0):
        self.type = type
        self.value = value
        self.baseIndex = baseIndex

    def getType(self):
        return self.type

    def __repr__(self):
        return '%s(%s:%d)' % (str(self.type), str(self.value), self.baseIndex)

class PointerTypeSchema(TypeSchema):
    def __init__(self, elementType):
        super().__init__()
        self.elementType = elementType

    def isDefaultConstructible(self):
        return True

    def buildPrimitiveMethodDictionary(self):
        self.metaTypeMethodDict[Symbol('basicNew')] = TypeSchemaPrimitiveMethod(self.basicNew)
        self.metaTypeMethodDict[Symbol('basicNew:')] = TypeSchemaPrimitiveMethod(self.basicNewWithValue)
        return super().buildPrimitiveMethodDictionary()

    def basicNew(self, valueType):
        return PointerTypeValue(valueType, 0)

    def basicNewWithValue(self, valueType, initialValue):
        return PointerTypeValue(valueType, initialValue)

class GCClassTypeSchema(RecordTypeSchema):
    pass

class BehaviorType(TypedValue, TypeInterface):
    def __init__(self, name = None, supertype = None, traits = [], schema = EmptyTypeSchema(), methodDict = {}):
        self.name = name
        self.methodDict = methodDict
        self.supertype = supertype
        self.traits = traits
        self.schema = schema
        self.type = None

    def onGlobalBindingWithSymbolAdded(self, symbol):
        if self.name is None:
            self.name = symbol

    def performWithArguments(self, machine, selector, arguments):
        return super().performWithArguments(machine, selector, arguments)

    def directTraits(self):
        return self.traits

    def lookupSelector(self, selector):
        found = self.methodDict.get(selector, None)
        if found is not None:
            return found

        ## Check a schema inserted primitive.
        found = self.schema.lookupPrimitiveWithSelector(selector)
        if found is not None:
            return found
        return None

    def lookupSelectorRecursively(self, selector):
        ## Check in the local method dictionary.
        found = self.lookupSelector(selector)
        if found is not None:
            return found

        ## Find in a direct trait.
        for trait in self.directTraits():
            found = trait.lookupSelector(found)
            if found is not None:
                return found

        ##  Find in the supertype.
        if self.supertype is not None:
            return self.supertype.lookupSelectorRecursively(selector)
        return None

    def runWithIn(self, machine, selector, arguments, receiver):
        method = self.lookupSelectorRecursively(selector)
        if method is None:
            raise DoesNotUnderstand('%s does not understand message %s' % (str(receiver), repr(selector)))
        return method.runWithIn(machine, selector, arguments, receiver)

    def addMethodWithSelector(self, method, selector):
        self.methodDict[selector] = method

    def withSelectorAddMethod(self, selector, method):
        self.methodDict[selector] = method

    def addMethodsWithSelectors(self, methodsWithSelector):
        for method, selector in methodsWithSelector:
            self.addMethodWithSelector(method, Symbol(selector))

    def addPrimitiveMethodsWithSelectors(self, methodsWithSelector):
        for method, selector in methodsWithSelector:
            self.addMethodWithSelector(PrimitiveMethod(method), Symbol(selector))

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

    def __str__(self):
        return self.getName()

    def __repr__(self):
        return self.getName()

    def addMetaTypeRootMethods(self):
        cls = self.__class__
        self.addPrimitiveMethodsWithSelectors([
            (cls.withSelectorAddMethod, 'withSelector:addMethod:'),
        ])

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

    def hasTrivialTypeSchema(self):
        return self.schema.isTrivialTypeSchema()

    def isTypeTheoryBoolean(self):
        return self.schema.isTypeTheoryBoolean()

    def isDefaultConstructible(self):
        return self.schema.isDefaultConstructible()

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

    def lookupSelector(self, selector):
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
            return String(self.thisType.getName() + ' type')
        return super().getName()

class SimpleType(BehaviorType):
    pass

class TypeBuilder(BehaviorTypedObject):
    def __init__(self):
        super().__init__()

    @classmethod
    def initializeBehaviorType(cls, type):
        BehaviorTypedObject.initializeBehaviorType(type)
        type.addPrimitiveMethodsWithSelectors([
            (cls.newAbsurdType, 'newAbsurdType'),
            (cls.newTrivialType, 'newTrivialType'),
            (cls.newProductType, 'newProductTypeWith:'),
            (cls.newSumTypeWith, 'newSumTypeWith:'),
            (cls.newRecordTypeWith, 'newRecordTypeWith:'),
            (cls.newArrayTypeForWithBounds, 'newArrayTypeFor:withBounds:'),
            (cls.newPointerTypeFor, 'newPointerTypeFor:'),

            (cls.newBooleanTypeWithSizeAndAlignment, 'newBooleanTypeWithSize:alignment:'),
            (cls.newUnsignedIntegerTypeWithSizeAndAlignment, 'newUnsignedIntegerTypeWithSize:alignment:'),
            (cls.newSignedIntegerTypeWithSizeAndAlignment, 'newSignedIntegerTypeWithSize:alignment:'),
            (cls.newCharacterTypeWithSizeAndAlignment, 'newCharacterTypeWithSize:alignment:'),
            (cls.newFloatTypeWithSizeAndAlignment, 'newFloatTypeWithSize:alignment:'),

            (cls.newGCClassWithSlots, 'newGCClassWithSlots:'),
            (cls.newGCClassWithSuperclassSlots, 'newGCClassWithSuperclass:slots:'),
            (cls.newGCClassWithPublicSlots, 'newGCClassWithPublicSlots:'),
            (cls.newGCClassWithSuperclassPublicSlots, 'newGCClassWithSuperclass:publicSlots:')
        ])

    def newAbsurdType(self):
        return SimpleType(schema = AbsurdTypeSchema())

    def newTrivialType(self):
        return SimpleType(schema = EmptyTypeSchema())

    def newProductType(self, elementTypes):
        if len(elementTypes) == 0:
            return self.newTrivialType()
        return SimpleType(schema = ProductTypeSchema(elementTypes))

    def newSumTypeWith(self, elementTypes):
        return SimpleType(schema = SumTypeSchema(elementTypes))

    def newRecordTypeWith(self, slots):
        return SimpleType(schema = RecordTypeSchema(slots))

    def newArrayTypeForWithBounds(self, elementType, bounds):
        return SimpleType(schema = ArrayTypeSchema(elementType, bounds))

    def newPointerTypeFor(self, elementType):
        return SimpleType(schema = PointerTypeSchema(elementType))

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
