import sys
import heapq as hq
from collections import deque
from enum import Enum, auto
from Variates import trunc_Exponential, trunc_Geometric, Equilikely

# Define Event data type
class EventType(Enum):
    GROUP_ARRIVAL = auto()
    ELEVATOR_RETURN = auto()
class Event:
    def __init__(self, type):
        self.type = type
        self.at = 0
        self.groupSize = 0

class ElevatorNES:
    def __init__(self, nfloor, nelev, tfile, ndays):

        self.nfloors = nfloor
        self.nelevs = nelev
        self.ndays = ndays
        
        try:
            self.trace = open(tfile, 'r')
        except FileNotFoundError:
            # print(f"Error: The trace file at {tfile} was not found.")
            sys.exit(1)
        
        self.eventList = []
        self.t = 0
        
        self.freeElevs = self.nelevs
        
        
        # SSQ specific state
        self.peopleQueue = deque()

        # For Reporting
        self.i = 0
        self.stops = 0
        self.maxQ = 0
        self.iPass = 0
        self.avgDelay = 0
        self.stdDelay = 0
        
        
    def NES_Main(self):
        for _ in range(self.ndays):
            
            self.i += 1

            self.totPeople = 100*self.nfloors
            self.setF = [[i+1, 100] for i in range(self.nfloors)]
            
            # Daily Reporting
            nStops = 0
            maxQ = 0
            iPass = 0
            avgDelay = 0
            stdDelay = 0
            
            # "Priming the pump"
            firstArrival = Event(EventType.GROUP_ARRIVAL)
            firstArrival.at = trunc_Exponential(10, 2, 90, self.trace)
            firstArrival.groupSize = trunc_Geometric(0.65, 1, 8, self.trace)
            self.totPeople -= firstArrival.groupSize
            hq.heappush(self.eventList, (firstArrival.at, firstArrival))
            
            while (len(self.eventList) > 0) :
                _, event = hq.heappop(self.eventList)
                self.t = event.at
                
                # PROCESS EVENT (GROUP_ARRIVAL)
                if event.type == EventType.GROUP_ARRIVAL:
                    for _ in range(event.groupSize):
                        ind = Equilikely(0, len(self.setF)-1, self.trace)
                        p = self.setF[ind][0]
                        self.peopleQueue.append(p)
                        self.setF[ind][1] -= 1
                        if self.setF[ind][1] == 0:
                            self.setF.pop(ind)

                    nextGroup = Event(EventType.GROUP_ARRIVAL)
                    nextGroup.at = self.t + trunc_Exponential(10, 2, 90, self.trace)
                    nextGroup.groupSize = trunc_Geometric(0.65, 1, 8, self.trace)
                    self.totPeople -= nextGroup.groupSize
                    hq.heappush(self.eventList, (nextGroup.at, nextGroup))

                # PROCESS EVENT (ELEVATOR_RETURN)
                elif event.type == EventType.ELEVATOR_RETURN:
                    self.freeElevs += 1
                    nStops += 1


                if self.freeElevs and self.peopleQueue:
                    elevs, nfree = round_robin(self.peopleQueue, self.freeElevs)
                    self.freeElevs = nfree
                    for e in elevs:
                        e.sort()
                        tot_delay = enterExit(len(e))
                        i = 0
                        nSameDest = 1
                        curr_floor = 0
                        while (i < len(e)-1):
                            while (i < len(e)-1 and e[i] == e[i+1]):
                                nSameDest += 1
                                i += 1
                            tot_delay += move_elevator(e[i]-curr_floor)
                            nStops += 1
                            tot_delay += enterExit(nSameDest)
                            
                            # Welford Accumulators for AVGDELAY and STDDELAY per passenger
                            optDelay = opt_delay(e[i])
                            normDelay = (tot_delay - optDelay)/optDelay
                            for _ in range(nSameDest):
                                self.iPass += 1
                                d = normDelay - self.avgDelay
                                self.avgDelay = self.avgDelay + d/self.iPass
                                self.stdDelay = self.stdDelay + (d**2)*((self.iPass-1)/self.iPass)
                            
                            curr_floor = e[i+1]
                            nSameDest = 1

                        elevReturn = Event(EventType.ELEVATOR_RETURN)
                        elevReturn.at = self.t + tot_delay
                        hq.heappush(self.eventList, (elevReturn.at, elevReturn))
                    
                if (len(self.peopleQueue) > maxQ): maxQ = len(self.peopleQueue)
                    
            # Welford Accumulators for STOPS and MAXQ
            avgStops = nStops/self.nelevs
            self.stops = self.stops + (1/self.i)*(avgStops - self.stops)
            self.maxQ = self.maxQ + (1/self.i)*(maxQ - self.maxQ)
    
        return self.stops, self.maxQ, self.avgDelay, (self.stdDelay/self.iPass)**0.5
    
    
def move_elevator(h):
    if h == 0: return 0
    elif h == 1: return 8
    else: return (2*8 + 5*(h-2))

def enterExit(n):
    times = [3, 5, 7, 9, 11, 13, 15, 17, 19, 22]
    return times[n-1]

def round_robin(queue, nfree):
    j = 0
    elevs = [[None] for _ in range(nfree)]
    max_alloc = nfree*10
    while (max_alloc > 0 and queue):
        elevs[j].append(queue.popleft())
        j = (j+1) % nfree
        max_alloc -= 1

    nfree = 0
    for i in range(len(elevs)):
        if elevs[i] == [None]:
            elevs.pop(i)
            nfree += 1
    return elevs, nfree

def opt_delay(floor):
    return 6 + move_elevator(floor)