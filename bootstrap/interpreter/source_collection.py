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
        bestLineFound = 0
        lowerBound = 0
        upperBound = len(self.lineIndex)
        while lowerBound < upperBound:
            middle = (lowerBound + upperBound) // 2
            middlePosition = self.lineIndex[middle]
            if middlePosition <= position:
                bestLineFound = middle
                lowerBound = middle + 1
            else:
                upperBound = middle 

        return (bestLineFound + 1, position - self.lineIndex[bestLineFound] + 1)

    def ensureLineIndexIsBuilt(self):
        if self.lineIndex is not None:
            return

        self.lineIndex = []
        self.lineIndex.append(0)
        for i in range(len(self.string)):
            if self.string[i] == '\n':
                self.lineIndex.append(i + 1)

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
            startPosition = bootstrapCompiler.convertSize(self.start),
            endPosition = bootstrapCompiler.convertSize(self.stop),
            startLine = bootstrapCompiler.convertSize(startLine),
            startColumn = bootstrapCompiler.convertSize(startColumn),
            endLine = bootstrapCompiler.convertSize(endLine),
            endColumn = bootstrapCompiler.convertSize(endColumn)
        )

    def __str__(self):
        startLine, startColumn = self.sourceCollection.getLineAndColumnForPosition(self.start)
        endLine, endColumn = self.sourceCollection.getLineAndColumnForPosition(self.stop)
        return '%s:%d.%d-%d.%d' % (self.sourceCollection.getName(), startLine, startColumn, endLine, endColumn)
