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
    def performWithArguments(self, selector, arguments):
        raise NotImplementedError()

    def getSymbolBindingReferenceValue(self):
        return self

class TypeInterface:
    def runWithIn(self, selector, arguments, receiver):
        raise NotImplementedError()

class TypedValue(ValueInterface):
    def getType(self):
        raise NotImplementedError()

    def performWithArguments(self, selector, arguments):
        return self.getType().runWithIn(selector, arguments, self)

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
        return getBasicTypeNamed(Symbol('Array'))

class Association(TypedValue):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def getType(self):
        return getBasicTypeNamed(Symbol('Association'))

class Dictionary(list, TypedValue):
    def getType(self):
        return getBasicTypeNamed(Symbol('Dictionary'))

class PrimitiveMethod:
    def __init__(self, method):
        self.method = method

    def getType(self):
        return getBasicTypeNamed(Symbol('PrimitiveMethod'))

    def runWithIn(self, selector, arguments, receiver):
        return self.method(receiver, *arguments)

class BlockClosure:
    def __init__(self, node, environment):
        self.node = node
        self.environment = environment

    def runWithIn(self, selector, arguments, receiver):
        return self.node.evaluateClosureWithEnvironmentAndArguments(self.environment, [receiver] + arguments)

class TypeSchema:
    pass

class GCClassTypeSchema:
    def __init__(self, instanceVariables):
        self.instanceVariables = instanceVariables

class EmptyTypeSchema(TypeSchema):
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

class BehaviorType(TypedValue, TypeInterface):
    def __init__(self, name = None, supertype = None, traits = [], schema = None, methodDict = {}):
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

    def runWithIn(self, selector, arguments, receiver):
        method = self.lookupSelectorRecursively(selector)
        if method is None:
            raise DoesNotUnderstand('%s does not understand message %s' % (str(receiver), repr(selector)))
        return method.runWithIn(selector, arguments, receiver)

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
