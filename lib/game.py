#!/usr/bin/env python3

## TODO
# Shield wall
# Edge fort (victory condition)
# UI

"""
 At this point, I have implemented Fetlar rules: no shieldwall capture, only exit for win
 Hnefatafl, Copenhagen rules
 1. The game is played by two players on a board of
    11×11 squares, one player taking control of the king
   and twelve defenders, the other taking control of
   twenty-four attackers. 
2. The pieces are set out as shown in figure 1. The attackers take the first move.
3. In his turn a player can move a single piece any
   number of spaces along a row or column; this piece
   may not jump over nor land on another of either colour.
4. The five marked squares in the centre and corners
   of the board are special, and only the king may land
   on them. Other pieces may pass over the central square.
5. A piece other than the king is captured when it
   is caught between two enemies along a row or column. A piece other than
   the king may also be captured by surrounding it between an enemy and one of
   the marked empty squares.
6. It is sometimes possible to capture two or three enemies separately (i.e. not
   two or three enemies in a row) against other pieces of
   your own in a single move; in this case all captured
   pieces are removed at once.
7. A row of pieces at the edge of the board may be captured by completely 
   surrounding them against the board edge, so that none of
   them have room to move. The capturing move must be a flanking move to the
   board edge, as shown in figure 2, and the opposite end could be bracketed by
   a piece or a marked corner square. This is the “shield wall” capture.
8. The king is captured by surrounding him on all four sides by attackers, or by
   surrounding him on three sides, if the fourth side is the marked central square.
9. The king wins the game if he reaches one of the corner squares. The king also
   wins if he constructs an “edge fort” (see figure 3), which is constructed so it
   cannot be captured by the attackers.
10. The attackers win if they capture the king. The attackers also win if they
    surround all of the king’s forces, so that none can reach the board edges.
11. Either player will lose the game if unable to move on his or her own turn.
12. Perpetual repetition is illegal. If the board position is repeated three times,
    the player in control of the situation must find another move.
Copyright Damian Walker 2015. All rights reserved.
http://tafl.cyningstan.com/
"""

import numpy as np
import random
import json

# FLAGS
repeatCheckOn = True # This tracks the rule disallowing a board state to be revisted 3 times. For running stateless, I turn it off

# For boolean functions, like "isValidMove", I only set a code if it returns false, using
# a global code. I should probably use the exception handler for this
lastReturnCode = 0
errorMessage = {}
RESTRICTED_SQUARE = 1
errorMessage[1] = "Only the king may enter the restricted squares"
TOO_MANY_REPEATS = 2
errorMessage[2] = "The board has already been in this state twice before, choose a different move"
NO_PIECE_TO_MOVE = 3
errorMessage[3] = "The board position you specified doesn't have a piece"
PIECE_DID_NOT_MOVE = 4
errorMessage[4] = "You did not give a new position for the specified piece"
WAY_BLOCKED = 5
errorMessage[5] = "The move you selected is blocked"
NO_DIAGONALS = 6
errorMessage[6] = "Pieces cannot move diagonally"

## things that end the game
gameOver = 0
gameOverMessage = {}
KING_CAPTURED = 1
gameOverMessage[1] = "King captured"
KING_ESCAPED = 2
gameOverMessage[2] = "King escaped"
NOT_ENOUGH_ATTACKERS_LEFT = 3
gameOverMessage[3] = "Not enough attackers left to capture the king"
NO_MOVES = 4
gameOverMessage[4] = "The payer has no legal move"
DEFENDERS_ENCLOSED = 5
gameOverMessage[5] = "The defenders are enclosed"

ROW = 0
COL = 1

ATTACKER = 1
DEFENDER = 2
KING = 3
DEAD_KING = 4

# the board is an 11x11 array, indexed first by row, then by column
# positions on the board are represented as follows:
#  0 = empty
#  1 = attacker
#  2 = defender
#  3 = king
# The starting state of the board is set up below
startingBoard = np.array([
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 1],
        [1, 1, 0, 2, 2, 3, 2, 2, 0, 1, 1],
        [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
        ])
