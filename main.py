# citire CFG
fin = open("date.in", 'r')

G = [] # limbajul citit

# nrV = int(fin.readline())
aux = fin.readline()
V = [item for item in aux.split()]
aux = fin.readline()
T = [item for item in aux.split()]
nrP = int(fin.readline())
P = {}
for i in range(nrP):
    rule = fin.readline().strip()
    leftside = rule.split('=')[0]
    if leftside not in P:
        P.update({leftside: []})
    right_side = rule.split('=')[1].split('|')
    for item in right_side:
        P[leftside].append(item)
S = fin.readline().strip()

# Reguli Chomsky
# S = lamda
# neterminal = neterminal neterminal
# neterminal = terminal

# Step 1
# remove S, if S has any terminals S0=S
newS = 'S0'
needsnewrule = 0
for rule in P[S]:
    for t in T:
        if rule.find(t) != -1:
            needsnewrule = 1
            break
    if needsnewrule == 1: break

if needsnewrule == 1:
    P.update({newS: [S]})

# Step 2
# CFG simplification

marked = []

def removeInnacesibile(cS):
    global V, P, marked
    rulesofcs = P[cS]

    if cS not in marked:
        marked.append(cS)
    for rule in rulesofcs:
        for nont in V:
            if rule.find(nont) != -1 and nont not in marked:
                removeInnacesibile(nont)

removeInnacesibile(S)
V = [item for item in marked]
nrP = len(P)
i = 0
while i < nrP:
    item = list(P.keys())[i]
    if item not in V:
        P.pop(item)
        nrP -= 1
    i += 1

marked = []


def removeInutile():
    global V, P, T, marked

    for cS in P:
        rulesofcs = P[cS]
        mark1 = True
        markLamda = False
        for rule in rulesofcs:
            if rule == "lamda":
                markLamda = True
                break
            mark2 = 0
            mark3 = 0
            for nont in V:
                if rule.find(nont) != -1 and nont != cS:
                    mark1 = False
                if rule.find(nont) == -1:
                    mark2 += 1
            if mark2 == len(V) and mark1 is True:
                for nonv in T:
                    if rule.find(nonv) != -1:
                        mark3 += 1
                if mark3 == len(rule):
                    mark1 = False
        if mark1 is True and markLamda is not True:
            marked.append(cS)


removeInutile()
for item in marked:
    V.remove(item)
    P.pop(item)
for stare in P:
    for rule in P[stare]:
        for item in marked:
            if rule.find(item) != -1 and rule in P[stare]:
                P[stare].remove(rule)
# print(P)


def removeLamda():
    global P, T, haslamda

    def getnewrules(item, m):
        global P, V, T, new, haslamda

        add = False
        addedrules = []
        whotoremove = []
        breakflag = False
        for rule in P[item]:
            for idx in range(len(rule)):
                if rule[idx] in m:
                    if rule not in whotoremove and item in new and rule not in new[item]:
                        for idx1 in range(len(rule)):
                            if rule[idx1] in T:
                                breakflag = True
                        whotoremove.append(rule)
                    newrule = rule[0:idx] + rule[idx + 1::]
                    if len(newrule) == 0:
                        newrule = "lamda"
                        haslamda = True
                    add = True
                    if newrule not in addedrules:
                        addedrules.append(newrule)
                        if item not in new:
                            new.update({item: [newrule]})
                        else: new[item].append(newrule)
                    if breakflag:
                        add = False
                        break
        return add, addedrules, whotoremove

    m = []
    for item in P:
        for rule in P[item]:
            # print("---", item, rule)
            if rule.find('lamda') != -1:
                m.append(item)
                P[item].remove(rule)
                break
    if len(m) == 0: return
    notbreakflag = True
    global new
    new = {}
    while notbreakflag:
        for item in P:
            notbreakflag, nR, w = getnewrules(item, m)
            if notbreakflag is True:
                for k in w:
                    if k in P[item]:
                        P[item].remove(k)
                for k in range(len(nR)):
                    if nR[k] not in P[item]:
                        P[item].append(nR[k])
        if notbreakflag is False:
            break


