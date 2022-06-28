ActiveEvaluationMachine = None

class EvaluationMachine:
    def __init__(self):
        pass

    def finishPendingEvaluations(self):
        pass

    @classmethod
    def getActive(self):
        return ActiveEvaluationMachine

    def makeActive(self):
        global ActiveEvaluationMachine
        ActiveEvaluationMachine = self