restricted = [[0,0], [10,0], [5,5], [0,10], [10,10]] # only the king can go to these squares
winningSquares = [[0,0], [10,0], [0,10], [10,10]] # king wins if they get to this square

board = np.zeros([11,11], dtype=int) # use this to set up an empty board
#states = []
#stateCount ={}

# EXTERNAL FUNCTIONS
def starting_board():
    boardAsList = np.ndarray.tolist(startingBoard)
    return json.dumps(boardAsList)


def initializeGame():
    global board
    np.copyto(board, startingBoard)

    global states
    states = [] # to track prior states of the board and prevent a loop

    global stateCount
    stateCount = {} # This is a dictionary indexed by the byte version of a board state

    global attackersLeft
    attackersLeft = 24

    global attTurn
    # turn is represented as "attacker's turn": attTurn
    #  True = attackers
    #  False = defenders
    # swap turns with "not attTurn"
    attTurn = True # the game starts with the attackers

    global gameOver
    gameOver = 0


## Tests to see if a board position contains a piece of the current turn-holder
def isMyPiece(row, col):
    if attTurn:
        if board[row, col] == 1:
            return True
        else:
            return False
    else:
        if board[row, col] >= 2:
            return True
        else:
            return False
    

# Rather than store a list of remaining peices, I think it may be easier to search the board for peices
# Lists all the pieces of the current turn-holder
def findMyPieces():
    pieces = list()
    for row in range(0, 11):
        for col in range(0, 11):
            if isMyPiece(row, col):
                pieces.append([row, col])
    if (not(pieces)): # this shouldn't happen
        print(board)
        exit("Error: no peices left")

    return pieces


# no board state can be returned to a third time. We keep track of how many times 
# a board state has been seen
def boardRepeat(piece, toRow, toCol):
    fromRow, fromCol = piece
    pieceType = board[fromRow, fromCol]
    
    localBoard = np.zeros([11,11], dtype=int) # use this to set up an empty board
    np.copyto(localBoard, board)
    localBoard[fromRow, fromCol] = 0
    localBoard[toRow, toCol] = pieceType 
    boardKey = localBoard.tobytes()
    if ((boardKey not in stateCount) or stateCount[boardKey] <= 1):
        return False
    else:
        return True


## return if a board position is open (and in-bounds)
def isNotBlocked(row, col):
    return ((row >= 0) 
        and (row <= 10)
        and (col >= 0)
        and (col <= 10)
        and (board[row, col] == 0)
      )


## return if the specified piece could move into the specified position (ignoring if it is blocked by another piece
def isValidMove(piece, row, col):
    global lastReturnCode
    startRow, startCol = piece
    isKing = (board[startRow, startCol] == KING)
    if (not isKing and ([row, col] in restricted)):
        lastReturnCode = RESTRICTED_SQUARE
        return False
    elif (repeatCheckOn and boardRepeat(piece, row, col)):
        lastReturnCode = TOO_MANY_REPEATS
        return False
    else:
        return True


# explore the moves for the peice by incrementing and decrementing the row and column, until you hit an obstacle
# there are special squares only the king can enter
def findMoves(piece):
    moves = list()

    row, col = piece # grab the current position

    # go up
    row -= 1 # move the peice off its current position so it doesn't detect itself
    while (isNotBlocked(row, col)):
        if (isValidMove(piece, row, col)):
            moves.append([row, col])
        row -= 1

    # go down
    row, col = piece
    row += 1
    while (isNotBlocked(row, col)):
        if (isValidMove(piece, row, col)):
            moves.append([row, col])
        row += 1

    # go left
    row, col = piece
    col -= 1
    while (isNotBlocked(row, col)):
        if (isValidMove(piece, row, col)):
            moves.append([row, col])
        col -= 1

    # go right
    row, col = piece
    col += 1
    while (isNotBlocked(row, col)):
        if (isValidMove(piece, row, col)):
            moves.append([row, col])
        col += 1

    return moves


