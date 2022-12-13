import matplotlib.pyplot as plt
import numpy as np
import T308 as proj

height=proj.b
width=proj.l
ball_with=1 # 1 stands for left team, 0 for right team
prev_ball_pos=proj.te[0]
consec_pass=0
last_idx_passed=-1

while(True):
    if ball_with==1:

        for i in range(height+2):
            plt.plot(np.linspace(0,width+1),i*np.ones(50))
        for j in range(width+2):
            plt.plot(j*np.ones(50),np.linspace(0,height+1))

        #plotting players now
        x_tp=np.array([])
        y_tp=np.array([])
        x_op=np.array([])
        y_op=np.array([])
        num_tp=proj.n_te
        num_op=proj.n_op
        plt.plot(0.5,int((height+1)/2)+0.5,'x')
        plt.plot(width+0.5,int((height+1)/2)+0.5,'x')
        for i in range(num_tp):
            x_tp=np.append(x_tp,proj.te[i][0]+0.5)#,np.random.randint(width-1)+0.5)
            y_tp=np.append(y_tp,proj.te[i][1]+0.5)#,np.random.randint(height-1)+0.5)
        for i in range(num_op):
            x_op=np.append(x_op,proj.op[i][0]+0.5)#,np.random.randint(width-1)+0.5)
            y_op=np.append(y_op,proj.op[i][1]+0.5)#,np.random.randint(height-1)+0.5)
        #print(x_tp,y_tp)
        #print(x_op,y_op)
        plt.scatter(x_tp[1:],y_tp[1:],color='g')
        plt.scatter(x_tp[0],y_tp[0],color='b')
        plt.scatter(x_op,y_op,color='r')
        prev_ball_pos=proj.te[0]

        [result,lengths,team] = proj.opt(proj.n_te, proj.n_op,
                        proj.te, proj.op, proj.l, proj.b, proj.goalpost,proj.k,proj.const,consec_pass)
        print(result)
        ball_gone=0
        if result[num_tp-1]==1:
            i = proj.opp_gets_pass(proj.n_te, proj.n_op,proj.te, proj.op, proj.l, proj.b, proj.goalpost,proj.k,proj.const,0,-1,1)
            if i!=-1 and np.random.choice(a=[0,1],p=[0.7,0.3])==1:
                ball_with=0
                print('ball goes from te to op during shoot to goalpost')
                consec_pass=0
                ball_gone=1
                last_idx_passed=-1
                temp=[proj.op[i][0],proj.op[i][1]]
                [proj.op[i][0],proj.op[i][1]]=[proj.op[0][0],proj.op[0][1]]
                [proj.op[0][0],proj.op[0][1]]=temp
            else:
                print("Game Over")
                break
        
        for i in range(len(result)):
            if result[i]==1:
                if i<=num_tp-2:
                    idx_o=proj.opp_gets_pass(proj.n_te, proj.n_op,proj.te, proj.op, proj.l, proj.b, proj.goalpost,proj.k,proj.const,0,i+1,0)
                    if idx_o!=-1 and np.random.choice(a=[0,1],p=[0.7,0.3])==1:
                        ball_gone=1
                        ball_with=0
                        print('ball goes from te to op during pass')
                        consec_pass=0
                        last_idx_passed=-1
                        temp=[proj.op[idx_o][0],proj.op[idx_o][1]]
                        [proj.op[idx_o][0],proj.op[idx_o][1]]=[proj.op[0][0],proj.op[0][1]]
                        [proj.op[0][0],proj.op[0][1]]=temp
                        plt.plot(np.linspace(x_tp[0],x_tp[i+1]),np.linspace(y_tp[0],y_tp[i+1]),color='g')
                    else:
                        print("Pass from ",[x_tp[0],y_tp[0]],"to ",[x_tp[i+1],y_tp[i+1]])
                        #prev_ball_pos=proj.te[0]
                        plt.plot(np.linspace(x_tp[0],x_tp[i+1]),np.linspace(y_tp[0],y_tp[i+1]),color='g')
                        temp=[proj.te[i+1][0],proj.te[i+1][1]]
                        [proj.te[i+1][0],proj.te[i+1][1]]=[proj.te[0][0],proj.te[0][1]]
                        [proj.te[0][0],proj.te[0][1]]=temp
                        if last_idx_passed == i+1:
                            consec_pass+=1
                        else:
                            consec_pass=1
                            last_idx_passed=i+1

                    
                else:
                    k=num_tp-1
                    for j in range(len(lengths)):
                        if k+lengths[j]<i:
                            k=k+lengths[j]
                        else:
                            #if j==0:
                            #    prev_ball_pos=proj.te[j]
                            temp=[proj.te[j][0],proj.te[j][1]]
                            [proj.te[j][0],proj.te[j][1]]=[team[j][i-k-1][0],team[j][i-k-1][1]]
                            plt.plot(np.linspace(temp[0]+0.5,proj.te[j][0]+0.5),np.linspace(temp[1]+0.5,proj.te[j][1]+0.5),color='g')
                            break
        if i == len(result)-1:
            print("Dribble")


        ## opponent move
        #only the safety is taken as the total score instead of safety*distance
        score,_=proj.safety_distance(proj.te,proj.op,proj.l,proj.b,proj.k,proj.const,proj.goalpost) 
        team,final_params=proj.dribble_op(proj.te,proj.op,score,proj.l,proj.b,proj.k)
        to_reach=[]
        for i in range(len(proj.op)):
            while len(final_params[i])!=0:
                idx=final_params[i].index(max(final_params[i]))
                [x,y]=team[i][idx]
                if [x,y] not in to_reach+proj.op+proj.te[1:]:
                    plt.plot(np.linspace(proj.op[i][0]+0.5,x+0.5),np.linspace(proj.op[i][1]+0.5,y+0.5),color='r')
                    [proj.op[i][0],proj.op[i][1]]=[x,y]
                    to_reach.append([x,y])
                    if ball_gone==0:
                        if [x,y]==proj.te[0]or[x,y]==prev_ball_pos or (proj.dist([x,y],proj.te[0])<=2**0.5 and np.random.choice(a=[0,1],p=[0.7,0.3])==1):
                            ball_with=0
                            print('ball goes from te to op during opponent move')
                            consec_pass=0
                            last_idx_passed=-1
                            if [x,y]!=proj.te[0]:
                                temp=[proj.op[i][0],proj.op[i][1]]
                                [proj.op[i][0],proj.op[i][1]]=[proj.op[0][0],proj.op[0][1]]
                                [proj.op[0][0],proj.op[0][1]]=temp
                    break
                else:
                    final_params[i].pop(idx)
                    team[i].pop(idx)
        plt.show()

        plt.close()
    else:
        for i in range(height+2):
            plt.plot(np.linspace(0,width+1),i*np.ones(50))
        for j in range(width+2):
            plt.plot(j*np.ones(50),np.linspace(0,height+1))

        #plotting players now
        x_tp=np.array([])
        y_tp=np.array([])
        x_op=np.array([])
        y_op=np.array([])
        num_tp=proj.n_te
        num_op=proj.n_op
        plt.plot(0.5,int((height+1)/2)+0.5,'x')
        plt.plot(width+0.5,int((height+1)/2)+0.5,'x')
        for i in range(num_tp):
            x_tp=np.append(x_tp,proj.te[i][0]+0.5)#,np.random.randint(width-1)+0.5)
            y_tp=np.append(y_tp,proj.te[i][1]+0.5)#,np.random.randint(height-1)+0.5)
        for i in range(num_op):
            x_op=np.append(x_op,proj.op[i][0]+0.5)#,np.random.randint(width-1)+0.5)
            y_op=np.append(y_op,proj.op[i][1]+0.5)#,np.random.randint(height-1)+0.5)
        #print(x_tp,y_tp)
        #print(x_op,y_op)
        plt.scatter(x_op[1:],y_op[1:],color='r')
        plt.scatter(x_op[0],y_op[0],color='y')
        plt.scatter(x_tp,y_tp,color='g')
        prev_ball_pos=proj.op[0]

        [result,lengths,team] = proj.opt(proj.n_op, proj.n_te,
                        proj.op, proj.te, proj.l, proj.b, proj.goalpost_te,proj.k,proj.const,consec_pass)
        print(result)
        if result[num_op-1]==1:
            i = proj.opp_gets_pass(proj.n_op, proj.n_te,proj.op, proj.te, proj.l, proj.b, proj.goalpost_te,proj.k,proj.const,0,-1,1)
            if i!=-1 and np.random.choice(a=[0,1],p=[0.7,0.3])==1:
                ball_with=1
                print('ball goes from op to te during shoot to goalpost')
                consec_pass=0
                ball_gone=1
                last_idx_passed=-1
                temp=[proj.te[i][0],proj.te[i][1]]
                [proj.te[i][0],proj.te[i][1]]=[proj.te[0][0],proj.te[0][1]]
                [proj.te[0][0],proj.te[0][1]]=temp
            else:
                print("Game Over")
                break
        for i in range(len(result)):
            if result[i]==1:
                if i<=num_op-2:
                    idx_t=proj.opp_gets_pass(proj.n_op, proj.n_te,proj.op, proj.te, proj.l, proj.b, proj.goalpost_te,proj.k,proj.const,0,i+1,0)
                    if idx_t!=-1 and np.random.choice(a=[0,1],p=[0.7,0.3])==1:
                        ball_gone=1
                        ball_with=1
                        print('ball goes from op to te during pass')
                        consec_pass=0
                        last_idx_passed=-1
                        temp=[proj.te[idx_t][0],proj.te[idx_t][1]]
                        [proj.te[idx_t][0],proj.te[idx_t][1]]=[proj.te[0][0],proj.te[0][1]]
                        [proj.te[0][0],proj.te[0][1]]=temp
                        plt.plot(np.linspace(x_op[0],x_op[i+1]),np.linspace(y_op[0],y_op[i+1]),color='r')
                    else:
                        print("Pass from ",[x_op[0],y_op[0]],"to ",[x_op[i+1],y_op[i+1]])
                        #prev_ball_pos=proj.op[0]
                        plt.plot(np.linspace(x_op[0],x_op[i+1]),np.linspace(y_op[0],y_op[i+1]),color='r')
                        temp=[proj.op[i+1][0],proj.op[i+1][1]]
                        [proj.op[i+1][0],proj.op[i+1][1]]=[proj.op[0][0],proj.op[0][1]]
                        [proj.op[0][0],proj.op[0][1]]=temp
                        if last_idx_passed == i+1:
                            consec_pass+=1
                        else:
                            consec_pass=1
                            last_idx_passed=i+1
                else:
                    k=num_op-1
                    for j in range(len(lengths)):
                        if k+lengths[j]<i:
                            k=k+lengths[j]
                        else:
                            #if j==0:
                             #   prev_ball_pos=proj.op[0]
                            temp=[proj.op[j][0],proj.op[j][1]]
                            [proj.op[j][0],proj.op[j][1]]=team[j][i-k-1][0],team[j][i-k-1][1]
                            plt.plot(np.linspace(temp[0]+0.5,proj.op[j][0]+0.5),np.linspace(temp[1]+0.5,proj.op[j][1]+0.5),color='r')
                            break
        if i == len(result)-1:
            print("Dribble")

        ## opponent move
        score,_=proj.safety_distance(proj.op,proj.te,proj.l,proj.b,proj.k,proj.const,proj.goalpost_te)
        team,final_params=proj.dribble_op(proj.op,proj.te,score,proj.l,proj.b,proj.k)
        to_reach=[]
        for i in range(len(proj.te)):
            while True:
                idx=final_params[i].index(max(final_params[i]))
                [x,y]=team[i][idx]
                if [x,y] not in to_reach+proj.te+proj.op[1:]:
                    plt.plot(np.linspace(proj.te[i][0]+0.5,x+0.5),np.linspace(proj.te[i][1]+0.5,y+0.5),color='g')
                    [proj.te[i][0],proj.te[i][1]]=[x,y]
                    to_reach.append([x,y])
                    if ball_gone==0:
                        if [x,y]==proj.op[0]or[x,y]==prev_ball_pos or (proj.dist([x,y],proj.op[0])<=2**0.5 and np.random.choice(a=[0,1],p=[0.7,0.3])==1):
                            ball_with=1
                            print('ball goes from op to te during opponent move')
                            consec_pass=0
                            last_idx_passed=-1
                            if [x,y]!=proj.op[0]:
                                temp=[proj.te[i][0],proj.te[i][1]]
                                [proj.te[i][0],proj.te[i][1]]=[proj.te[0][0],proj.te[0][1]]
                                [proj.te[0][0],proj.te[0][1]]=temp
                    break
                else:
                    final_params[i].pop(idx)
                    team[i].pop(idx)
        plt.show()

        plt.close()
