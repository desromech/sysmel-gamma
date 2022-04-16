class SourceCollection:
    pass

class EmptySourceCollection(SourceCollection):
    def __init__(self):
        pass

    def positionForRange(self, range):
        return EmptySourcePosition()

class StringSourceCollection(SourceCollection):
    def __init__(self, string, stringName):
        self.string = string
        self.stringName = stringName

    def positionForRange(self, range):
        return SourceCollectionPosition(self, range)

class SourcePosition:
    def asSourcePosition(self):
        return self

    def isEmptySourcePosition(self):
        return False

class EmptySourcePosition(SourcePosition):
    def mergeWith(self, other):
        return other

    def isEmptySourcePosition(self):
        return True

class SourceCollectionPosition(SourcePosition):
    def __init__(self, sourceCollection, range):
        self.sourceCollection = sourceCollection
        (self.start, self.stop) = range

    def mergeWith(self, other):
        if other.isEmptySourcePosition():
            return self
        assert self.sourceCollection == other.sourceCollection
        return SourceCollectionPosition(self.sourceCollection, (min(self.start, other.start), max(self.stop, other.stop)))
