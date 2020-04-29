# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:08:28 2020

@author: m1552
"""
import copy

#Enter the system as an automata, the unoberved event will be named "uo".
#There are an simple example automata.
events = ['a','b','c','d']
states = ["q1","q2","q3","q4"]
startState = []
transition = [{'a':{"q1"},'b':{"q1"},'c':{"q1"},'d':{"q4"},'uo':set()},
             {'a':{"q2"},'b':{"q1"},'c':{"q2"},'d':{"q2"},'uo':set()},
             {'a':{"q3"},'b':{"q3"},'c':{"q2"},'d':{"q3"},'uo':set()},
             {'a':{"q3"},'b':{"q4"},'c':{"q4"},'d':{"q4"},'uo':set()}]


#Build the state table for the automata
state_table = {}
j = 0
for i in states:
    state_table.update({i: transition[j]})
    j+=1

#Give the specification point
Tspec = []

#Calculate the unobservable reach for a state, and store it in the state_table
def UnobservableReach(state, state_table):
    stateTable = copy.deepcopy(state_table)
    for i in state:
        States = list(stateTable[i]['uo'])
        for x in States:
            States.remove(x)
            for y in stateTable[x]['uo']:
                if y not in stateTable[i]['uo'] and y != i:
                    stateTable[i]['uo'].add(y)
                    States.append(y)
    return stateTable
    

#Generate the DFA state table for the automata
def getNewTransition(current_states, events, state_table, state_table_DFA, state_DFA, mold):
    #The dictionary to store the transition of the current_state point
    theState = {}
    for i in events:
        theState.update({i:set()})
 
    # Loop to get all the point that the current_state point can access for every events
    for i in current_states:
        for j in events:
            for state in state_table[i][j]:
                theState[j].add(state)
                for k in state_table[state]['uo']:
                    theState[j].add(k)
                    
    if mold == "observer":
        state_table_DFA.update({current_states : theState})
        #Add the the children of the current_state to the set 
        #if they are not in the states set
        for i in events:
            if len(theState[i]) > 1 and tuple(sorted(list(theState[i]))) not in state_DFA:
                state_DFA.append(tuple(sorted(list(theState[i]))))
            elif len(theState[i]) == 1 and tuple(theState[i]) not in state_DFA:
                state_DFA.append(tuple(theState[i]))
    elif mold == "detector":
        #Build state pairs for the point whose length is more than 2,
        #and the state pairs will be the new children for the current_state
        for i in events:
            if len(theState[i]) > 2:
                index = 0
                stateList = sorted(list(theState[i]))
                theState[i].clear()#Clear the old children
                
                #Nest loop to generate state pair
                while index < len(stateList) - 1:
                    fState = stateList[index]
                    nextIndex = index + 1
                    while nextIndex < len(stateList):
                        sState = stateList[nextIndex]
                        statePair = (fState,sState)
                        theState[i].add(statePair)#Build the new children
                        if statePair not in state_DFA:
                            #And add the the children of the current_state to the set 
                            #if they are not in the states set
                            state_DFA.append(statePair)
                        nextIndex += 1
                    index += 1
            elif len(theState[i]) > 0:
                #And add the the children of the current_state to the set 
                #if they are not in the states set
                if tuple(sorted(list(theState[i]))) not in state_DFA:
                    state_DFA.append(tuple(sorted(list(theState[i]))))
        state_table_DFA.update({current_states : theState})
                

#Method to get the observer and detector, the parameter 'mold' indicate which you want to get
#(The mold should be 'observer' or 'detector')
def dfaGenerate(states, events, state_table, startState, mold):
    state_table_DFA = {}
    #Determine the startState
    if startState:
        for i in startState:
            for j in state_table[i]['uo']:
                startState.append(j)
        current_states = tuple(startState)
    else:
        current_states = tuple(states)
    state_DFA = [current_states]
    
    #Build the DFA state table
    while(current_states):
        i = state_DFA.index(current_states)+1
        getNewTransition(current_states, events, state_table, state_table_DFA, state_DFA, mold)
        if i < len(state_DFA):
            current_states = state_DFA[i]
        else:
            current_states = None
    return state_table_DFA


#Generate a table for calculating the SCC
def TableForScc(state_table_DFA, events, mold):
    sccTable = {}
    states = state_table_DFA.keys()
    
    #Build a table which map the point to all its children no matter the event is
    if mold == "observer":
        for i in states:
            sccTable.update({i:set()})
            for j in events:
                if state_table_DFA[i][j]:
                    sccTable[i].add(tuple(sorted(list(state_table_DFA[i][j]))))     
    elif mold == "detector":
        for i in states:
            sccTable.update({i:set()})
            for j in events:
                if len(state_table_DFA[i][j])>2:
                    for k in state_table_DFA[i][j]:
                        sccTable[i].add(k)
                elif state_table_DFA[i][j]:
                    sccTable[i].add(tuple(sorted(list(state_table_DFA[i][j]))))  
        
    return sccTable


#Method to calculate the SCC for the entered automata
def sccGet(Table):
    theStack = []#A Stack
    lastPointStack = []#Stack that store the last point of the point in theStack
    popedPoint = []#Store the poped points of theStack
    allScc = []#The strongly connected components
    stateTable = copy.deepcopy(Table)
    DFN = {}
    LOW = {}
    states = list(stateTable.keys())
    index = 1
    
    theStack.append(states[0])
    DFN.update({states[0]:1})
    LOW.update({states[0]:1})
    currentPoint = theStack[0]
    
    while theStack:
        if stateTable[currentPoint]:
            theNextState = stateTable[currentPoint].pop()
            if theNextState not in popedPoint:
                if theNextState not in theStack:
                    theStack.append(theNextState)
                    lastPointStack.append(currentPoint)
                    index += 1
                    DFN.update({theNextState:index})
                    LOW.update({theNextState:index})
                    currentPoint = theStack[len(theStack)-1]
                elif theNextState!=currentPoint:
                    LOW[currentPoint]=min(LOW[currentPoint],DFN[theNextState])
                    
        else:
            if DFN[currentPoint] == LOW[currentPoint]:
                theScc = []
                scc = theStack.pop()
                if theStack:
                    lastPointStack.pop()
                while currentPoint!= scc:
                    theScc.append(scc)
                    popedPoint.append(scc)
                    lastPointStack.pop()
                    scc = theStack.pop()
                
                theScc.append(scc)
                popedPoint.append(scc)
                allScc.append(theScc)
                if theStack:
                    currentPoint = theStack[len(theStack)-1]
            else:
                nextPoint = currentPoint
                currentPoint = lastPointStack[theStack.index(currentPoint)-1]
                LOW[currentPoint]=min(LOW[currentPoint],LOW[nextPoint])
                
    return allScc

#Method to calculate the indistinguishable state pairs for D-detectability
def indistinguishableStatesPairs(thePoint):
    allPair = []
    index = 0
    stateList = sorted(list(thePoint))
    #Nest loop to generate state pair
    while index < len(stateList):
        fState = stateList[index]
        nextIndex = index
        while nextIndex < len(stateList):
            sState = stateList[nextIndex]
            statePair = (fState,sState)
            allPair.append(statePair)
            nextIndex += 1
        index += 1
    return allPair


#Method to Judge the detectability of the automata
def detectabilityJudge(sccTable, allScc, detectabilityType, Tspec, mold):
    Xm = []
    states = list(sccTable.keys())
    #Determine the aim states set
    if detectabilityType == "Ddetectable":
        for i in states:
            if len(set(indistinguishableStatesPairs(i)).intersection(set(Tspec))) == 0:
                Xm.append(i)
    elif detectabilityType == "detectable":
        for i in states:
            if len(i) == 1:
                Xm.append(i)
       
    selfCycle = []
    strongD = True
    weakD = False
    strongPD = True
    weakPD = False
    
    #The set that store the state which has self cycle
    for i in states:
        if i in sccTable[i]:
            selfCycle.append(i)
    
    #Judge the detectability
    for i in allScc:
        Pinxm = []#Point with element in Xm
        Pnotinxm = []#Point with elements not in Xm
        for j in i:
            if j in Xm:
                Pinxm.append(j)
            else:
                Pnotinxm.append(j)
        
        if len(i) == 1:
            if Pnotinxm == i and i in selfCycle:
                strongD = False
                strongPD =False
            elif Pinxm == i and i in selfCycle:
                weakD = True
                weakPD = True
        elif len(i) > 1:
            if Pinxm == i:
                weakD = True
                weakPD = True
                for k in Pinxm:
                    for l in sccTable[k]:
                        if l not in Xm:
                            strongD = False
            elif Pnotinxm == i:
                strongD = False
                strongPD = False
            else:
                strongD = False
                weakPD = True
                for m in Pnotinxm:
                    if m in selfCycle:
                        strongPD = False
                for n in Pinxm:
                    if n in selfCycle:
                        weakD = True
                if judgeTO(sccTable,Pinxm) == False:
                    weakD = True
                if judgeTO(sccTable,Pnotinxm) == False:
                    strongPD = False
                
            
                
            
     
    #Output the result
    if mold == "observer":
        if strongD:
            print("The system is strongly " + detectabilityType)
        elif weakD:
            print("The system is weakly " + detectabilityType)
        elif strongPD:
            print("The system is strong periodically " + detectabilityType)
        elif weakPD:
            print("The system is weakly periodically " + detectabilityType)
        else:
            print("The system is not " + detectabilityType)
    elif mold == "detector" and detectabilityType == "Ddetectable":
        if strongD:
            print("The system is strongly " + detectabilityType)
        else:
            print("The system is not strongly " + detectabilityType)
    elif mold == "detector" and detectabilityType == "detectable":
        if strongD:
            print("The system is strongly " + detectabilityType)
        elif strongPD:
            print("The system is strongly periodically " + detectabilityType)
        else:
            print("The system is not strongly or strongly periodically " + detectabilityType)
    
def judgeTO(table,states):
    inDegree = {}
    zPoints = []
    for i in states:
        inDegree.update({i:0})
        
    for i in states:
        for j in table[i]:
            if j in states and j != i:
                inDegree[j] += 1
            
    for i in states:
        if inDegree[i] == 0:
            zPoints.append(i)
            
    while zPoints:
        p = zPoints.pop()
        for i in table[p]:
            if i in states:
                inDegree[i] -= 1
        states.remove(p)
    
    if states:
        return False
    else:
        return True

choiceForMod = input("\nPlease select the type of model(enter 1 for \"observer\", enter 2 for \"detector\"): ")
choiceForDet = input("\nPlease select the type of detectability(enter 1 for \"detectability\", enter 2 for \"D-detectability\"): ")
print("\n")
stateTable = UnobservableReach(states, state_table)
if choiceForMod == "1":
    table = TableForScc(dfaGenerate(states,events,stateTable, startState, "observer"),events,"observer")
    scc=sccGet(table)
    if choiceForDet == "1":
        detectabilityJudge(table,scc,"detectable",Tspec, "observer")
    elif choiceForDet == "2":
        detectabilityJudge(table,scc,"Ddetectable",Tspec, "observer")
elif choiceForMod == "2":
    table = TableForScc(dfaGenerate(states,events,stateTable, startState, "detector"),events,"detector")
    scc=sccGet(table)
    if choiceForDet == "1":
        detectabilityJudge(table,scc,"detectable",Tspec, "detector")
    elif choiceForDet == "2":
        detectabilityJudge(table,scc,"Ddetectable",Tspec, "detector")
    
    
 