"""
for every attacker, there must be another attacker adjacent, including diagonals
and within that loop you must be able to find all defenders
find the inside, looking only at attackers. Then see if all the defenders are on one of those square
the inside is any place with space between two attackers. Walk out from that inside. If you hit a wall, 
mark all those squares as out of consideration.
or start walking from a corner. 
track min and max row and column for each blob. It it touches the edge, all squares in that blob
are out of consideration. All squares with attackers are out of consideration.
start horizontal, go edge to edge in one direction, keeping the same state as the last square
"""
## Checks if the current board is a victory for either player
def isVictory():
    global gameOver
    if (gameOver):
        return gameOver
    #check for edge fort
    # I decided to skip this for now

    #check for a complete surround of attackers
    ENCLOSED = 0
    NOT_ENCLOSED = 1
    exposed = np.zeros([11,11], dtype=int) # use this to set up an empty board we use to detect
    # loop to bleed the theoretical max of 10
    for n in range(10):
        for r in range(11):
            # bleed right
            enclosed = NOT_ENCLOSED # starting at the edge
            for c in range(11):
                if (board[r, c] == ATTACKER):
                    enclosed = ENCLOSED
                enclosed = exposed[r, c] or enclosed
                if ((board[r, c] >= DEFENDER)
                    and (enclosed == NOT_ENCLOSED)):
                    return False # if we do other checks after this, we need to double break
                exposed[r, c] = enclosed
            # bleed left
            enclosed = NOT_ENCLOSED # starting at the edge
            for c in range(10, -1, -1):
                if (board[r, c] == ATTACKER):
                    enclosed = ENCLOSED
                enclosed = exposed[r, c] or enclosed
                if ((board[r, c] >= DEFENDER)
                    and (enclosed == NOT_ENCLOSED)):
                    return False # if we do other checks after this, we need to double break
                exposed[r, c] = exposed[r, c] or enclosed
            
        for c in range(11):
            # bleed down
            enclosed = NOT_ENCLOSED # starting at the edge
            for r in range(11):
                if (board[r, c] == ATTACKER):
                    enclosed = ENCLOSED
                enclosed = exposed[r, c] or enclosed
                if ((board[r, c] >= DEFENDER)
                    and (enclosed == NOT_ENCLOSED)):
                    return False # if we do other checks after this, we need to double break
                exposed[r, c] = enclosed
    
        # bleed left
            enclosed = NOT_ENCLOSED # starting at the edge
            for r in range(10, -1, -1):
                if (board[r, c] == ATTACKER):
                    enclosed = ENCLOSED
                enclosed = exposed[r, c] or enclosed
                if ((board[r, c] >= DEFENDER)
                    and (enclosed == NOT_ENCLOSED)):
                    return False # if we do other checks after this, we need to double break
                exposed[r, c] = exposed[r, c] or enclosed
    gameOver = ATTACKERS_ENCLOSED
    return gameOver

## Keep a record of states of the board, to prevent loops
def storeState():
    if (not repeatCheckOn):
        return True

    global states
    global stateCount

    # store the new state of the board
    states.append(board)
    # keep track of how many times we've seen this board
    boardKey = board.tobytes()
    if (boardKey not in stateCount):
        stateCount[boardKey] = 1
    else:
        stateCount[boardKey] += 1


## Check if a position is within the bounds of the board
def inBounds(row, col):
    if ((row >= 0)
        and (row <= 10)
        and (col >= 0)
        and (col <= 10)):
        return True
    else:
        return False


