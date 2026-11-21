
# Deliverables
1. Simulation event types:
    In total, my simulation makes use of three event types (Elevator.py Lines 8-21):
        - GROUP_ARRIVAL > with parameters .type, .at, and .groupSize
            This is the event type that makes use of the truncated exponential and geometric variate functions I built. For each person in groupSize, I create a Person object with an initial arrival time to the ground floor and a destination floor that follows an Equilikely distribution based on a set F I've created to log the number of people left that still need to go to each floor. These people are then added to a people queue to wait for an elevator.
        - ELEVATOR_STOP > with parameters .type, .at, .elev, .floor
            This is the event type that occurs whenever an elevator arrives at a floor that's not the ground floor. While at the specific floor it calculates the normal delay times for each passenger that is exiting, and then creates a new ELEVATOR_STOP event for the next person in the elevator going to a different floor.
        - ELEVATOR_RETURN > with parameters .type and .at
            This is the event type that occurs when an elevator has dropped off all of its occupants at their given floors. It is scheduled as a case when an event is ELEVATOR_STOP, and simply tells the simulation that there is one more free elevator at the ground floor.

2. I created a separate Variate.py python file for all of my necessary variates. In that, a function called trunc_Geometric (Lines 27-42) handles the variate calculations, taking in the probability p, the truncation bounds, and the random trace file. It makes use of the geometric cdf (Lines 43-45) and the truncated geometric cdf (Lines 46-48). In the actual simulation (Elevator.py), a function call looks like this (Line 108):
trunc_Geometric(0.65, 1, min(self.totPeople,8), self.trace)
totPeople is a running total of all the people that still need to get to their floor, so when totPeople falls below 8, the truncation is limited from 1 to totPeople rather than 1 to 8.

3. I have two primary sections where I use Welford algorithms. The first, for STOPS and MAXQ is called in Elevator.py Lines 157-160. These require a counter i that incremented once each day (Line 69). MAXQ is checked at the beginning of each event in the main while loop (Line 93), and STOPS is incremented once for every ELEVATOR_STOP and ELEVATOR_RETURN event. The second was for the pedestrian average normal delay and standard deviation of normal delay (Elevator.py Lines 118-126). These required a second counter iPass which incremented once for every elevator passenger that exits. 

4. My elevator events are handled in my main while loop (Elevator.py Line 87). It starts with a dispatch if statement at the bottom of the loop (Lines 146-155) that checks if there are people in the queue and if there are free elevators. If so, the people are distributed round-robin style among the free elevators, and ELEVATOR_STOP events are scheduled for each one.
The ELEVATOR_STOP events are handled in Lines 112-139, and the ELEVATOR_RETURN events are handled in Lines 141-144.

5. My eventList data structure is a priority queue structure using the heapq python library. It is initially declared as an empty list in Elevator.py Line 48, but I use heapq functions "heappush" to enqueue events (Line 84 for example) and "heappop" to dequeue events (Line 89).



# Using git
git should be installed, or your terminal will prompt u to.
Run ```git clone https://github.com/karidge/ElevatorUp.git```
The folder will be created.

To push changes to the repository:
```git add .``` // Adds all files to the addition
```git commit -m "Message here"``` // Commit with message
```git push``` // Pushes to the repository

# Misc. commands for running script in docker instance
```docker run -it simgrading runuser -l blaster```
```git clone https://github.com/karidge/ElevatorUp.git && cd ElevatorUp && dos2unix SIM && chmod +x SIM```
```cd ElevatorUp```
```dos2unix SIM```
```chmod +x SIM```
```./SIM 1 1 <(/SIMGRADING/Random 6) 1```