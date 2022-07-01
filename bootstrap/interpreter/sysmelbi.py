#!/usr/bin/env python3
import sys
import os
import os.path
from evalmachine import *
from environment import *
from errors import *

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
    except InterpreterError as error:
        print(error)
        sys.exit(1)
    evaluationMachine.finishPendingEvaluations()

if __name__ == '__main__':
    sysmelbiMain()