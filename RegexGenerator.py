import re
import hashlib
import io
import argparse
from math import log
from math import ceil
from os import listdir
from os.path import isfile, isdir, join



class RegexReport:
    def __init__(self):
        #Key is scope number, value is array of regex in that scope
        self.regStr = {}
        #Each element is line of text in the detailed report
        self.reportText = []


class Corpus:
    def __init__(self, window):
      self.corpusFiles = {}
      self.corpusTerms = {}
      self.window = window
      self.regStrList = []
      self.corpusNegFiles = {}
      self.corpusNegTerms = {}
      

    def Update(self):
        self.UpdatePos()
        self.UpdateNeg()
    
    def UpdatePos(self):
        self.corpusTerms = {}
        for file in list(self.corpusFiles):
            for x in list(self.corpusFiles[file].terms):
                if( self.corpusFiles[file].terms[x].Value not in self.corpusTerms ):
                    self.corpusTerms[self.corpusFiles[file].terms[x].Value] = Term( self.corpusFiles[file].terms[x].Value )
                else:
                    self.corpusTerms[self.corpusFiles[file].terms[x].Value].Count = 1 + self.corpusTerms[self.corpusFiles[file].terms[x].Value].Count
                self.corpusTerms[self.corpusFiles[file].terms[x].Value].Neighbors =  self.corpusFiles[file].terms[x].Neighbors + self.corpusTerms[self.corpusFiles[file].terms[x].Value].Neighbors
                
    def UpdateNeg(self):
        self.corpusNegTerms = {}
        for file in list(self.corpusNegFiles):
            for x in list(self.corpusNegFiles[file].terms):
                if( self.corpusNegFiles[file].terms[x].Value not in self.corpusNegTerms ):
                    self.corpusNegTerms[self.corpusNegFiles[file].terms[x].Value] = Term( self.corpusNegFiles[file].terms[x].Value )
                else:
                    self.corpusNegTerms[self.corpusNegFiles[file].terms[x].Value].Count = 1 + self.corpusNegTerms[self.corpusNegFiles[file].terms[x].Value].Count
                self.corpusNegTerms[self.corpusNegFiles[file].terms[x].Value].Neighbors =  self.corpusNegFiles[file].terms[x].Neighbors + self.corpusNegTerms[self.corpusNegFiles[file].terms[x].Value].Neighbors

    def AddPosFile(self, fullName):
        f = open(fullName, "br")
        binary = f.read()
        sha256 = hashlib.sha256(binary).hexdigest()
        f = io.open(fullName, mode="r", encoding="utf-8")
        NewTermsList = f.read()
        CurFile = File(sha256,fullName)

        num = 0
        while ( num < ( len(NewTermsList) - 1) ):
            if( NewTermsList[num] not in CurFile.terms ):
                NewTerm  = Term( NewTermsList[num] )
                CurFile.terms[NewTermsList[num]] = NewTerm
            else:
                CurFile.terms[NewTermsList[num]].Count = 1 + CurFile.terms[NewTermsList[num]].Count


            #get neighbor words, before and after if applicapble
            prevNum = num - self.window
            nextNum = num + self.window
            while( prevNum < num):
                if( prevNum > 0  ):
                    # get the value of the 4-digit Unicode in \uhhhh format
                    UniHex = str("\\\\") + "x{" + str(format( ord(NewTermsList[prevNum]), '04x')) +"}"
                    position = prevNum - num
                    CurFile.terms[NewTermsList[num]].Neighbors.append((NewTermsList[prevNum],position,UniHex))
                prevNum = prevNum + 1
            while( nextNum > num ):
                if( nextNum < ( len(NewTermsList) - 1) ):
                    # get the value of the 4-digit Unicode in \uhhhh format
                    UniHex = str("\\\\") + "x{" + str(format( ord(NewTermsList[nextNum]), '04x')) +"}"
                    position = nextNum - num
                    CurFile.terms[NewTermsList[num]].Neighbors.append((NewTermsList[nextNum],position,UniHex))
                nextNum = nextNum - 1

            num = num + 1

        self.corpusFiles[CurFile.sha256] = CurFile
        f.close()
        NewTermsList = ""

    def AddNegFile(self, fullName):
        f = open(fullName, "br")
        binary = f.read()
        sha256 = hashlib.sha256(binary).hexdigest()
        f = io.open(fullName, mode="r", encoding="utf-8")
        NewTermsList = f.read()
        CurFile = File(sha256,fullName)

        num = 0
        while ( num < ( len(NewTermsList) - 1) ):
            if( NewTermsList[num] not in CurFile.terms ):
                NewTerm  = Term( NewTermsList[num] )
                CurFile.terms[NewTermsList[num]] = NewTerm
            else:
                CurFile.terms[NewTermsList[num]].Count = 1 + CurFile.terms[NewTermsList[num]].Count


            #get neighbor words, before and after if applicapble
            prevNum = num - self.window
            nextNum = num + self.window
            while( prevNum < num):
                if( prevNum > 0  ):
                    # get the value of the 4-digit Unicode in \uhhhh format
                    UniHex = str("\\\\") + "x{" + str(format( ord(NewTermsList[prevNum]), '04x')) +"}"
                    position = prevNum - num
                    CurFile.terms[NewTermsList[num]].Neighbors.append((NewTermsList[prevNum],position,UniHex))
                prevNum = prevNum + 1
            while( nextNum > num ):
                if( nextNum < ( len(NewTermsList) - 1) ):
                    # get the value of the 4-digit Unicode in \uhhhh format
                    UniHex = str("\\\\") + "x{" + str(format( ord(NewTermsList[nextNum]), '04x')) +"}"
                    position = nextNum - num
                    CurFile.terms[NewTermsList[num]].Neighbors.append((NewTermsList[nextNum],position,UniHex))
                nextNum = nextNum - 1

            num = num + 1

        self.corpusNegFiles[CurFile.sha256] = CurFile
        f.close()
        NewTermsList = ""

    def GenerateRegStrList(self):
        NegativeTerms = list(self.corpusNegTerms)
        for x in list(self.corpusTerms):     
            posSet = [None for x in range((self.window * 2 ) + 1) ]
            negSet = [None for x in range((self.window * 2 ) + 1) ]
            regexStr = ""
            num = -1 * self.window
            order = []
            if x in NegativeTerms:
                #Add the anchor value to the array
                negSet[0] = {"\\" + self.corpusNegTerms[x].UniHex: (self.corpusNegTerms[x].Value,0,"\\" + self.corpusNegTerms[x].UniHex)}
                for y in self.corpusNegTerms[x].Neighbors:
                    if( negSet[y[1]] == None ):
                        newDict = {}
                        newDict[y[2]] = 1
                        negSet[y[1]] = newDict
                    else:
                        if y[2] not in list(negSet[y[1]]):
                            negSet[y[1]][y[2]] = 1
                        else:
                            negSet[y[1]][y[2]] = negSet[y[1]][y[2]] + 1    
            
            #Add the key value to the array
            posSet[0] = {self.corpusTerms[x].UniHex: (self.corpusTerms[x].Value,0,self.corpusTerms[x].UniHex)}
            for y in self.corpusTerms[x].Neighbors:
                if( posSet[y[1]] == None ):
                    newDict = {}
                    newDict[y[2]] = 1
                    posSet[y[1]] = newDict
                else:
                    if y[2] not in list(posSet[y[1]]):
                        posSet[y[1]][y[2]] = 1
                    else:
                        posSet[y[1]][y[2]] = posSet[y[1]][y[2]] + 1
            
            while num <= self.window:
                order.append( num)
                num = num + 1
            badRegexStr = False
            for index in order:
                if posSet[index] != None:
                    sortedkeys = sorted(posSet[index], key=posSet[index].get, reverse=True)                 
                    regexStr = regexStr + "["
                    charAdded = 0
                    if index != 0:
                        for x in sortedkeys:
                            if negSet[index] != None and x not in list(negSet[index]):
                                regexStr = regexStr + x
                                charAdded = charAdded + 1
                            elif negSet[index] == None or negSet[index][x] == None:    
                                regexStr = regexStr + x
                                charAdded = charAdded + 1
                            else:
                                pass
                        if charAdded == 0:
                            badRegexStr = True
                        regexStr = regexStr + "]"
                    else:
                        regexStr = regexStr + list(posSet[index])[0]
                        regexStr = regexStr + "]"

                    #print( regexStr )
                    #print( index, len(list(posSet[index])) )
            if not badRegexStr:
                #print( regexStr )
                self.regStrList.append(regexStr)

    def GenerateRegexReport(self):
        self.Update()
        self.GenerateRegStrList()   

        #check if postitive files exist
        for x in list(self.corpusFiles):
            if not isfile(self.corpusFiles[x].fullName):
                print("ERROR: File no longer exists: " + self.corpusFiles[x].fullName )
                exit(-1)
        #check if negative  files exist
        for x in list(self.corpusNegFiles):
            if not isfile(self.corpusNegFiles[x].fullName):
                print("ERROR: File no longer exists: " + self.corpusNegFiles[x].fullName )
                exit(-1)

        regStr = {self.window : [] }
        reportText = []
        reportText.append("################ Begin Scope Size:" + str(self.window) + " ################")
        reportText.append("###### Begin Pre-Prune Test ######")
        posResults = {}
        posHits = {}
        negResults = {}
        negHits = {}
        badSet = []
        posScore = 0
        negScore = 0
        reportText.append("# Number of regStr in regStrList before pruning: " + str(len(self.regStrList)))
        for x in list(self.corpusFiles):
            fullName = self.corpusFiles[x].fullName
            
            reportText.append( "### Begin File: " +  fullName )
            f = io.open(fullName, mode="r", encoding="utf-8")
            text = f.read()
            num = 0
            score = 0
            while num < len(self.regStrList):
                pattern = re.compile(self.regStrList[num])
                patternScore = len(re.findall(pattern, text))
                if num not in list(posResults):
                    posResults[num] = patternScore
                else:
                    posResults[num] = posResults[num] + patternScore
                if num not in list(posHits):
                    posHits[num] = 1
                else:
                    posHits[num] = posHits[num] + 1
                reportText.append( "# regStr Score: " + str(patternScore) + " regStr: " + self.regStrList[num] )
                score = score + patternScore
                posScore = posScore + patternScore
                num = num + 1
            reportText.append( "# Overall Score: " + str(score) )
            reportText.append( "### End File: " +  fullName )

        for x in list(self.corpusNegFiles):
            fullName = self.corpusNegFiles[x].fullName
            reportText.append( "### Begin File: " +  fullName )
            f = io.open(fullName, mode="r", encoding="utf-8")
            text = f.read()
            num = 0
            score = 0
            while num < len(self.regStrList):
                pattern = re.compile(self.regStrList[num])
                patternScore = len(re.findall(pattern, text))
                if num not in list(negResults):
                    negResults[num] = patternScore
                else:
                    negResults[num] = negResults[num] + patternScore
                if num not in list(negHits):
                    negHits[num] = 1
                else:
                    negHits[num] = negHits[num] + 1
                reportText.append( "# regStr Score: " + str(patternScore) + " regStr: " + self.regStrList[num] )
                score = score + patternScore
                negScore = negScore + patternScore
                num = num + 1
            reportText.append( "# Overall Score: " + str(score) )
            reportText.append( "### End File: " +  fullName )
        reportText.append("###### End Pre-Prune Test ######")

        num = 0
        if posScore == 0:
            reportText.append("# Zero hits in the positive files for the regStr generated for this scope. Try again with a smaller scope value.")         
        else:
            hitTF = {}
            #Prune weak regStr 
            while num < len(self.regStrList):
                posTF = posResults[num] / posScore
                if negScore != 0:
                    negTF = negResults[num] / negScore
                else:
                    negTF = 0
                
                if negScore != 0 and posTF <= negTF:
                    badSet.append(num)
                elif negScore != 0 and posResults[num] <= negResults[num]:
                    badSet.append(num)
                else:
                    #Prune longer regStr that have same performance as a shorter regStr 
                    if posTF in list(hitTF):
                        if len(self.regStrList[hitTF[posTF]]) > len(self.regStrList[num]):
                            badSet.append(hitTF[posTF])
                            hitTF[posTF] = num
                        else:
                            badSet.append(num)
                    else:
                        hitTF[posTF] = num
                num = num + 1

            reportText.append("###### Begin Post-Prune Test ######")
            reportText.append("# Number of regStr in regStrList after pruning: " + str(len(self.regStrList) - len(badSet)))
            
            for x in list(self.corpusFiles):
                fullName = self.corpusFiles[x].fullName
                reportText.append( "### Begin File: " +  fullName )
                f = io.open(fullName, mode="r", encoding="utf-8")
                text = f.read()
                num = 0
                score = 0
                while num < len(self.regStrList):
                    if num not in badSet:
                        pattern = re.compile(self.regStrList[num])
                        patternScore = len(re.findall(pattern, text))
                        reportText.append( "# regStr Score: " + str(patternScore) + " regStr: " + self.regStrList[num] )
                        score = score + patternScore
                    num = num + 1
                reportText.append( "# Overall Score: " + str(score) )
                reportText.append( "### End File: " +  fullName )

            for x in list(self.corpusNegFiles):
                fullName = self.corpusNegFiles[x].fullName
                reportText.append( "### Begin File: " +  fullName )
                f = io.open(fullName, mode="r", encoding="utf-8")
                text = f.read()
                num = 0
                score = 0
                while num < len(self.regStrList):
                    if num not in badSet:
                        pattern = re.compile(self.regStrList[num])
                        patternScore = len(re.findall(pattern, text))
                        reportText.append( "# regStr Score: " + str(patternScore) + " regStr: " + self.regStrList[num] )
                        score = score + patternScore
                    num = num + 1
                reportText.append( "# Overall Score: " + str(score) )
                reportText.append( "### End File: " +  fullName )
            reportText.append("###### End Post-Prune Test ######")
        reportText.append("################ End Scope Size:" + str(self.window) + " ################")
        
        num = 0
        while num < len(self.regStrList):
            if num not in badSet:
                regStr[self.window].append(self.regStrList[num])
            num = num + 1
        return regStr, reportText



