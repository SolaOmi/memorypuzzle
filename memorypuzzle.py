#!/usr/bin/env python3

import random, pygame, sys
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program
RUNTIME = 100 # Time limit to solve the puzzle
WINDOWWIDTH = 640 # size of window's width in pixels
WINDOWHEIGHT = 480 # size of window's height in pix
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 10 # size of gap between boxes in pixels
BOARDWIDTH = 8 # number of columns of icons
BOARDHEIGHT = 6 # number of rows of icons
assert(BOARDWIDTH*BOARDHEIGHT)%2==0,'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH-(BOARDWIDTH*(BOXSIZE + GAPSIZE)))/2)
YMARGIN = int((WINDOWHEIGHT-(BOARDHEIGHT*(BOXSIZE + GAPSIZE)))/2)

#             R  G  B
GRAY     = (100,100,100)
NAVYBLUE = (60,60,100)
WHITE    = (255,255,255)
RED      = (255,0,0)
GREEN    = (0,255,0)
BLUE     = (0,0,255)
YELLOW   = (255,255,0)
ORANGE   = (255,128,0)
PURPLE   = (255,0,255)
CYAN     = (0,255,255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE
TEXTCOLOR = WHITE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED,GREEN,BLUE,YELLOW,ORANGE,PURPLE,CYAN)
ALLSHAPES = (DONUT,SQUARE,DIAMOND,LINES,OVAL)
assert len(ALLCOLORS)*len(ALLSHAPES)*2>=BOARDWIDTH*BOARDHEIGHT,"Board is too big for the number of shapes/colors defined"

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))

    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 48)

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x,y) of the first box clicked.
    score = 0 # initial amount of points
    streak = 0 # score multiplier
    time = RUNTIME # time counter

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        # change color of score status depending on streak
        scoreColor = WHITE
        if streak == 3:
            scoreColor = ORANGE
        elif streak == 2:
            scoreColor = YELLOW

        scoreSurf, scoreRect = makeTextObjs('Score: ' + str(score), BASICFONT, TEXTCOLOR)
        scoreRect.topleft = (WINDOWWIDTH - 100, 10)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

        seconds = FPSCLOCK.tick()/15
        time -= seconds
        timerSurf, timerRect = makeTextObjs('Time: ' + str(round(time)), BASICFONT, TEXTCOLOR)
        timerRect.topleft = (WINDOWWIDTH - 610, 10)
        DISPLAYSURF.blit(timerSurf, timerRect)

        if time < 0:
            pygame.time.wait(2000)
            gameOver(score)

            # Reset the board
            DISPLAYSURF.fill(BGCOLOR)
            mainBoard = getRandomizedBoard()
            revealedBoxes = generateRevealedBoxesData(False)

            # Show the fully unrevealed board for a second.
            drawBoard(mainBoard, revealedBoxes)
            pygame.display.update()
            pygame.time.wait(1000)

            # Replay the start game animation.
            startGameAnimation(mainBoard)
            score = 0
            time = RUNTIME

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type==KEYUP and event.key==K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard,[(boxx,boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard,firstSelection[0],firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard,boxx,boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0],firstSelection[1]),(boxx,boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                        if score >= 2:
                            # minus one for every wrong guess if you have more than zero points
                            score -= 2
                        elif score == 1:
                            score = 0
                        # reset streak for wrong guess.
                        streak = 0
                    elif icon1shape == icon2shape and icon1color == icon2color and not hasWon(revealedBoxes):
                        # plus 5 times streak for every correct guess
                        if streak < 3:
                            streak += 1
                        score += (5*streak) if streak > 0 else 5
                    elif hasWon(revealedBoxes): # check if all pairs found
                        score += (5*streak) if streak > 0 else 5
                        gameOver(score)
                        pygame.time.wait(2000)

                        # Reset the board
                        DISPLAYSURF.fill(BGCOLOR)
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                        score = 0
                        streak = 0
                        time = RUNTIME

                    firstSelection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes


def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape,color))

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(BOARDWIDTH*BOARDHEIGHT/2) # calculate how many icons are needed
    icons = icons[:numIconsUsed]*2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx*(BOXSIZE+GAPSIZE) + XMARGIN
    top  = boxy*(BOXSIZE+GAPSIZE) + YMARGIN
    return(left,top)


def getBoxAtPixel(x,y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx,boxy)
            boxRect = pygame.Rect(left,top,BOXSIZE,BOXSIZE)
            if boxRect.collidepoint(x,y):
                return (boxx,boxy)
    return (None,None)


def drawIcon(shape, color, boxx, boxy):
    quarter = int(BOXSIZE*0.25) # syntactic sugar
    half = int(BOXSIZE*0.5) # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
    # Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF,color,(left + half, top + half),half-5)
        pygame.draw.circle(DISPLAYSURF,BGCOLOR, (left + half, top + half),quarter-5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF,color,(left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF,color,((left + half, top),(left + BOXSIZE - 1, top + half),(left + half, top + BOXSIZE - 1),(left,top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF,color,(left,top+i),(left+i,top))
            pygame.draw.line(DISPLAYSURF,color,(left+i,top+BOXSIZE-1),(left+BOXSIZE-1,top+i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF,color,(left,top+quarter,BOXSIZE,half))


def getShapeAndColor(board, boxx, boxy):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed."boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0],box[1])
        pygame.draw.rect(DISPLAYSURF,BGCOLOR,(left,top,BOXSIZE,BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape,color,box[0],box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF,BOXCOLOR,(left,top,coverage,BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board,boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE,(-REVEALSPEED)-1,-REVEALSPEED):
        drawBoxCovers(board,boxesToReveal,coverage)


def coverBoxesAnimation(board,boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE+REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board,boxesToCover,coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx,boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF,BOXCOLOR,(left,top,BOXSIZE,BOXSIZE))
            else:
                # Draw a (revealed) icon.
                shape, color = getShapeAndColor(board,boxx,boxy)
                drawIcon(shape,color,boxx,boxy)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx,boxy)
    pygame.draw.rect(DISPLAYSURF,HIGHLIGHTCOLOR,(left-5,top-5,BOXSIZE+10,BOXSIZE+10),4)


def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x,y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8,boxes)

    drawBoard(board,coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def gameOver(score):
    DISPLAYSURF.fill(BGCOLOR)

    # Draw game over text.
    titleSurf, titleRect = makeTextObjs('Game Over', BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    # load high score.
    with open('highscore.txt', 'r') as fileIn:
            highscore = int(fileIn.read().strip())

    if score > highscore:
        # Draw the score
        scoreSurf, scoreRect = makeTextObjs('Score: ' + str(score), BASICFONT, TEXTCOLOR)
        scoreRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

        # Draw the new high score text.
        subTitSurf, subTitRect = makeTextObjs('NEW HIGH SCORE!', BASICFONT, TEXTCOLOR)
        subTitRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 65)
        DISPLAYSURF.blit(subTitSurf, subTitRect)

        # save new highscore
        with open('highscore.txt', 'w') as fileIn:
            fileIn.write(str(score))

    else:
        # Draw the score
        scoreSurf, scoreRect = makeTextObjs('High Score: ' + str(highscore), BASICFONT, TEXTCOLOR)
        scoreRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True


if __name__ == '__main__':
    main()
