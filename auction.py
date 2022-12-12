class Auction:
    def __init__(self):
        self.epsilon = -1
        self.epsilonDiviserMultiplier = 0
        self.delta_lim = 0.01
        self.bidderAssignments = [-1]
        self.goodAssignments = []
        self.goodPrices = []
        self.costMatrix = [[]]
        self.rowSize = 0
        self.colSize = 0
        self.balancedAssignment = False

    def setBalanced(self, balanced):
        self.balancedAssignment = balanced
        if self.balancedAssignment:
            self.goodPrices = [0] * self.colSize
        else:
            self.goodPrices = [0] * ((self.colSize - 1) + (self.rowSize - 1))

    def setInput(self, cMatrix):
        self.rowSize = len(cMatrix)
        self.colSize = len(cMatrix[0])
        self.costMatrix = cMatrix

    def initEpsilon(self):
        if self.epsilon == -1:
            maxValue = -999999999
            for i in range(len(self.costMatrix)):
                maxValue = max(maxValue, max(self.costMatrix[i]))
            self.epsilon = maxValue / 4
            if self.epsilon == 0:
                self.epsilon = 1
            """epsilon
        /= ((epsilonDiviserMultiplier == 0) ? 1 : epsilonDiviserMultiplier * 5);"""

    def epsilonScaling(self):
        self.epsilon /= 5

    def initBiddersAndGoods(self):
        self.bidderAssignments = []
        self.goodAssignments = []
        if self.balancedAssignment:
            self.bidderAssignments = [-1] * self.rowSize
            self.goodAssignments = [-1] * self.colSize
        else:
            self.bidderAssignments = [-1] * ((self.rowSize - 1) + (self.colSize - 1))
            self.goodAssignments = [-1] * ((self.colSize - 1) + (self.rowSize - 1))

    def initFirstRound(self):
        self.bidderAssignments[0] = -1

    def makeBalancedMatrix(self, matrix):
        nRows = len(matrix)
        nCols = len(matrix[0])
        matrix[nRows - 1][nCols - 1] = 0

        # Add rows
        for i in range(nCols - 2):
            newLine = matrix[nRows - 1]
            matrix.append(newLine)
        # Add columns
        for i in range((nRows - 1) + (nCols - 1)):
            for j in range(nRows - 2):
                matrix[i].append(matrix[i][nCols - 1])

        return matrix

    # ----------------------------------------
    # Main Functions
    # ----------------------------------------
    def runAuctionRound(self, cMatrix):
        unassignedBidders = []
        for i in range(len(self.bidderAssignments)):
            unassignedBidders.append(i)

        while len(unassignedBidders) != 0:
            bidderId = unassignedBidders[0]
            unassignedBidders.pop(0)

            # Get good with highest value
            bestValue = -9999999999
            bestSecondValue = -9999999999
            bestGoodId = -1
            for goodId in range(len(self.goodPrices)):
                """if (
                    not self.balancedAssignment
                    and bidderId >= self.rowSize - 1
                    and goodId >= self.colSize - 1
                ):
                    continue"""
                if cMatrix[bidderId][goodId] == -1:
                    continue
                goodPrice = self.goodPrices[goodId]
                value = -cMatrix[bidderId][goodId] - goodPrice
                if value > bestValue:
                    bestSecondValue = bestValue
                    bestValue = value
                    bestGoodId = goodId
                elif value > bestSecondValue:
                    bestSecondValue = value

            # Update assignments
            self.bidderAssignments[bidderId] = bestGoodId
            if self.goodAssignments[bestGoodId] != -1:
                unassignedBidders.append(self.goodAssignments[bestGoodId])
            self.goodAssignments[bestGoodId] = bidderId

            # Update price
            delta = abs(bestValue - bestSecondValue) + self.epsilon
            self.goodPrices[bestGoodId] = self.goodPrices[bestGoodId] + delta

    def run(self):
        matchings = []

        self.initEpsilon()

        # Try to avoid price war
        """tempPrice = max(self.goodPrices)
        savedPrices = []
        for i in range(len(self.goodPrices)):
            old = self.goodPrices[i]
            self.goodPrices[i] = self.goodPrices[i] * self.epsilon / (1 if tempPrice == 0 else tempPrice)
            t = old - self.goodPrices[i]
            savedPrices.append(t)"""

        # Make balanced cost matrix
        if not self.balancedAssignment:
            self.costMatrix = self.makeBalancedMatrix(self.costMatrix)

        # Run auction
        self.initFirstRound()
        while not self.stoppingCriterion(self.costMatrix):
            self.initBiddersAndGoods()
            self.runAuctionRound(self.costMatrix)
            self.epsilonScaling()
            """iter++;
      if(numberOfRounds != -1 and iter >= numberOfRounds)
        break;"""

        # Create output matching
        for bidderId in range(len(self.bidderAssignments)):
            """int i = std::min(bidderId, this->rowSize-1);
            int j = std::min(bidderAssignments[bidderId], this->colSize-1);"""
            i = bidderId
            j = self.bidderAssignments[bidderId]
            if self.balancedAssignment or (
                not self.balancedAssignment
                and not (i >= self.rowSize - 1 and j >= self.colSize - 1)
            ):
                matchings.append([i, j, self.costMatrix[i][j]])

        # Set prices as before
        """for i in range(len(self.goodPrices)):
            self.goodPrices[i] += savedPrices[i]"""

        return matchings

    # ----------------------------------------
    # From data
    # ----------------------------------------
    def distance(self, p1, p2):
        return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

    def distanceDiag(self, p):
        diag = (p[0] + p[1]) / 2
        return self.distance(p, [diag, diag])

    def makeCostMatrix(self, mu_1, mu_2):
        costMatrix = []
        for i in range(len(mu_1)):
            costMatrix.append([])
            for j in range(len(mu_2)):
                costMatrix[i].append(self.distance(mu_1[i], mu_2[j]))
            costMatrix[i].append(self.distanceDiag(mu_1[i]))

        costMatrix.append([])
        for j in range(len(mu_2)):
            costMatrix[len(mu_1)].append(self.distanceDiag(mu_2[j]))
        costMatrix[len(mu_1)].append(0)

        return costMatrix

    def runFromData(self, mu_1, mu_2):
        costMatrix = self.makeCostMatrix(mu_1, mu_2)
        self.setInput(costMatrix)
        self.setBalanced(False)
        matching = self.run()
        return matching

    def getDistanceFromMatching(self, matching):
        return sum(list(map(lambda x: x[2], matching)))

    # ----------------------------------------
    # Stopping Criterion Functions
    # ----------------------------------------
    def stoppingCriterion(self, cMatrix):
        if self.bidderAssignments[0] == -1:  # Auction not started
            return False
        delta = 5
        delta = self.getRelativePrecision(cMatrix)
        return not (delta > self.delta_lim)

    def getRelativePrecision(self, cMatrix):
        d = self.getMatchingDistance(cMatrix)
        # if d < 1e-12:
        if d < 1e-6:
            return 0
        denominator = d - len(self.bidderAssignments) * self.epsilon
        if denominator <= 0:
            return 1
        else:
            return d / denominator - 1

    def getMatchingDistance(self, cMatrix):
        d = 0
        for bidderId in range(len(self.bidderAssignments)):
            i = bidderId
            j = self.bidderAssignments[bidderId]
            d += cMatrix[i][j]
        return d

    # ----------------------------------------
    # Utils
    # ----------------------------------------
    def printMatrix(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                print(matrix[i][j], " ", end="")
            print()
