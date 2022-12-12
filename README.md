# Persistence_Diagram_Barycenter_Python

This repository contains a python code to compute a (possibly weighted) barycenter of an ensemble of persistence diagrams

## Persistence Diagram format
A Persistence Diagram should be represented as a list of list where each inner list corresponds to a persistence pair with 2 values, its birth and its death.

Example:
```
diag = [[0, 10], [4, 5], [6, 8]]
```

## Computing distance between Persistence Diagrams

This repository provides an implementation of the Auction algorithm to compute a distance between Persistence Diagrams, and hence an assignement between their pairs.

Example:
```
from auction import Auction

diag1 = [[0, 10], [4, 5], [6, 8]]
diag2 = [[2, 12], [3, 7], [5, 9]]

auctionSolver = Auction()
matching = auctionSolver.runFromData(diag1, diag2)
distance = auctionSolver.getDistanceFromMatching(matching)
```

## Computing barycenter of an ensemble of Persistence Diagrams

```
from barycenter import Barycenter

diag1 = [[1, 10], [4, 7], [3, 8], [5, 6]]
diag2 = [[0, 11], [3, 8], [4, 9], [2, 7]]
diag3 = [[2, 15], [2, 9], [1, 7], [1, 8]]
data = [diag1, diag2, diag3]

barycenterSolver = Barycenter()
barycenter = barycenterSolver.run(data)
```
