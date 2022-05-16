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

class Dictionary(list, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('AnyDictionary'))

class PrimitiveMethod:
    def __init__(self, method):
        self.method = method

    def getType(self):
        return getBasicTypeNamed(Symbol('PrimitiveMethod'))

    def runWithIn(self, machine, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class BlockClosure(TypedValue):
    def __init__(self, node, environment):
        self.node = node
        self.environment = environment

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
        return self.node.evaluateClosureWithEnvironmentAndArguments(machine, self.environment, arguments)

    def asMemoizedBlockClosure(self):
        return MemoizedBlockClosure(self.node, self.environment)

    def asTemplatedBlockClosure(self):
        return TemplatedBlockClosure(self.node, self.environment)

class AbstractMemoizedBlockClosure(BlockClosure):
    def __init__(self, node, environment):
        super().__init__(node, environment)
        self.memoizationTable = {}

    def evaluateWithArguments(self, machine, arguments):
        if arguments in self.memoizationTable:
            return self.memoizationTable[arguments]

        result = super().evaluateWithArguments(machine, arguments)
        self.memoizationTable[arguments] = result
        return result

class MemoizedBlockClosure(AbstractMemoizedBlockClosure):
    def asMemoizedBlockClosure(self):
        return self

class TemplatedBlockClosure(AbstractMemoizedBlockClosure):
    def asTemplatedBlockClosure(self):
        return self

class TypeSchema:
    pass

class EmptyTypeSchema(TypeSchema):
    pass

class AbsurdTypeSchema(TypeSchema):
    pass

class PrimitiveTypeSchema(TypeSchema):
    def __init__(self, size, alignment):
        super().__init__()
        self.size = size
        self.alignment = alignment

class PrimitiveUnsignedIntegerTypeSchema(PrimitiveTypeSchema):
    pass

class PrimitiveSignedIntegerTypeSchema(PrimitiveTypeSchema):
    pass

class PrimitiveBooleanTypeSchema(PrimitiveTypeSchema):
    pass

class PrimitiveCharacterTypeSchema(PrimitiveTypeSchema):
    pass

class PrimitiveFloatTypeSchema(PrimitiveTypeSchema):
    pass

class SumTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        self.elementTypes = elementTypes

class ProductTypeSchema(TypeSchema):
    def __init__(self, elementTypes):
        self.elementTypes = elementTypes

class RecordTypeSchema(TypeSchema):
    def __init__(self, slots):
        self.slots = slots

class ArrayTypeSchema(TypeSchema):
    def __init__(self, elementType, bounds):
        self.elementType = elementType
        self.bounds = bounds

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

    def directTraits(self):
        return self.traits

    def lookupSelector(self, selector):
        return self.methodDict.get(selector, None)

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
        return String('')

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
        return MetaType(thisType = self, supertype = typeSupertype)

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

    def getMetaTypeRoot(self):
        return None

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

            (cls.newBooleanTypeWithSizeAndAlignment, 'newBooleanTypeWithSize:alignment:'),
            (cls.newUnsignedIntegerTypeWithSizeAndAlignment, 'newUnsignedIntegerTypeWithSize:alignment:'),
            (cls.newSignedIntegerTypeWithSizeAndAlignment, 'newSignedIntegerTypeWithSize:alignment:'),
            (cls.newCharacterTypeWithSizeAndAlignment, 'newCharacterTypeWithSize:alignment:'),
            (cls.newFloatTypeWithSizeAndAlignment, 'newFloatTypeWithSize:alignment:'),

            (cls.newGCClassWithSlots, 'newGCClassWithSlots:'),
            (cls.newGCClassWithSuperclassSlots, 'newGCClassWithSuperclass:slots:')
        ])

    def newAbsurdType(self):
        return SimpleType(schema=AbsurdTypeSchema())

    def newTrivialType(self):
        return SimpleType()

    def newProductType(self, elementTypes):
        return SimpleType(schema = ProductTypeSchema(elementTypes))

    def newSumTypeWith(self, elementTypes):
        return SimpleType(schema = SumTypeSchema(elementTypes))

    def newRecordTypeWith(self, slots):
        return SimpleType(schema = RecordTypeSchema(slots))

    def newArrayTypeForWithBounds(self, elementType, bounds):
        return SimpleType(schema = ArrayTypeSchema(elementType, bounds))

    def newGCClassWithSuperclassSlots(self, supertype, instanceVariable):
        return SimpleType(supertype = supertype, schema = GCClassTypeSchema(instanceVariable))

    def newGCClassWithSlots(self, instanceVariable):
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
