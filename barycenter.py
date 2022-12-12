import random
from copy import deepcopy
from auction import Auction


class Barycenter:
    def __init__(self):
        self.sizeLimitPercent = 0.0
        self.sizeLimit = 0
        self.randomInit = False

    def runAuction(self, barycenter, mu):
        auctionSolver = Auction()
        matching = auctionSolver.runFromData(barycenter, mu)
        return matching

    def distanceFromMatching(self, matching):
        auctionSolver = Auction()
        return auctionSolver.getDistanceFromMatching(matching)

    def postprocessMatchings(self, barycenter, data, matchings):
        newMatchings = []
        for i in range(len(matchings)):
            matching = matchings[i]
            newMatching = []
            for match in matching:
                if not (match[0] >= len(barycenter) or match[1] >= len(data[i])):
                    newMatching.append(match)
            newMatchings.append(newMatching)
        return newMatchings

    def assignment(self, barycenter, data):
        matchings = []
        for i in range(len(data)):
            matching = self.runAuction(barycenter, data[i])
            matchings.append(matching)
        return matchings

    def update(self, barycenter, data, matchings, alphas):
        matchings = self.postprocessMatchings(barycenter, data, matchings)

        noData = len(data)
        baryNoNodes = len(barycenter)

        # m[i][j] contains the node in trees[j] matched to the node i in the barycenter
        matchingMatrix = []
        for i in range(baryNoNodes):
            matchingMatrix.append([])
            matchingMatrix[i] = [-1] * noData
        # m[i][j] contains the node in the barycenter matched to the node j in trees[i]
        revMatchingMatrix = []
        for i in range(noData):
            revMatchingMatrix.append([])
            revMatchingMatrix[i] = [-1] * len(data[i])
        # Compute matrices
        for i in range(noData):
            for j in range(len(matchings[i])):
                matchingMatrix[matchings[i][j][0]][i] = matchings[i][j][1]
                revMatchingMatrix[i][matchings[i][j][1]] = matchings[i][j][0]

        # Update barycenter
        newBary = []
        for i in range(baryNoNodes):
            newBirth = 0
            newDeath = 0
            noProjec = 0
            alphaSum = 0
            for j in range(noData):
                if matchingMatrix[i][j] != -1:
                    alphaSum += alphas[j]
            for j in range(noData):
                if matchingMatrix[i][j] != -1:
                    # newBirth += data[j][matchingMatrix[i][j]][0]
                    # newDeath += data[j][matchingMatrix[i][j]][1]
                    newBirth += data[j][matchingMatrix[i][j]][0] * alphas[j] / alphaSum
                    newDeath += data[j][matchingMatrix[i][j]][1] * alphas[j] / alphaSum
                else:
                    noProjec += 1
            if noData != noProjec:
                # newBirth /= (noData - noProjec)
                # newDeath /= (noData - noProjec)
                projec = (newBirth + newDeath) / 2
                # newBirth = ((noData - noProjec) * newBirth + noProjec * projec) / noData
                # newDeath = ((noData - noProjec) * newDeath + noProjec * projec) / noData
                newBirth = alphaSum * newBirth + (1 - alphaSum) * projec
                newDeath = alphaSum * newDeath + (1 - alphaSum) * projec
                newBary.append([newBirth, newDeath])

        # Add nodes unmatched in data
        for i in range(noData):
            for j in range(len(data[i])):
                if revMatchingMatrix[i][j] == -1:
                    projec = (data[i][j][0] + data[i][j][1]) / 2
                    # newBirth = (data[i][j][0] + (noData-1) * projec) / noData
                    # newDeath = (data[i][j][1] + (noData-1) * projec) / noData
                    newBirth = alphas[i] * data[i][j][0] + (1 - alphas[i]) * projec
                    newDeath = alphas[i] * data[i][j][1] + (1 - alphas[i]) * projec
                    newBary.append([newBirth, newDeath])

        newBary = self.limitSizeBarycenter_(newBary, data)

        return newBary

    def computeEnergy(self, matchings, alphas):
        energy = 0
        for i in range(len(matchings)):
            matching = matchings[i]
            cost_i = 0
            for match in matching:
                cost_i += match[2]
            cost_i *= alphas[i]
            energy += cost_i
        return energy
        # return sum( list( map(lambda x: sum( list( map(lambda y: y[2], x) ) ), matchings) ) )

    def display(self, barycenter, data):
        displayer = Display()
        displayer.display(data, barycenter)

    def print(self, *args):
        print("[BARYCENTER] ", end="")
        print(*args)

    def getBestInitIndex(self, data):
        distanceMatrix = []
        for i in range(len(data)):
            distanceMatrix.append([0] * len(data))
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                matching = self.runAuction(data[i], data[j])
                distanceMatrix[i][j] = self.distanceFromMatching(matching)
                distanceMatrix[j][i] = distanceMatrix[i][j]
        bestIndex = None
        bestDistance = None
        for i in range(len(distanceMatrix)):
            dist = sum(distanceMatrix[i])
            if bestDistance is None or dist < bestDistance:
                bestDistance = dist
                bestIndex = i
        return bestIndex

    def run(self, data, alphas=None):
        self.print("compute barycenter...")

        # Init barycenter
        if self.randomInit:
            initIndex = random.randint(0, len(data) - 1)
        else:
            initIndex = self.getBestInitIndex(data)
        barycenter = data[initIndex]
        barycenter = self.limitSizeBarycenter_(barycenter, data)
        self.print("initIndex =", initIndex)

        # Init alpha if None
        if alphas is None:
            alphas = []
            for i in range(len(data)):
                alphas.append(1.0 / len(data))

        # Run
        oldFrechetEnergy = -1
        converged = False
        while not converged:
            # Assignment
            matchings = self.assignment(barycenter, data)

            # Convergence
            frechetEnergy = self.computeEnergy(matchings, alphas)
            self.print("Frechet energy =", frechetEnergy)
            tol = oldFrechetEnergy / 100
            if oldFrechetEnergy != -1 and abs(frechetEnergy - oldFrechetEnergy) <= tol:
                converged = True
                break
            oldFrechetEnergy = frechetEnergy

            # Update
            barycenter = self.update(barycenter, data, matchings, alphas)

        self.print("converged!")
        # self.display(barycenter, data)

        return barycenter

    # sizeLimitPercent is a percentage between 0 and 100
    def limitSizeBarycenter(self, barycenter, data, sizeLimitPercent, sizeLimit):
        if sizeLimitPercent == 0.0:
            sizeLimitPercent = 100.0

        newBary = deepcopy(barycenter)

        # Add persistence (used to sort pairs)
        for i in range(len(barycenter)):
            newBary[i].append(max(barycenter[i]) - min(barycenter[i]))

        # Sort by persistence and remove pairs
        newBary.sort(key=lambda e: e[2], reverse=True)
        noNodes = sum([len(data[i]) for i in range(len(data))])
        newSize = int(max(noNodes * sizeLimitPercent / 100.0, 1))
        if sizeLimit != 0:
            newSize = int(min(newSize, sizeLimit))
        newBary = newBary[:newSize]

        # Remove persistence
        for i in range(len(newBary)):
            newBary[i] = newBary[i][:2]

        return newBary

    def limitSizeBarycenter_(self, barycenter, data):
        return self.limitSizeBarycenter(
            barycenter, data, self.sizeLimitPercent, self.sizeLimit
        )


if __name__ == "__main__":
    x_1 = [[10.0, 26.0], [16.0, 25.0]]
    x_2 = [[10.0, 30.0], [16.0, 30.0], [23.0, 27.0]]
    x_3 = [[10.0, 27.0], [18.0, 27.0], [22.0, 26.0]]
    data = [x_1, x_2, x_3]
    bary = Barycenter()
    barycenter = bary.run(data)
    print(barycenter)
