class InterpreterError(Exception):
    pass

class InterpreterErrorWithSourcePosition(InterpreterError):
    def __init__(self, sourcePosition, errorMessage):
        self.sourcePosition = sourcePosition
        super().__init__('%s: %s' % (str(sourcePosition), errorMessage))

class InterpreterParseError(InterpreterErrorWithSourcePosition):
    pass

class InterpreterSemanticAnalysisError(InterpreterErrorWithSourcePosition):
    pass

class InterpreterEvaluationError(InterpreterErrorWithSourcePosition):
    pass

class InterpreterEvaluationCatchedError(InterpreterErrorWithSourcePosition):
    def __init__(self, sourcePosition, catchedError, strackTrace):
        self.catchedError = catchedError
        super().__init__(sourcePosition, 'error catched during evaluation:\n%s\n%s' % (str(catchedError), strackTrace))

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