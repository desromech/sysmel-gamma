from parser import parseString

class IdentifierLookupScope:
    def __init__(self, parentScope):
        self.parentScope = parentScope

    def lookupSymbol(self, symbol):
        return None

    def lookupSymbolRecursively(self, symbol):
        result = self.lookupSymbol(symbol)
        if result is not None:
            return result
        elif self.parentScope is not None:
            return self.parentScope.lookupSymbolRecursively(symbol)
        else:
            return None

class LexicalScope(IdentifierLookupScope):
    def __init__(self, parentScope):
        super().__init__(parentScope)
        self.symbolTable = {}

    def setSymbolValue(self, symbol, value):
        self.symbolTable[symbol] = value

    def lookupSymbol(self, symbol):
        return self.symbolTable.get(symbol, None)

class TopLevelEnvironment(LexicalScope):
    def __init__(self, parentScope = None):
        super().__init__(parentScope)

class ScriptEvaluationEnvironment(LexicalScope):
    def __init__(self, parentScope):
        super().__init__(parentScope)

    def evaluateScriptFile(self, scriptFile, scriptFilename, scriptDirectory):
        self.setSymbolValue('__CurrentScriptFilename__', scriptFilename)
        self.setSymbolValue('__CurrentScriptDirectory__', scriptDirectory)
        scriptSource = scriptFile.read()
        parseTree = parseString(scriptSource, scriptFilename)
        return parseTree.evaluateWithEnvironment(self)