haslamda = True
while haslamda is True:
    haslamda = False
    removeLamda()
# print("remove lamda", P)


def removeUnitProd():
    global P, V
    k = 0
    nr = len(P)
    while k < nr:
        cS = list(P.keys())[k]
        nrR = len(P[cS])
        i = 0
        while i < nrR:
            rule = P[cS][i]
            if len(rule) == 1 and rule[0] in V:
                who = rule[0]
                P[cS].remove(rule)
                nrR -= 1
                for rulenew in P[who]:
                    if rulenew not in P[cS]:
                        P[cS].append(rulenew)
                        nrR += 1
            else: i += 1
        k += 1

removeUnitProd()

# print("minimized", P)
# Step 3: adapting to chomsky rules

# i) prod rules like S=aA
newStates = [chr(i) for i in range(ord('A'),ord('Z')+1) if chr(i) not in V ]
added = []

nrP = len(P)
i = 0
while i < nrP:
    cS = list(P.keys())[i]
    nrR = len(P[cS])
    for j in range(nrR):
        hasV = False
        hasT = 0
        whoT = []
        for nonT in V:
            if P[cS][j].find(nonT) != -1:
                hasV = True
                break
        for nonV in T:
            if P[cS][j].find(nonV) != -1:
                whoT.append(nonV)
                hasT += 1
        if hasV and hasT != 0:
            while hasT > 0:
                addnew = newStates[0]
                for st in added:
                    if whoT[hasT - 1] in P[st]:
                        addnew = st
                        break
                else:
                    newStates.pop(0)
                    added.append(addnew)
                    P.update({addnew: [whoT[hasT - 1]]})
                    nrP += 1
                poz = P[cS][j].find(whoT[hasT - 1])
                newrule = ""
                for k in range(len(P[cS][j])):
                    if k != poz:
                        newrule = newrule + P[cS][j][k]
                    else:
                        newrule = newrule + addnew
                P[cS][j] = newrule
                hasT -= 1
    i += 1

# ii) S -> ASB => S -> CB C -> AS
nrP = len(P)
i = 0
while i < nrP:
    cS = list(P.keys())[i]
    nrR = len(P[cS])
    for j in range(nrR):
        hasV = False
        hasT = 0
        whoT = []
        for nonT in V:
            if P[cS][j].find(nonT) != -1:
                hasV = True
                break
        for idx in range(len(P[cS][j])):
            if P[cS][j][idx] in T:
                whoT.append(P[cS][j][idx])
                hasT += 1
        if hasV is False and hasT != 1:
            while hasT > 0:
                addnew = newStates[0]
                for st in added:
                    if whoT[hasT - 1] in P[st]:
                        addnew = st
                        break
                else:
                    newStates.pop(0)
                    P.update({addnew: [whoT[hasT - 1]]})
                    nrP += 1
                poz = P[cS][j].find(whoT[hasT - 1])
                newrule = ""
                for k in range(len(P[cS][j])):
                    if k != poz:
                        newrule = newrule + P[cS][j][k]
                    else:
                        newrule = newrule + addnew
                P[cS][j] = newrule
                hasT -= 1
    i += 1

nrP = len(P)
i = 0
while i < nrP:
    cS = list(P.keys())[i]
    nrR = len(P[cS])
    for j in range(nrR):
        nrV = 0
        for idx in range((len(P[cS][j]))):
            if P[cS][j][idx] in P:
                nrV += 1
        if nrV > 2:
            k = 0
            newrule = ""
            while k + 1 < len(P[cS][j]):
                addnew = newStates[0]
                newStates.pop(0)
                P.update({addnew: [P[cS][j][k] + P[cS][j][k + 1]]})
                newrule = newrule + addnew
                k += 2
            while k < len(P[cS][j]):
                newrule = newrule + P[cS][j][k]
                k += 1
            P[cS][j] = newrule
    i += 1

fout = open("date.out", "w")
fout.write(S + '\n')
for state in P:
    fout.write(str(state) + '=>')
    count = 0
    for rule in P[state]:
        fout.write(rule)
        if count < len(P[state]) - 1:
            fout.write("|")
        count += 1
    fout.write("\n")
