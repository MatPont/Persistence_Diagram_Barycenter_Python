# Persistence_Diagram_Barycenter_Python

This repository provides python classes to compute distances and a (possibly weighted) barycenter of persistence diagrams

## Persistence Diagram format
A Persistence Diagram should be represented as a list of list where each inner list corresponds to a persistence pair with 2 values, its birth and its death.

**Example:**

```
diag = [[0, 10], [4, 5], [6, 8]]
```

## Computing distance between Persistence Diagrams

This repository provides an implementation of the Auction algorithm [Bertsekas, 1981] to compute a distance between two persistence diagrams, and hence an assignment between their pairs.

**Example:**

```
from auction import Auction

diag1 = [[0, 10], [4, 5], [6, 8]]
diag2 = [[2, 12], [3, 7]]

auctionSolver = Auction()
matching = auctionSolver.runFromData(diag1, diag2)
distance = auctionSolver.getDistanceFromMatching(matching)
```

## Computing barycenter of an ensemble of Persistence Diagrams

This repository provides an implementation of the barycenter (Fréchet means) algorithm [Turner et al., 2014] for an ensemble of persistence diagrams.

**Example**

```
from barycenter import Barycenter

diag1 = [[1, 10], [4, 7], [3, 8], [5, 6]]
diag2 = [[0, 11], [3, 8], [4, 9]]
diag3 = [[2, 15], [2, 9]]
data = [diag1, diag2, diag3]

barycenterSolver = Barycenter()
barycenter = barycenterSolver.run(data)
```

## References

[Bertsekas, 1981] D. P. Bertsekas. A new algorithm for the assignment problem. Mathematical Programming, 1981.

[Turner et al., 2014] K. Turner, Y. Mileyko, S. Mukherjee, and J. Harer. Fréchet Means for Distributions of Persistence Diagrams. DCG, 2014.
