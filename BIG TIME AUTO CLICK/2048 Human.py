import pickle
import copy
import pygame
import neat
import os
import random
pygame.font.init()

# Big Board W&H / 5x5 game boards in it + 20 px padding
BIG_HW = 970
BIG_PAD = 20
# Small Game Board W&H
SMALL_HW = 170
SMALL_PAD = 2

TILE_HW = 40
STAT_FONT = pygame.font.SysFont("comicsans", 50)
WHITE_COLOR = (255, 255, 255)

TILE_2 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "2.png")), (TILE_HW, TILE_HW))
TILE_4 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "4.png")), (TILE_HW, TILE_HW))
TILE_8 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "8.png")), (TILE_HW, TILE_HW))
TILE_16 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "16.png")), (TILE_HW, TILE_HW))
TILE_32 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "32.png")), (TILE_HW, TILE_HW))
TILE_64 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "64.png")), (TILE_HW, TILE_HW))
TILE_128 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "128.png")), (TILE_HW, TILE_HW))
TILE_256 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "256.png")), (TILE_HW, TILE_HW))
TILE_512 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "512.png")), (TILE_HW, TILE_HW))
TILE_1024 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "1024.png")), (TILE_HW, TILE_HW))
TILE_2048 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "2048.png")), (TILE_HW, TILE_HW))
TILE_4096 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "4096.png")), (TILE_HW, TILE_HW))
TILE_8192 = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "8192.png")), (TILE_HW, TILE_HW))
TILES = (TILE_2, TILE_4, TILE_8, TILE_16, TILE_32, TILE_64, TILE_128, TILE_256, TILE_512, TILE_1024, TILE_2048,
         TILE_4096, TILE_8192)
big_board = [[None, None, None, None, None],
             [None, None, None, None, None],
             [None, None, None, None, None],
             [None, None, None, None, None],
             [None, None, None, None, None]]


class Tile:

    def __init__(self, board):
        self.x = random.randrange(len(board.boxes))
        self.y = random.randrange(len(board.boxes))
        # if selected position is already assigned, random another one
        while board.boxes[self.y][self.x] is not None:
            self.x = random.randrange(len(board.boxes))
            self.y = random.randrange(len(board.boxes))
        board.boxes[self.y][self.x] = self
        # assign position and add padding
        self.pos = (SMALL_PAD + self.x*(SMALL_PAD + TILE_HW) + board.x, SMALL_PAD + self.y*(SMALL_PAD + TILE_HW) + board.y)
        self.value = 0
        if random.random() > 0.9:
            self.value = 1
        self.img = TILES[self.value]

    # update tile position // to be called with board.make_move()
    def move_tile(self, x, y, board):
        self.pos = (SMALL_PAD + x*(SMALL_PAD + TILE_HW) + board.x, SMALL_PAD + y*(SMALL_PAD + TILE_HW) + board.y)

    def double_tile(self):
        self.value += 1
        self.img = TILES[self.value]

    def collide(self):
        pass

    def fuse(self):
        pass

    def draw(self, win):
        win.blit(self.img, self.pos)


