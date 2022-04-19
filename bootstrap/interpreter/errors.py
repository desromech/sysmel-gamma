class InterpreterError(Exception):
    pass

class InterpreterParseError(InterpreterError):
    pass

class InterpreterEvaluationError(InterpreterError):
    pass