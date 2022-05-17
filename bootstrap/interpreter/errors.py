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