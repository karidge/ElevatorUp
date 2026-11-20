The autograder should be installed outside of this repository.
```curl -O https://cs.mcprogramming.com/static/sim/hr/96170718dcca5241/elevatorup-student.tar.bz2```

From the assignment page
```mkdir tmp && cd tmp && tar xjf ../elevatorup-student.tar.bz2```


# Deliverables
1. Display $\pi_k$ and $\hat{p}_a(\pi_k)$ columns

Where $\pi_k$ is some path from node 1 to node N
$\hat{p}_a(\pi_k)$ is the probability that the path $\pi_k$ is the critical (longest) path



# Using git
git should be installed, or your terminal will prompt u to.
Run ```git clone https://github.com/karidge/ElevatorUp.git```
The folder will be created.

To push changes to the repository:
```git add .``` // Adds all files to the addition
```git commit -m "Message here"``` // Commit with message
```git push``` // Pushes to the repository

# Running script on docker instance
```docker run -it simgrading runuser -l blaster```
In the instance:
```git clone https://github.com/karidge/ElevatorUp.git && cd ElevatorUp && dos2unix SIM && chmod +x SIM```
```cd ElevatorUp```
```dos2unix SIM```
```chmod +x SIM```
```./SIM 1 1 <(/SIMGRADING/Random 6) 1```