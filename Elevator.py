import sys
import itertools
import heapq as hq
from collections import deque
from enum import Enum, auto
from Variates import trunc_Exponential, trunc_Geometric, Equilikely

# Define Event data type
class EventType(Enum):
    GROUP_ARRIVAL = auto()
    ELEVATOR_RETURN = auto()
    ELEVATOR_STOP = auto()
class Event:
    def __init__(self, type):
        self.type = type
        self.at = 0
        self.groupSize = 0
        self.elev = []
        self.floor = 0
        self.nStops = 0

class Person:
    def __init__(self, dest, at):
        self.dest = dest
        self.at = at

class ElevatorNES:
    def __init__(self, nfloor, nelev, tfile, ndays):

        self.nfloors = nfloor
        self.nelevs = nelev
        self.ndays = ndays
        self.counter = itertools.count()
        
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
            
            # "Priming the pump"
            firstArrival = Event(EventType.GROUP_ARRIVAL)
            firstArrival.at = trunc_Exponential(10, 2, 90, self.trace)
            firstArrival.groupSize = trunc_Geometric(0.65, 1, 8, self.trace)
            self.totPeople -= firstArrival.groupSize
            hq.heappush(self.eventList, (firstArrival.at, next(self.counter), firstArrival))
            
            while (len(self.eventList) > 0) :
                _, _, event = hq.heappop(self.eventList)
                self.t = event.at
                
                if (len(self.peopleQueue) > maxQ): maxQ = len(self.peopleQueue)
                
                # PROCESS EVENT (GROUP_ARRIVAL)
                if event.type == EventType.GROUP_ARRIVAL:
                    for _ in range(event.groupSize):
                        ind = Equilikely(0, len(self.setF)-1, self.trace)
                        p = Person(self.setF[ind][0], self.t)
                        self.peopleQueue.append(p)
                        self.setF[ind][1] -= 1
                        if self.setF[ind][1] == 0:
                            self.setF.pop(ind)

                    if self.totPeople:
                        nextGroup = Event(EventType.GROUP_ARRIVAL)
                        nextGroup.at = self.t + trunc_Exponential(10, 2, 90, self.trace)
                        nextGroup.groupSize = trunc_Geometric(0.65, 1, min(self.totPeople,8), self.trace)
                        self.totPeople -= nextGroup.groupSize
                        hq.heappush(self.eventList, (nextGroup.at, next(self.counter), nextGroup))

                # PROCESS EVENT (ELEVATOR_STOP)
                elif event.type == EventType.ELEVATOR_STOP:
                    nExit = []
                    while (event.elev and event.elev[0].dest == event.floor) :
                        nExit.append(event.elev.pop(0))
                    
                    # Welford Accumulators for AVGDELAY and STDDELAY per passenger
                    optDelay = opt_delay(event.floor)
                    for j in range(len(nExit)):
                        self.iPass += 1
                        tot_delay = self.t - nExit[j].at + enterExit(len(nExit))
                        normDelay = (tot_delay - optDelay)/optDelay
                        d = normDelay - self.avgDelay
                        self.avgDelay = self.avgDelay + d/self.iPass
                        self.stdDelay = self.stdDelay + (d**2)*((self.iPass-1)/self.iPass)
                    
                    if not event.elev:
                        elevReturn = Event(EventType.ELEVATOR_RETURN)
                        elevReturn.at = self.t + enterExit(len(nExit)) + move_elevator(event.floor)
                        hq.heappush(self.eventList, (elevReturn.at, next(self.counter), elevReturn))
                    else:
                        nextStop = Event(EventType.ELEVATOR_STOP)
                        nextStop.floor = event.elev.pop(0).dest
                        nextStop.at = self.t + enterExit(len(nExit)) + move_elevator(nextStop.floor)
                        nextStop.elev = event.elev
                        hq.heappush(self.eventList, (nextStop.at, next(self.counter), nextStop))

                    nStops += 1
                
                # PROCESS EVENT (ELEVATOR_RETURN)
                elif event.type == EventType.ELEVATOR_RETURN:
                    self.freeElevs += 1
                    nStops += 1


                if self.freeElevs and self.peopleQueue:
                    elevs = round_robin(self.peopleQueue, self.freeElevs)
                    self.freeElevs = self.nelevs - len(elevs)
                    for e in elevs:
                        elevStop = Event(EventType.ELEVATOR_STOP)
                        elevStop.floor = e.pop(0).dest
                        elevStop.at = self.t + enterExit(len(e)) + move_elevator(elevStop.floor)
                        elevStop.elev = e
                        hq.heappush(self.eventList, (elevStop.at, next(self.counter), elevStop))

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
    elevs = [[] for _ in range(nfree)]
    max_alloc = nfree*10
    while (max_alloc > 0 and queue):
        elevs[j].append(queue.popleft())
        j = (j+1) % nfree
        max_alloc -= 1

    elevs = [sorted(e, key=lambda x: x.dest) for e in elevs if len(e)]

    return elevs

def opt_delay(floor):
    return 6 + move_elevator(floor)