class Board:
    popped = False

    def __init__(self):
        while not self.popped:
            for y in range(len(big_board)):
                if self.popped:
                    break
                for x in range(len(big_board[y])):
                    if big_board[y][x] is None:
                        big_board[y][x] = self
                        self.x = BIG_PAD + x*(BIG_PAD + SMALL_HW)
                        self.y = BIG_PAD + y*(BIG_PAD + SMALL_HW)
                        self.popped = True
                        break
        # map the boxes for easier tracking
        self.boxes = [[None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None]]

    # return true if the board is full of tiles / used to pop out the board
    def board_full(self):
        for x in self.boxes:
            for y in x:
                if y is None:
                    return False
        return True

    # return True if no moves are available to the board
    def locked_board(self):
        if self.make_move("up", test=True) or self.make_move("down", test=True) \
                or self.make_move("left", test=True) or self.make_move("right", test=True):
            return False
        return True

    def add_tile(self):
        if not self.board_full():
            Tile(self)

    # position is correct but won't update yet
    # make it to dir = up or down or left or right
    # test argument is for checking if the board have any available moves without messing with it
    def make_move(self, dir, test=False):
        made_move = False
        if dir == "up":
            # won't care about self.boxes[0]
            # select every number and move them to the highest position available
            for y in range(1, len(self.boxes)):
                for x in range(len(self.boxes)):
                    local_move = False
                    if self.boxes[y][x] is not None:
                        best_move = None
                        for i in reversed(range(y)):
                            if self.boxes[i][x] is None:
                                # keep the best move y position stored and move it at the end
                                best_move = i
                                continue
                            elif self.boxes[i][x].value == self.boxes[y][x].value:
                                if self.boxes[i][x].value < len(TILES) - 1:
                                    if not test:
                                        self.boxes[y][x] = None
                                        self.boxes[i][x].double_tile()
                                    local_move = True
                                    made_move = True
                                break
                            else:
                                break
                        if best_move is not None and not local_move:
                            if not test:
                                self.boxes[y][x].move_tile(x, best_move, self)
                                self.boxes[best_move][x] = self.boxes[y][x]
                                self.boxes[y][x] = None
                            made_move = True
        if dir == "down":
            # will iterate range(4-1) in reverse : 2, 1, 0
            for y in reversed(range(len(self.boxes) - 1)):
                for x in range(len(self.boxes)):
                    local_move = False
                    if self.boxes[y][x] is not None:
                        best_move = None
                        for i in range(y + 1, len(self.boxes)):
                            if self.boxes[i][x] is None:
                                # keep the best move y position stored and move it at the end
                                best_move = i
                                continue
                            elif self.boxes[i][x].value == self.boxes[y][x].value:
                                if self.boxes[i][x].value < len(TILES) - 1:
                                    if not test:
                                        self.boxes[y][x] = None
                                        self.boxes[i][x].double_tile()
                                    local_move = True
                                    made_move = True
                                break
                            else:
                                break
                        if best_move is not None and not local_move:
                            if not test:
                                self.boxes[y][x].move_tile(x, best_move, self)
                                self.boxes[best_move][x] = self.boxes[y][x]
                                self.boxes[y][x] = None
                            made_move = True
        if dir == "left":
            for x in range(1, len(self.boxes)):
                for y in range(len(self.boxes)):
                    local_move = False
                    if self.boxes[y][x] is not None:
                        best_move = None
                        for i in reversed(range(x)):
                            if self.boxes[y][i] is None:
                                # keep the best move y position stored and move it at the end
                                best_move = i
                                continue
                            elif self.boxes[y][i].value == self.boxes[y][x].value:
                                if self.boxes[y][i].value < len(TILES) - 1:
                                    if not test:
                                        self.boxes[y][x] = None
                                        self.boxes[y][i].double_tile()
                                    local_move = True
                                    made_move = True
                                break
                            else:
                                break
                        if best_move is not None and not local_move:
                            if not test:
                                self.boxes[y][x].move_tile(best_move, y, self)
                                self.boxes[y][best_move] = self.boxes[y][x]
                                self.boxes[y][x] = None
                            made_move = True
        if dir == "right":
            for x in reversed(range(len(self.boxes) - 1)):
                for y in range(len(self.boxes)):
                    local_move = False
                    if self.boxes[y][x] is not None:
                        best_move = None
                        for i in range(x + 1, len(self.boxes)):
                            if self.boxes[y][i] is None:
                                # keep the best move y position stored and move it at the end
                                best_move = i
                                continue
                            elif self.boxes[y][i].value == self.boxes[y][x].value:
                                if self.boxes[y][i].value < len(TILES) - 1:
                                    if not test:
                                        self.boxes[y][x] = None
                                        self.boxes[y][i].double_tile()
                                    local_move = True
                                    made_move = True
                                break
                            else:
                                break
                        if best_move is not None and not local_move:
                            if not test:
                                self.boxes[y][x].move_tile(best_move, y, self)
                                self.boxes[y][best_move] = self.boxes[y][x]
                                self.boxes[y][x] = None
                            made_move = True

        # need a fix, currently doesn't check if there is available moves or not
        if made_move and not test:
            self.add_tile()
        return made_move

    def draw(self, win):
        pygame.draw.rect(win, WHITE_COLOR, (self.x, self.y, SMALL_HW, SMALL_HW))


def draw_window(win, boards):
    for board in boards:
        board.draw(win)
        for line_board in board.boxes:
            for tile in line_board:
                if tile is not None:
                    tile.draw(win)

    pygame.display.update()


# Main Loop
boards = []
rem = []
for _ in range(25):
    boards.append(Board())
for board in boards:
    Tile(board)

run = True
while run:
    win = pygame.display.set_mode((BIG_HW, BIG_HW))
    clock = pygame.time.Clock()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # used to pop tiles in all boards and remove boards that are full // modify this later to implement AI
        if keys[pygame.K_DOWN]:
            for board in boards:
                board.make_move("down")
                if board.locked_board():
                    rem.append(board)
        if keys[pygame.K_UP]:
            for board in boards:
                board.make_move("up")
                if board.locked_board():
                    rem.append(board)
        if keys[pygame.K_LEFT]:
            for board in boards:
                board.make_move("left")
                if board.locked_board():
                    rem.append(board)
        if keys[pygame.K_RIGHT]:
            for board in boards:
                board.make_move("right")
                if board.locked_board():
                    rem.append(board)
        for board in rem:
            boards.remove(board)
        rem = []

    draw_window(win, boards)

# have to define neat network parameters
# how many inputs and which ones
# probably 4 outputs, higher define if up,down,left,right
# fitness would like take in account new big tile +5, staying alive +0.1, dying -=1 etc

# test code

'''test_board = Board()
test2_board = Board()
test3_board = Board()
test_tile = Tile(test_board)
test2_tile = Tile(test2_board)
test3_tile = Tile(test3_board)
boards = [test_board, test2_board, test3_board]'''