class File:
    def __init__(self, sha256, name):
      self.sha256 = sha256
      self.fullName = name
      self.terms = {}

    def __eq__(self, other):
        return self.sha256 == other.sha256
  


class Term:
    def __init__(self, Value ):
      self.Value = Value
      self.Neighbors = []
      self.Count = 1
      self.UniHex = str("\\\\") + "x{" + str(format( ord(Value), '04x')) +"}"
    
    def __eq__(self, other):
        return self.Value == other.Value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--positive', type=str, help='Directory containing files for the Positive set (what you want to detect)', required=True)
    parser.add_argument('-n', '--negative', type=str, help='Directory containing files for the Negative set (what you *dont* want to detect)', default="")
    parser.add_argument('-o', '--output', type=str, help='Output file name, where the training report and results will be sent. Appends output if file exists already.', required=True)
    parser.add_argument('-s', '--scope', type=int, help='Number of characters included before AND after the key character. A higher number in scope will increase RAM usage! Defaults to 3', default=3)
    parser.add_argument("-r", "--rerun", action="store_true", help="After first run, decrement the scope and re-run until scope is zero")
    parser.add_argument("-d", "--detail", action="store_true", help="Increase report output details, shows per regStr per file scores, file total scores, and results from before AND after pruning")
    parser.add_argument("-f", "--force", action="store_true", help="Force proceed when -s/--scope is greater than 5")
    args = parser.parse_args()

    #Validate supplied args
    if not isdir(args.positive):
        print("ERROR: Directory does not exist : " + args.positive )
        exit(-1)
    if args.negative !=  "" and not isdir(args.negative):
        print("ERROR: Directory does not exist : " + args.negative )
        exit(-1)
    if not args.force and args.scope > 5 :
        print("WARNING: scope is greater than 5 which will use more RAM, add -f/--force flag to proceed")
        exit(-2)
    if args.scope <= 0 :
        print("ERROR: scope is less than 1. Scope needs to be between 1 and 5, if greater than 5 add -f/--force flag to proceed")
        exit(-1)

    outputFile = open(args.output,"a+")
       

    #Create a new RegexReport for this run
    newReport = RegexReport()
    

    if args.rerun:
        runNum = args.scope
        minNum = 1
    else:
        runNum = args.scope
        minNum = args.scope
    
    while( runNum >= minNum ):
        #start with supplied window scope 
        NewCorpus = Corpus(runNum)

        mypath = args.positive
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        for fullName in onlyfiles:
            fullName = mypath + fullName
            NewCorpus.AddPosFile(fullName)
    
        if args.negative != "":
            mypath = args.negative
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            for fullName in onlyfiles:
                fullName = mypath + fullName
                NewCorpus.AddNegFile(fullName)
    
        curReport = NewCorpus.GenerateRegexReport()
    
        for x in curReport[1]:
            newReport.reportText.append(x)
        newReport.regStr[NewCorpus.window] = curReport[0][NewCorpus.window]
    
        runNum = runNum - 1

    #Write Report
    if args.detail:
        for line in newReport.reportText:
            outputFile.write(line + "\n")
    outputFile.write("############ Begin RegStr Output ############\n")
    for x in list(newReport.regStr):
        outputFile.write("###### Begin Scope Output: " + str(x) + " ######\n")
        for y in newReport.regStr[x]:
            outputFile.write(y + "\n")
        outputFile.write("###### End Scope Output: " + str(x) + " ######\n")     
    outputFile.write("############ End RegStr Output ############\n")