## Check for (and execute) a capture, on an axis in a direction
def captureByDirection(axis, direction, row, col, execute = True):
    global gameOver
    # is there an opponent's piece adjacent (att = 1, def = 2, king = 3)
    if (axis == ROW):
        row += direction
    else:
        col += direction
    if (not inBounds(row, col)):
        return False
    capturePieceType = board[row, col]
    # check for a opposing peice
    if (attTurn and (capturePieceType >= DEFENDER)
        or (not attTurn and (capturePieceType == ATTACKER))):
        # check for the other side of the capture
        captureRow = row
        captureCol = col
        if (axis == ROW):
            row += direction
        else:
            col += direction
        if (not inBounds(row, col)):
            return False
        opposingPieceType = board[row, col]
        if (attTurn and (opposingPieceType == ATTACKER)
            or (not attTurn and (opposingPieceType >= DEFENDER)) # you can capture with the king
            or ([row, col] in restricted)): # you can capture against restricted squares
            # this is capture for a normal piece
            # but check for a king
            if (attTurn and (capturePieceType == KING)):
                # now we need to check on the axis (the if below is ugly, perhaps I should reconsider my data structure)
                if (((axis == ROW)
                     and ((captureCol <= 9) and (board[captureRow, captureCol + 1] == ATTACKER) 
                         or ([captureRow, captureCol + 1] in restricted))
                        and ((captureCol >= 1) and (board[captureRow, captureCol - 1] == ATTACKER) 
                         or ([captureRow, captureCol - 1] in restricted))
                        )
                    or ((axis == COL)
                        and ((captureRow <= 9) and (board[captureRow + 1, captureCol] == ATTACKER) 
                             or ([captureRow + 1, captureCol] in restricted))
                        and ((captureRow >= 1) and (board[captureRow - 1, captureCol] == ATTACKER) 
                         or ([captureRow - 1, captureCol] in restricted))
                        )
                    ):
                    if (execute):
                        gameOver = KING_CAPTURED
                        board[captureRow, captureCol] = DEAD_KING
                    return 4
            elif (execute):
                #print ('capture ', capturePieceType)
                board[captureRow, captureCol] = 0
                if (not attTurn):
                    global attackersLeft
                    attackersLeft -= 1
                    # you need at least three attackers to capture the king
                    if (attackersLeft == 2):
                        gameOver = NOT_ENOUGH_ATTACKERS_LEFT
            return 1

    return False # in all other cases, it didn't happen
            
        
# Check for captures. Return the capture value (1 for each normal piece, 4 for the king
# if execute is False, it will report on a possible capture, but won't execute on it
def capture(toRow, toCol, execute = True):
    capture = 0
    capture += captureByDirection(ROW, 1, toRow, toCol, execute) # down
    capture += captureByDirection(ROW, -1, toRow, toCol, execute) # up
    capture += captureByDirection(COL, 1, toRow, toCol, execute) # right
    capture += captureByDirection(COL, -1, toRow, toCol, execute) # left
    return capture


## Moves the peice from the specified start position to the specified end position. 
## if checkForValid is true, it checks if it is a legal move. When the computer is playing
## itself, we can skip the check, as it will only submit valid moves
def movePiece(start, end, checkForValid = True):
    global lastReturnCode
    startRow, startCol = start
    endRow, endCol = end
    pieceType = board[startRow, startCol]
#    print("moving", start, "(type " + str(pieceType) + ") to", end)

    if (checkForValid):
        # piece actually moves
        if (start == end):
            lastReturnCode = PIECE_DID_NOT_MOVE
            return False

        # is there a piece at the start
        if (board[startRow, startCol] == 0):
            lastReturnCode = NO_PIECE_TO_MOVE
            return False

        # no diagonals
        if ((startRow != endRow) and (startCol != endCol)):
            lastReturnCode = NO_DIAGONALS
            return False

        # make sure the final and intervening squares are clear
        # determine axis direction of move
        if (startRow == endRow):
            #moving column to column
            if (startCol > endCol):
                # moving left, so reverse columns
                checkCol = endCol
                checkEnd = startCol - 1 # the -1 accounts for the fact the piece starts there
            else:
                checkCol = startCol + 1 # the +1 accounts for the piece starting there
                checkEnd = endCol
                
            while (checkCol <= checkEnd):
                if (isNotBlocked(startRow, checkCol)):
                    checkCol += 1
                else:
                    lastReturnCode = WAY_BLOCKED
                    return False
        else:
            #moving row to row
            if (startRow > endRow):
                # moving up, so reverse rows
                checkRow = endRow
                checkEnd = startRow - 1 # the -1 accounts for the fact the piece starts there
            else:
                checkRow = startRow + 1 # the +1 accounts for the piece starting there
                checkEnd = endRow
            while (checkRow <= checkEnd):
                if (isNotBlocked(checkRow, startCol)):
                    checkRow += 1
                else:
                    lastReturnCode = WAY_BLOCKED
                    return False

        if (not isValidMove([startRow, startCol], endRow, endCol)):
            return False # last return code already set by isValidMove

    board[startRow, startCol] = 0
    board[endRow, endCol] = pieceType 
    
    # do captures
    if(capture(endRow, endCol, True)):
        True

    # check for king win
    if ((pieceType == KING)
        and [endRow, endCol] in winningSquares
        ):
        global gameOver
        gameOver = KING_ESCAPED

    storeState()
    return True


