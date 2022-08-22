#!/usr/bin/env python3
import sys
import os
import os.path
from evalmachine import *
from environment import *
from errors import *

sys.setrecursionlimit(50000)

def printHelp():
    print('sysmelbi.py <scripts to evaluate> -- <script arguments>')

def sysmelbiMain():
    scriptsToEvaluate = []
    i = 1
    hasSeenLastInterpreterArgument = False
    scriptArguments = []

    while i < len(sys.argv) and not hasSeenLastInterpreterArgument:
        arg = sys.argv[i]
        if arg == '--':
            hasSeenLastInterpreterArgument = True
        elif arg == '-sources':
            i += 1
            listFileName = sys.argv[i]
            listFileNameDirectory = os.path.dirname(listFileName)
            with open(listFileName, 'r') as sourceListFile:
                for fileName in sourceListFile:
                    fileName = fileName.strip()
                    if len(fileName) == 0:
                        continue
                    scriptsToEvaluate.append(os.path.join(listFileNameDirectory, fileName))
        elif len(arg) and arg.startswith('-'):
            pass
        else:
            scriptsToEvaluate.append(arg)
        i = i + 1

    if len(scriptsToEvaluate) == 0:
        return printHelp()
    
    #print(scriptsToEvaluate)
    bootstrapCompiler = BootstrapCompiler()
    bootstrapCompiler.activate()
    evaluationMachine = EvaluationMachine()
    evaluationMachine.makeActive()
    try:
        for scriptToEvaluate in scriptsToEvaluate:
            scriptEnvironment = bootstrapCompiler.makeScriptEvaluationScope()

            if scriptToEvaluate == '-':
                scriptFilename = 'stdin'
                scriptDirectory = os.path.dirname(os.path.abspath(os.getcwd()))
                scriptEnvironment.evaluateScriptFile(sys.stdin, scriptFilename, scriptDirectory)
            else:
                scriptFilename = os.path.abspath(scriptToEvaluate)
                scriptDirectory = os.path.dirname(scriptFilename)
                with open(scriptFilename, 'r') as scriptFile:
                    scriptEnvironment.evaluateScriptFile(evaluationMachine, scriptFile, scriptFilename, scriptDirectory)
        evaluationMachine.finishPendingEvaluations()
    except InterpreterError as error:
        print(error)
        sys.exit(1)

if __name__ == '__main__':
    sysmelbiMain()