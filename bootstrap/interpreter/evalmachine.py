ActiveEvaluationMachine = None

class EvaluationMachine:
    def __init__(self):
        self.pendingEvaluations = []

    def addPendingEvaluation(self, pendingEvaluation):
        self.pendingEvaluations.append(pendingEvaluation)

    def finishPendingEvaluations(self):
        while len(self.pendingEvaluations) > 0:
            self.pendingEvaluations.pop(0)()

    @classmethod
    def getActive(self):
        return ActiveEvaluationMachine

    def makeActive(self):
        global ActiveEvaluationMachine
        ActiveEvaluationMachine = self