# Looks to see if a peice of the specified type is adjacent
def isAdjacent(row, col, pieceType):
    searchRow = row + 1
    searchCol = col
    if (inBounds(searchRow, searchCol)):
        if (board[searchRow, searchCol] == pieceType):
            return True

    searchRow = row - 1
    searchCol = col 
    if (inBounds(searchRow, searchCol)):
        if (board[searchRow, searchCol] == pieceType):
            return True

    searchRow = row
    searchCol = col + 1
    if (inBounds(searchRow, searchCol)):
        if (board[searchRow, searchCol] == pieceType):
            return True

    searchRow = row
    searchCol = col - 1
    if (inBounds(searchRow, searchCol)):
        if (board[searchRow, searchCol] == pieceType):
            return True


# Look at all peices and moves, and select one at random
def randomMove():
    myPieces = findMyPieces()

    random.shuffle(myPieces)
    for piece in myPieces:
        moves = findMoves(piece)
        if (not moves): # make sure this peice has moves
            continue
        move = random.choice(moves)
        break

    if (not movePiece(piece, move, True)):
        exit("Can't peform the move:" + errorMessage[lastReturnCode])

#    while (moves):
#        print(moves.pop())



def opponentAbove(position):
    return isOpponent(ROW, -1, position)

def opponentBelow(position):
    return isOpponent(ROW, 1, position)

def opponentRight(position):
    return isOpponent(COL, 1, position)

def opponentLeft(position):
    return isOpponent(COL, -1, position)

def isOpponent(axis, direction, position):
    row, col = position
    if (axis == ROW):
        row += direction
    else:
        col += direction
    if (not inBounds(row, col)):
        return False
    if ([row, col] in restricted):
        return True
    if ((attTurn)
        and (board[row, col] >= DEFENDER)):
        return True
    elif (board[row, col] == ATTACKER):
        return True
    return False


def smartMove():
    myPieces = findMyPieces()
    # generate a list of all possible moves
    myMoves = []
    for piece in myPieces:
        for move in findMoves(piece):
            myMoves.append([piece, move])
            
    # if a user has no valid moves, they lose
    if (len(myMoves) == 0):
        global gameOver
        gameOver = NO_MOVES
        return False

    #    print(len(myMoves)) number of moves
    random.shuffle(myMoves) # reorder moves to help with learning
    
    # give each move a score, and sort by score
    scores = {}
    # search for a captures
    for move in myMoves:
        start = move[0]
        startRow, startCol = start
        end = move[1]
        endRow, endCol = end
        score = capture(endRow, endCol, False) # points vary by capture

        # points for moving into a protected position
        True

        if (attTurn):
            # points for moving attackers next to the king
            if (isAdjacent(endRow, endCol, KING)):
                score += 1
                
            # points for clogging the corners
            score += (abs(endRow - 5) + abs(endCol -5))/10

        else:
            myPieceType = board[startRow, startCol]
            # points for moving the king to the corner
            if (([endRow, endCol] in winningSquares)
                and myPieceType == KING):
                score = 10
            # points for moving the king to the edge
            if ((myPieceType == KING)
                and ((endRow in [0, 10])
                     or (endCol in [0, 10]))):
                score += .5

            # move the king out of a capturable position (surrounded on three sides)
            if (myPieceType == KING):
                # this doesn't currently detect the state when you're protected by an ally on the other side
                surroundingCount = opponentAbove(start) + opponentBelow(start) + opponentLeft(start) + opponentRight(start)
                if (surroundingCount >= 3):
                    score += 3

        # index by the move, so we can add multiple elements to the score
        scores[str(move)] = [score, move]


#    for score in scores:
#        print(scores[score])
    indexOfBestScore = max(scores.keys(), key = (lambda k: scores[k][0]))
    piece, target = scores[indexOfBestScore][1]
 #   print("chosen", piece, target)
    if (not movePiece(piece, target, True)):
        exit("Can't peform the move:" + errorMessage[lastReturnCode])

    return True


