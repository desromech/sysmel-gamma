import typesystem

class SourceCollection:
    def convertIntoTargetSourceCollectionWith(self, bootstrapCompiler):
        raise Exception("convertIntoTargetSourceCollectionWith subclassResponsibility")

class EmptySourceCollection(SourceCollection):
    def __init__(self):
        pass

    def positionForRange(self, range):
        return EmptySourcePosition()

    def convertIntoTargetSourceCollectionWith(self, bootstrapCompiler):
        return bootstrapCompiler.getEmptySourceSourceCollection()

class StringSourceCollection(SourceCollection):
    def __init__(self, string, stringName):
        self.string = string
        self.stringName = stringName
        self.lineIndex = None

    def positionForRange(self, range):
        return SourceCollectionPosition(self, range)

    def getName(self):
        return self.stringName

    def getLineAndColumnForPosition(self, position):
        self.ensureLineIndexIsBuilt()
        return (1, 1)

    def ensureLineIndexIsBuilt(self):
        if self.lineIndex is not None:
            return

        self.lineIndex = []
        for i in range(len(self.string)):
            if self.string[i] == '\n':
                self.lineIndex.append(i)

    def convertIntoTargetSourceCollectionWith(self, bootstrapCompiler):
        return bootstrapCompiler.makeASTNodeWithSlots('SourceStringCollection',
            sourceString = typesystem.String(self.string),
            name = typesystem.String(self.stringName)
        )

class SourcePosition:
    def asSourcePosition(self):
        return self

    def isEmptySourcePosition(self):
        return False

    def convertIntoTargetSourcePositionWith(self, bootstrapCompiler):
        raise Exception("convertIntoTargetSourcePositionWith subclassResponsibility")

class EmptySourcePosition(SourcePosition):
    def mergeWith(self, other):
        return other

    def isEmptySourcePosition(self):
        return True

    def __str__(self):
        return 'unknown'

    def convertIntoTargetSourcePositionWith(self, bootstrapCompiler):
        return bootstrapCompiler.getEmptySourcePosition()

class SourceCollectionPosition(SourcePosition):
    def __init__(self, sourceCollection, range):
        self.sourceCollection = sourceCollection
        (self.start, self.stop) = range

    def mergeWith(self, other):
        if other.isEmptySourcePosition():
            return self
        assert self.sourceCollection == other.sourceCollection
        return SourceCollectionPosition(self.sourceCollection, (min(self.start, other.start), max(self.stop, other.stop)))

    def convertIntoTargetSourcePositionWith(self, bootstrapCompiler):
        startLine, startColumn = self.sourceCollection.getLineAndColumnForPosition(self.start)
        endLine, endColumn = self.sourceCollection.getLineAndColumnForPosition(self.stop)
        return bootstrapCompiler.makeASTNodeWithSlots('SourceStringPosition',
            sourceCollection = bootstrapCompiler.convertASTSourceCollection(self.sourceCollection),
            startPosition = typesystem.Integer(self.start),
            endPosition = typesystem.Integer(self.stop),
            startLine = typesystem.Integer(startLine),
            startColumn = typesystem.Integer(startColumn),
            endLine = typesystem.Integer(endLine),
            endColumn = typesystem.Integer(endColumn)
        )

    def __str__(self):
        startLine, startColumn = self.sourceCollection.getLineAndColumnForPosition(self.start)
        endLine, endColumn = self.sourceCollection.getLineAndColumnForPosition(self.stop)
        return '%s:%d.%d-%d.%d' % (self.sourceCollection.getName(), startLine, startColumn, endLine, endColumn)
