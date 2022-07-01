class InterpreterError(Exception):
    pass

class InterpreterParseError(InterpreterError):
    pass

class InterpreterEvaluationError(InterpreterError):
    pass

class DoesNotUnderstand(InterpreterError):
    pass

class SubclassResponsibility(InterpreterError):
    pass

class PrimitiveFailed(InterpreterError):
    pass

class NonInstanceableType(InterpreterError):
    pass

class NonBooleanEvaluableValue(InterpreterError):
    pass

class MissingSlotsForInstancingType(InterpreterError):
    pass

class CannotCoerceValueToType(InterpreterError):
    pass

class SumTypeNotMatched(InterpreterError):
    pass