# Test if the rules are correctly implemented
def runTests():
    global board
    initializeGame()

    # This board is an extreme example of  COMPLETE enclosure
    print("test enclosure detection positive")
    board = np.array([
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0]
        ])
    if(not isVictory()):
        exit('Failed Victory check 2')

    # This crazy board is an extreme example of an INCOMPLETE enclosure
    print("test enclosure detection negative")
    board = np.array([
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0]
        ])
    if(isVictory()):
        exit('Failed Victory check 1')

    ### FORCE A TEST OF REPEAT
    global repeatCheckOn
    repeatCheckOn = True

    board = np.array([
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 2, 0, 0, 0, 1, 0, 0, 1, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        ])
    #Precedence tests
    smartMove()

    #Capture test
    print("Capture up")
    movePiece([3,1],[2,1])
    if (board[1,1] != 0):
        exit("FAIL")
    print("Simultaneous capture left, right, and down")
    movePiece([5,5],[8,5])
    if ((board[8,4] != 0)
        or (board[8,6] != 0)
        or (board[9,5] != 0)):
        print(board)
        exit("FAIL")

    print("Capture against restricted square")
    movePiece([1,5],[3,5])
    if (board[4,5] != 0):
        exit("FAIL")

    print("Capture king")
    movePiece([3,9], [2,9])
    if (not gameOver):
        exit("FAIL")

    board = np.zeros([11,11], dtype=int) # use this to set up an empty board

    board[5,0] = 3 # set up a test board with only a king
    print("Move king to restricted square (this is allowed)")
    if (not movePiece([5,0], [5,5])):
        exit("FAIL") 
    np.copyto(board, startingBoard)

    storeState()
    print("Throw error when moving attacker to restricted square")
    if (movePiece([10,7], [10,10]) or lastReturnCode != RESTRICTED_SQUARE):
        exit("FAIL")
    print("Throw error when moving through a block")
    if (movePiece([10,7], [10,5]) or lastReturnCode != WAY_BLOCKED):
        exit("FAIL")
    print("Throw error when starting position is empty")
    if (movePiece([10,10], [10,5]) or lastReturnCode != NO_PIECE_TO_MOVE):
        exit("FAIL")
    print("Throw error when start and end positions are the same")
    if (movePiece([10,7], [10,7]) or lastReturnCode != PIECE_DID_NOT_MOVE):
        exit("FAIL")
    movePiece([10,7], [10,8])
    movePiece([10,8], [10,7])
    movePiece([10,7], [10,8])
    if (repeatCheckOn):
        print("Throw error when board state has repeated too many times")
        if (movePiece([10,8], [10,7]) or lastReturnCode != TOO_MANY_REPEATS):
            exit("FAIL")
    print("Throw error if piece moves diagonally")
    if (movePiece([10,8], [9,5]) or lastReturnCode != NO_DIAGONALS):
        exit("FAIL")
    print("Throw error if piece moves off the board")
    if (movePiece([10,8], [11, 8]) or lastReturnCode != WAY_BLOCKED):
        exit("FAIL")

    exit("All tests PASS")

        
##########
## MAIN ##
##########

#runTests()

totalMoves = 0
winTypes = {}
for n in range(0,100):
    initializeGame()

    i = 0 # safety stop
    while (not isVictory()):
        i += 1
        if (i >= 1000):
            break
        # randomMove()
        smartMove()
        totalMoves += 1
        attTurn = not attTurn # swicth to the other player's turn

    #print('Game over: ' + gameOverMessage[gameOver])
    # print(states)
    #count = len(states)
    if (gameOver == 0):
        print('woop', i)
        print(board)
        exit('sld')
    if (gameOver not in winTypes):
        winTypes[gameOver] = 1
    else:
        winTypes[gameOver] += 1

#    print('moves:', count)
#    print(states[count - 1])
#    print("----------------------------")

print('average moves per game: ', int(totalMoves/n))
for winType in winTypes:
    print(gameOverMessage[winType] + ': ' + str(winTypes[winType]))
