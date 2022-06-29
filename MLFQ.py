#Konrad Dagiel


class Process:
    """
    Process class represents processes being executed by the scheduler.
    Processes can be added to the end of queues, popped from the start of queues.

    id: integer that identifies process for tracking

    timeLeft: integer symbolising how close process is to completing

    isIO: boolean true if process is I/O else false

    prio: initial priority queue the process is placed into

    """
    def __init__(self, id, timeLeft,isIO=False, prio=0):
        self._id=id
        self._timeLeft=timeLeft
        self._isIO=isIO
        self._priority=prio

    def __str__(self):
        return "Process prio="+ str(self._priority)+ ", time left="+ str(self._timeLeft)

def mlfq(timeslice, queues):
    """
    Main function of program, creates specified amount of queues,
    appends processes to appropriate queues, and puts IO operations into
    the blocked list

    Then runs exec function until all processes are finished executing

    timeslice: time slice of queue 1

    queues: number of multi-level feedback queues
    """
    global timeElapsed
    timeElapsed=0
    #create mlfq structure with specified amount of queues
    for _ in range(queues):
        queueList.append([])
        
    #append processes to their respective queues
    for i in processlist:
        if i._isIO==False:
            queueList[i._priority].append(i)
            print("Process",i._id,"added to queue", i._priority)
        #IO processes go in the blocked list.
        #For simplicity, IO will always take 320 units of time
        else:
            blockedList.append(i)
            print("IO Process",i._id,"added to blocked list")
    
    #exectute processes
    q=0 #start at queue 0
    while q<queues: #continue until at last queue
        if exec(queueList[q],timeslice,q, timeElapsed):
            #if no interrupts, execute processes in next queue
            q+=1
        else:
            #if interrupted, start iteration again at queue 0
            q=0
    #when all processes executed, idle process takes over
    print("IDLE process takes over cpu")
    return True

def exec(list, timeslice,q, timeElapsed):
    """
    exec function takes in a queue, with 0 or more processes in it.
    dequeues the first process, subtracts a quantum from its timeLeft
    (quantum determined by queue level)
    if process is finished, remove from queue system
    else push onto lower priority queue

    repeat until queue empty
    """
    remaining=0 #time left over from last process finishing

    #check if all higher queues are empty before executing
    #if not, return false, start processing again from queue 0
    for i in queueList[0:q]:
        if i != []:
            return False


    lowered=False #voltage is in its default state, not lowered

    #iterate this queue until empty
    while list != []:

        #if there are 2 or less processes in the last queue, and voltage in higher state
        #lower voltage, increase timeslice by 20%
        if q==len(queueList)-1 and len(list)<=2 and lowered==False:
            print('LOWERING VOLTAGE BY 20%')
            lowered=True
            timeslice=int(timeslice*1.2)


        p=list[0] #consider first process in queue
        
        #time to be subtracted is 2(^i)*q 
        #if a process finished in its time slice with extra time remaining,
        #give this extra time to this process
        t=((2**(p._priority))*timeslice)+remaining

        #increment time elapsed in this queue
        timeElapsed+=t

        #Process from blocked list enters the queue matching its priority level
        if timeElapsed==320 and blockedList!=[]:
            pio=blockedList.pop()
            queueList[pio._priority].append(pio)
            print("Process",pio._id,"added to queue",pio._priority)
            #interrupt this queue executing
            return False

        #subtract t from the time left in the current process
        p._timeLeft -= t

        #remove this process from this queue
        p=list.pop(0)

        #if process not finished within timeslice, lower its priority, and append it to the newxt lowest queue
        if p._timeLeft >0:
            print("process",p._id,"exec for",t,"secs, in queue",p._priority, "time left:",p._timeLeft)
            remaining=0
            #either go down a level if possible:
            if p._priority+1<=len(queueList)-1:
                p._priority+=1
            #or append to same list, (round-robin)
            queueList[p._priority].append(p)
        #else if finished within timeslice, pop it from the queue structure, and give the next process its remaining time
        else:
            remaining-=p._timeLeft
            print("process",p._id,"finished in queue",p._priority, "with", remaining,"secs remaining"  )

    #return to main loop and process the next queue
    return True

#init queueList and blockedList
queueList=[]
blockedList=[]

"""
Testing with 5 processes, 2 of which are IO.
Processes vary from low mid to high priorities,
low mid to very high execution times
"""
p0=Process(0,2000,True,3)
p1=Process(1,60)
p2=Process(2,10000, False, 7)
p3=Process(3,5000)
p4=Process(4,200,True)
processlist=[p0,p1,p2,p3,p4]

def test(timeslice, queues):
    mlfq(timeslice, queues)

#We test with a timeslice of 10, and 8 priority queues.
#but these vals can be changed
test(10, 8)