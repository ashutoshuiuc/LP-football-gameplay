import numpy as np
import pulp as p
import math
import copy

#--------------------------------------------Functions------------------------------
def dist(pt1,pt2):
    return ((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)**0.5

def traj(init_i, s_i, init_j, s_j, score):
    if s_i==init_i:
        #line is x = s_i
        a = 1
        b = 0
        c = -s_i
    else:  
        m = (s_j - init_j)/(s_i - init_i)
        b = 1
        a = -m
        c = m*s_i - s_j
    if dist((s_i,s_j),(init_i,init_j))>6:
        return -INF

    #ax + by + c is our line
    traj_score = 0#score[s_i][s_j]
    p=1
    q=1
    step_i = step_j = 1
    if init_i > s_i:
        step_i = -1
        p=-1
    if init_j > s_j:
        step_j = -1
        q=-1
    arr=[]
    #print(init_i,init_j)
    #print(s_i,s_j)
    for i in range(init_i, s_i+p, step_i):
        for j in range(init_j, s_j+q, step_j):
            #if i == init_i and j == init_j:
            #    continue
            
            d = abs(a*i + b*j + c)/(a**2 + b**2)**0.5
            #print(d)
            if d < 1/math.sqrt(2) + 0.001:
                arr.append(score[i][j]) #traj_score = min(traj_score, score[i][j])
    return sum(arr)/len(arr) #traj_score

def safety_distance(te, op, l, b,k,const,goalpost):
    safety = np.zeros((l,b))
    distance = np.ones((l,b))
    for i in range(l):
        for j in range(b):
            distance[i][j]=3*k/(1+k*dist(goalpost,(i,j)))
            safety[i][j]=const + sum(-k/(1+k*dist((i,j),(op[m][0],op[m][1]))) for m in range(len(op)))#sum(k/(1+k*dist((i,j),(te[m][0],te[m][1]))) for m in range(len(te)))
            if i==0 or j==0 or i==l-1 or j==b-1:
                safety[i][j] +=-0.5
            if i==1 or j==1 or i==l-2 or j==b-2:
                safety[i][j]+=-0.25
    return safety, distance

def inv_safety_op(te, op, l, b,k,const):
    safety = np.zeros((l,b))
    #distance = np.ones((l,b))
    for i in range(l):
        for j in range(b):
            #distance[i][j]=k/(1+k*dist((l-1,int(b/2)),(i,j)))
            safety[i][j]=const+sum(k/(1+k*dist((i,j),(te[m][0],te[m][1]))) for m in range(len(te)))# + sum(-k/(1+k*dist((i,j),(op[m][0],op[m][1]))) for m in range(len(op)))

    return safety



def dribble(te, op, score,goalpost,l,b):
    possible_dribble = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i != 0 or j != 0:
                possible_dribble.append((i, j))

    team = []
    for buddy in te:
        li = []
        for i in possible_dribble:
            add_i, add_j = i
            if buddy[0]+add_i>=0 and buddy[0]+add_j>=0 and buddy[0]+add_i<=l-1 and buddy[1]+add_j<=b-1 and [buddy[0]+add_i,buddy[1]+add_j] not in te + op:
                li.append([buddy[0] + add_i, buddy[1] + add_j])
            """
            try:
                test = score[buddy[0] + add_i][buddy[1] + add_j] #to see if it exists
                if [buddy[0]+add_i,buddy[1]+add_j] not in te + op:
                    l.append([buddy[0] + add_i, buddy[1] + add_j])
            except:
                pass
            """
        team.append(li)
    print(team)
    #team has possible locations for each player
    final_params = []
    for i in range(len(te)):
        x = copy.deepcopy(te)
        x.remove(te[i]) #Should not pass to current player

        params = []
        for probable in team[i]:
            result = 0
            count = 1 # for goalpost count
            for j in x:
                result += traj(probable[0], j[0],probable[1], j[1], score)
                count += 1
            result += traj(probable[0],  goalpost[0],probable[1], goalpost[1], score)
            params.append(result/count)
        
        final_params.append(params)

    return (team, final_params)

def dribble_op(te, op, score,l,b,k=2):
    possible_dribble = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i != 0 or j != 0:
                possible_dribble.append((i, j))

    team = []
    for buddy in op:
        li = []
        for i in possible_dribble:
            add_i, add_j = i
            if buddy[0]+add_i>=0 and buddy[0]+add_j>=0 and buddy[0]+add_i<=l and buddy[1]+add_j<=b and [buddy[0]+add_i,buddy[1]+add_j] not in te + op:
                li.append([buddy[0] + add_i, buddy[1] + add_j])
            """
            try:
                test = score[buddy[0] + add_i][buddy[1] + add_j] #to see if it exists
                if [buddy[0]+add_i,buddy[1]+add_j] not in te + op:
                    l.append([buddy[0] + add_i, buddy[1] + add_j])
            except:
                pass
            """
        team.append(li)

    #team has possible locations for each player
    final_params = []
    for i in range(len(op)):
        #x = copy.deepcopy(te)
        #x.remove(te[i]) #Should not pass to current player

        params = []
        for probable in team[i]:
            
            result = k/(1+k*dist(probable,te[0]))
            #count = 1 # for goalpost count
            #for j in x:
            #    result += traj(probable[0], probable[1], j[0], j[1], score)
            #    count += 1
            #result += traj(probable[0], probable[1], goalpost[0], goalpost[1], score)
            
            params.append(result)
        
        final_params.append(params)

    return (team, final_params)
    

def opt(n_te, n_op, te, op, l, b, goalpost,k,const,consec_pass):
    
    safety, distance = safety_distance(te, op, l, b,k,const,goalpost)
    score=safety*distance
    #print(score.shape)
    
    #t calculation, hardcoded for all 3 possibilites
    #We have 2 players to shoot to, and one goalpost to kick towards
    t = []
    if consec_pass<=1:
        for g in range(1, n_te):
            init_i = te[0][0] #us
            init_j = te[0][1]
            
            s_i = te[g][0] #teammate
            s_j = te[g][1]

            t.append(traj(init_i, s_i, init_j, s_j, score))
    else:
        for g in range(1, n_te):
            #init_i = te[0][0] #us
            #init_j = te[0][1]
            
            #s_i = te[g][0] #teammate
            #s_j = te[g][1]

            t.append(-INF)


    #Goal calc
    init_i = te[0][0] #us
    init_j = te[0][1]

    s_i, s_j = goalpost
    thresh=2
    t.append(traj(init_i, s_i, init_j, s_j, score)/thresh)

    #Dribble calculation
    team, final_params = dribble(te, op, score,goalpost,l,b)
    lengths = [len(i) for i in team]

    for player in range(len(team)):
        for d_pos in range(len(team[player])):
            t.append(final_params[player][d_pos])
    
    prob = p.LpProblem('football',p.LpMaximize)
    binary_vars=[p.LpVariable(str(i), lowBound=0, upBound=1, cat="Binary") for i in range(n_te+sum(lengths))] #pass = n_te-1, shoot = 1, dribble = whatever,p = n_te(condition)(removed)
    
    #code first n_te-1 as passes, next for shoot, and remaining for dribble, last n_te are p(condition variable)(removed)
    prob+=sum(binary_vars[i]*t[i] for i in range(n_te)) + sum(binary_vars[i+n_te]*t[i+n_te] for i in range(sum(lengths)))/n_te
    prob+=(sum(binary_vars[j] for j in range(n_te+lengths[0]))==1)
    counter=lengths[0]
    for i in range(1,n_te):
        prob+=(binary_vars[i-1]+sum(binary_vars[j] for j in range(n_te+counter,n_te+counter+lengths[i]))==1) #(sum(binary_vars[i] for i in range(n_te)) + binary_vars[-1] == 1)
        counter+=lengths[i]
    """
    counter = 0
    j=0
    for i in lengths:
        prob+= sum(binary_vars[counter + n_te + k] for k in range(i)) == binary_vars[-1]
        #prob+= sum(binary_vars[counter + n_te + i]) <= 1
        counter += i
        j+=1
    """
    status = prob.solve(p.PULP_CBC_CMD(msg=0))

    #print("Goalpost = "+str(goalpost))
    result = [i.value() for i in binary_vars]
    

    return [result,lengths,team]

def opp_gets_pass(n_te, n_op, te, op, l, b, goalpost,k,const,te_idx1,te_idx2,to_goal):
    if to_goal==1:
        s_i=goalpost[0]
        s_j=goalpost[1]
        init_i=te[te_idx1][0]
        init_j=te[te_idx1][1]

        if s_i==init_i:
            #line is x = s_i
            a = 1
            b = 0
            c = -s_i
        else:  
            m = (s_j - init_j)/(s_i - init_i)
            b = 1
            a = -m
            c = m*s_i - s_j
        #if dist((s_i,s_j),(init_i,init_j))>6:
        #    return -INF

        #ax + by + c is our line
        #traj_score = 0#score[s_i][s_j]

        my_var=-1
        for idx in range(len(op)):
            d=abs(a*op[idx][0] + b*op[idx][1] + c)/(a**2 + b**2)**0.5
            if d<1/(2):
                my_var=idx
        return my_var
    else:
        s_i=te[te_idx2][0]
        s_j=te[te_idx2][1]
        init_i=te[te_idx1][0]
        init_j=te[te_idx1][1]

        if s_i==init_i:
            #line is x = s_i
            a = 1
            b = 0
            c = -s_i
        else:  
            m = (s_j - init_j)/(s_i - init_i)
            b = 1
            a = -m
            c = m*s_i - s_j
        #if dist((s_i,s_j),(init_i,init_j))>6:
        #    return -INF

        #ax + by + c is our line
        #traj_score = 0#score[s_i][s_j]

        my_var=-1
        for idx in range(len(op)):
            d=abs(a*op[idx][0] + b*op[idx][1] + c)/(a**2 + b**2)**0.5
            if d<1/(2):
                my_var=idx
        return my_var






#--------------------------------------------Constants-----------------------------
l=15 #length of the field
b=15 #length of the bredth
n_op=3 #number of opponents
n_te=3 #number of team members
op=[]
te=[] #te[0] is initial player.
const = 10 #constant for initial score function
k=4 #constant for distance function
goalpost = [l-1, int(b/2)]
goalpost_te=[0,int(b/2)]
INF=10000

#--------------------------------------------Main Loop---------------------------------

#safety at any point (i,j)=const+sum(k*(-1)^t/(1+kr)) where t = 0 for our team member and t = 1 for opponent team member
#score = safety_function*distance_function

#x=int(l/2)
#y=int(b/2)
#te.append([x,y])
#print("team member {num} position: ({pos1},{pos2})".format(num=0, pos1=x, pos2=y))
for i in range(n_te):
    while(True):
        x=np.random.randint(1,int(l/2))
        y=np.random.randint(1,b)
        if [x,y] not in te:
            break
    te.append([x,y])
    print("team member {num} position: ({pos1},{pos2})".format(num=i, pos1=x, pos2=y))


for i in range(n_op):
    while(True):
        x=np.random.randint(int(l/2),l)
        y=np.random.randint(1,b)
        if [x,y] not in te+op:
            break
    
    op.append([x,y])
    print("opponent {num} position: ({pos1},{pos2})".format(num=i, pos1=x, pos2=y))