#!/usr/bin/env python3
import sys
import os
import os.path
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
    for scriptToEvaluate in scriptsToEvaluate:
        try:
            scriptEnvironment = bootstrapCompiler.makeScriptEvaluationEnvironment()

            if scriptToEvaluate == '-':
                scriptFilename = 'stdin'
                scriptDirectory = os.path.dirname(os.path.abspath(os.getcwd()))
                scriptEnvironment.evaluateScriptFile(sys.stdin, scriptFilename, scriptDirectory)
            else:
                scriptFilename = os.path.abspath(scriptToEvaluate)
                scriptDirectory = os.path.dirname(scriptFilename)
                with open(scriptFilename, 'r') as scriptFile:
                    scriptEnvironment.evaluateScriptFile(scriptFile, scriptFilename, scriptDirectory)
        except InterpreterError as error:
            print(error)
            sys.exit(1)


if __name__ == '__main__':
    sysmelbiMain()