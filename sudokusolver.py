from time import time
import sys
import copy
import logging

class SodukuSolver:
    def __init__(self,dim,fileDir):
        self.dim = dim
        self.expandedNodes = 0
        with open(fileDir) as f:
	        content = f.readlines()
	        self.board = [list(x.strip()) for x in content]
        self.rv = self.getRemainingValues()

    def __str__(self):
        string = '\n'
        for row in self.board:
            for x in row:
                string += x+" "
            string+='\n'
        return string

    def isSafe(self,row,col,choice):
        choiceStr = str(choice)
        for i in range(self.dim):
            if self.board[row][i] == choiceStr or self.board[i][col] ==choiceStr:
                return False

        boxR = row - (row % 3)
        boxV = col - (col % 3)
        for i in range(3):
            for j in range(3):
                if self.board[boxR + i][boxV + j] == choiceStr:
                    return False
        return True

    def getNextLocation(self):
        for i in range(self.dim):
            for j in range(self.dim):
                if self.board[i][j] == '0':
                    return (i,j)
        return (-1,-1)

    def getDomainLength(self,lst):
        # 'x' represents fixed value(already filled)
        if 'x' in lst or lst == []:
            return 10               # to prevent the agent from choosing an empty domain as MRV cell
        else:
            return len(lst)

    # returning the next smallest domain
    # filling the cells with smaller domain size further reduces the search space in next steps
    def getNextMRVRowCol(self):
        # stores lengths of all lists(domains) from RV
        rvMap = list(map(self.getDomainLength,self.rv))
        minimum = min(rvMap)
        if minimum == 10:
            return (-1,-1)
        index = rvMap.index(minimum)
        # as domains are stored linearly
        return(index // 9, index % 9)

    # a function to find a truncated domain which reduces our search space
    def getDomain(self,row,col):
        # creating a list of numbers (1-9)
        RVCell = [str(i) for i in range(1 ,self.dim + 1)]

        # removing elements from the RVCell which are found in the row
        for i in range(self.dim):
            if self.board[row][i] != '0':
                if self.board[row][i] in RVCell:
                    RVCell.remove(self.board[row][i])

        # removing elements from the RVCell which are found in the column
        for i in range(self.dim):
            if self.board[i][col] != '0':
                if self.board[i][col] in RVCell:
                    RVCell.remove(self.board[i][col])

        # removing elements from the RVCell which are found in the sector
        boxRow = row - row%3
        boxCol = col - col%3
        for i in range(3):
            for j in range(3):
                if self.board[boxRow+i][boxCol+j]!=0:
                    if self.board[boxRow+i][boxCol+j] in RVCell:
                        RVCell.remove(self.board[boxRow+i][boxCol+j])
        return RVCell

    # finding possible values for each cell 
    # already filled cells are represented as ['x']
    def getRemainingValues(self):
        RV=[]
        for row in range(self.dim):
            for col in range(self.dim):
                if self.board[row][col] != '0':
                    RV.append(['x'])
                else:
                    RV.append(self.getDomain(row,col))
        return RV


    '''Solving methods'''
    def solveBacktracking(self):
        location = self.getNextLocation()
        if location[0] == -1:
            return True
        else:
            self.expandedNodes += 1
            for choice in range(1,self.dim+1):
                if self.isSafe(location[0],location[1],choice):
                    self.board[location[0]][location[1]] = str(choice)
                    if self.solveBacktracking():
                        return True
                    self.board[location[0]][location[1]] = '0'
            return False

    # forward checking
    def isEmptyDomainProduced(self,row,col,choice):
        element = self.rv.pop(row*9 + col)

        if [] in self.rv:
            self.rv.insert(row*9 + col,element)
            return True
        else:
            self.rv.insert(row*9 + col,element)
            return False
                
    def solveCSP(self):
        location = self.getNextMRVRowCol()
        if location[0] == -1:
            return True
        else:
            self.expandedNodes+=1

            row = location[0]
            col = location[1]

            for choice in self.rv[row*9 + col]:
                choice_str = str(choice)
                self.board[row][col] =  choice_str
                cpy = copy.deepcopy(self.rv)
                self.rv = self.getRemainingValues()
                
                if not self.isEmptyDomainProduced(row,col,choice_str):
                    if self.solveCSP():
                        return True

                self.board[row][col] = '0'
                self.rv = cpy

            return False



def main():

    # taking filename of puzzle and algorithm to be used as command line input
    # to run : python3 solver.py [filename] [algo]
    file = sys.argv[1]
    algo = sys.argv[2]

    # create and configure the logger
    logging.basicConfig(filename = "sudoku.log", format = '[%(asctime)s]: %(message)s', level = logging.INFO)

    try:
        s = SodukuSolver(9,'problems/{}.txt'.format(file))
        start = time()

        time_elapsed = 0.0

        if(algo == "CSP"):
            print(s)
            s.solveCSP()
            print(s)
            end = time()
            time_elapsed = round((end - start), 3)
            logging.info(f"{file}.txt    {algo}    {s.expandedNodes}  --  {time_elapsed}")
        elif(algo == "backtracking"):
            print(s)
            s.solveBacktracking()
            print(s)
            end = time()
            time_elapsed = round((end - start), 3)
            logging.info(f"{file}.txt    {algo}    {s.expandedNodes}  --  {time_elapsed}")
        else:
            print("\nAlgorithm not implemented")
            logging.info(f"\"wrong algorithm specified\"")

        print(f"Time Elapsed: {time_elapsed}")
        print(f"Nodes Expanded: {s.expandedNodes}")

    except FileNotFoundError:
        logging.info(f"\"{file}.txt not found\"")
        print(f"{file}.txt not found")
        


if __name__ == "__main__":
    main()
