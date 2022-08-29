class InterpreterError(Exception):
    pass

class InterpreterErrorWithSourcePosition(InterpreterError):
    def __init__(self, sourcePosition, errorMessage, previousError = None):
        self.sourcePosition = sourcePosition
        self.errorMessage = errorMessage
        self.previousError = previousError

        super().__init__(self.formatDescription())

    def formatDescription(self):
        fullDescription = '%s: %s' % (str(self.sourcePosition), self.errorMessage)
        if self.previousError is not None:
            fullDescription = '%s\n%s' % (str(self.previousError), fullDescription)
        return fullDescription

class InterpreterStackTraceError(InterpreterErrorWithSourcePosition):
    def formatDescription(self):
        return '%s\n\t%s %s.' %(str(self.previousError), self.errorMessage, self.sourcePosition)

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