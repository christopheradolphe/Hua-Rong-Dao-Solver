from copy import deepcopy
from heapq import heappush, heappop
import heapq  
import time
import argparse
import sys

#====================================================================================

char_goal = '1'
char_single = '2'
single_allowable_right = ['<', '2']
single_allowable_left = ['>', '2']
single_allowable_above = ['v', '2']
single_allowable_below = ['^', '2']
vertical_double_sideways = [['^', 'v'], ['1', '1']]
horizontal_double_above_below = [['<', '>'],['1', '1']]



class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """
        self.grid = []
        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()

    def empty_slots(self):
      #Returns list of tuples in form of [(x1,y1), (x2,y2)]
        empty = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == ".":
                    empty.append((j,i))
        return empty

    def move(self, x_coord, y_coord, direction):
        """
        :param coord: x and y coordinate of the upper left corner of piece being moved
        :type coord: Tuple 
        :param is_single: Direction 
        :type is_single: char (l: left, r:right, u:up, d:down)
        """
        #Find the piece that you want to move based on the x and y coordinate 
        for piece in self.pieces:
            if piece.coord_x == x_coord and piece.coord_y == y_coord:
                if direction == 'r':
                    piece.coord_x += 1
                if direction == 'l':
                    piece.coord_x -= 1
                if direction == 'u':
                    piece.coord_y -= 1
                if direction == 'd':
                    piece.coord_y += 1
        self.__construct_grid()
        return self
        #To move a piece change x or y coordinate of top left corner piece

    def goal_position(self):
        for piece in self.pieces:
            if piece.is_goal:
                return (piece.coord_x, piece.coord_y)         
        return None
    
    def manhattan_distance(self):
        (x, y) = self.goal_position()
        return abs(1-x) + abs(3-y)

        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, g, depth, parent=None, h=0):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.g = g
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.
        self.h = h
        self.f = self.g + self.h
    
    def possible_move_finder(self):
        #Find all empty slots
        empty_spaces = self.board.empty_slots()
        viable_moves = []
        #Format viable moves as: (piece_location, movement)
        #Piece location is location of top left coordinate of piece
        #Find all pieces around that empty slot
        for elem in empty_spaces:
            (x_coord, y_coord) = elem
            #Viability rules for solo space:
            if x_coord > 0:
                if self.board.grid[y_coord][x_coord - 1] in single_allowable_left:
                    if self.board.grid[y_coord][x_coord - 1] == '>':
                        viable_moves.append(((y_coord, x_coord-2, 'r')))
                    else:
                        viable_moves.append((y_coord, x_coord-1, 'r'))
            if x_coord < 3:
                if self.board.grid[y_coord][x_coord + 1] in single_allowable_right:
                        viable_moves.append((y_coord, x_coord+1, 'l'))
            if y_coord > 0:
                if self.board.grid[y_coord-1][x_coord] in single_allowable_below:
                    if self.board.grid[y_coord][x_coord - 1] == 'v':
                        viable_moves.append(((y_coord-2, x_coord, 'd')))
                    else:
                        viable_moves.append((y_coord-1, x_coord, 'd'))
            if y_coord < 4:
                if self.board.grid[y_coord+1][x_coord] in single_allowable_above:
                    viable_moves.append((y_coord+1, x_coord, 'u'))

        #Check if empty spaces are connected
        #Horizontally Connected
        (E1_x, E1_y) = empty_spaces[0]
        (E2_x, E2_y) = empty_spaces[1]

        if E1_y == E2_y:
            if E1_x == E2_x - 1:
                if E1_y > 0:
                    if [self.board.grid[E1_y - 1][E1_x], self.board.grid[E1_y - 1][E2_x]] in horizontal_double_above_below:
                        if self.board.grid[E1_y - 1][E1_x] == '1':
                            viable_moves.append(((E1_y-2, E1_x, 'd')))
                        else:
                            viable_moves.append((E1_y - 1, E1_x, 'd'))
                if E1_y < 4:
                    if [self.board.grid[E1_y + 1][E1_x], self.board.grid[E1_y + 1][E2_x]] in horizontal_double_above_below:
                        viable_moves.append((E1_y + 1, E1_x, 'u'))
            if E1_x == E2_x + 1:
                if E1_y > 0:
                    if [self.board.grid[E1_y - 1][E2_x], self.board.grid[E1_y - 1][E1_x]] in horizontal_double_above_below:
                        if self.board.grid[E1_y - 1][E2_x] == '1':
                            viable_moves.append((E1_y-2, E2_x, 'd'))
                        else:
                            viable_moves.append((E1_y - 1, E2_x, 'd'))
                if E1_y < 4:
                    if [self.board.grid[E1_y + 1][E2_x], self.board.grid[E1_y + 1][E1_x]] in horizontal_double_above_below:
                        viable_moves.append((E1_y + 1, E2_x, 'u'))

        #Vertically Connected
        if E1_x == E2_x:
            if E1_y == E2_y - 1:
                if E1_x > 0:
                    if [self.board.grid[E1_y][E1_x - 1], self.board.grid[E2_y][E2_x - 1]] in vertical_double_sideways:
                        if self.board.grid[E1_y][E1_x - 1] == '1':
                            viable_moves.append(((E1_y, E1_x - 2, 'r')))
                        else:
                            viable_moves.append((E1_y, E1_x - 1, 'r'))
                if E1_x < 3:
                    if [self.board.grid[E1_y][E1_x + 1], self.board.grid[E2_y][E2_x + 1]] in vertical_double_sideways:
                        viable_moves.append((E1_y, E1_x + 1, 'l'))
            if E1_y == E2_y + 1:
                if E1_x > 0:
                    if [self.board.grid[E2_y][E2_x - 1], self.board.grid[E1_y][E1_x - 1]] in vertical_double_sideways:
                        if self.board.grid[E2_y][E1_x - 1] == '1':
                            viable_moves.append(((E2_y, E2_x - 2, 'r')))
                        else:
                            viable_moves.append((E2_y, E2_x - 1, 'r'))
                if E1_x < 3:
                    if [self.board.grid[E2_y][E2_x + 1], self.board.grid[E1_y][E1_x + 1]] in vertical_double_sideways:
                        viable_moves.append((E2_y, E2_x + 1, 'l'))     
            

            #Singles always allowed
            #If 2x1: ^ allowed if below, ^ allowed if on top, > allowed if on left, < allowed if on right
            #If 2x2: Never allowed

            #Viability rules for connected space:
            #2x1: vertical connection requires vertical block, horizontal block requires horizontal connection
            #2x2: always allowed to move into connected empties
        #Find which pieces can move into that empty slot
        return viable_moves

    def output(self, state, file):
        output_file = open(file, "w")
        if state.parent == None:
            state.print_grid(file)
        else:
            self.output(state.parent, file)
            state.print_grid(file)

    def print_grid(self, filename):
        output_file = open(filename, "a")
        for i in range(self.board.height):
            for j in range(self.board.width):
                output_file.write(self.board.grid[i][j])
            output_file.write("\n")
        output_file.write("\n")
        return None
    
    def print_board(self):
        for i in range(self.board.height):
            for j in range(self.board.width):
                print(self.board.grid[i][j])
            print("\n")
        print("\n") 


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False
    
    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board

def dfs(current_state, output_filename):
    explored = []
    frontier = [current_state]
    cur = None
    while len(frontier) > 0:
        cur = frontier.pop()
        if cur.board.grid not in explored:
            explored.append(cur.board.grid)
            if cur.board.goal_position() == (1,3):
                cur.output(cur, output_filename)
                return cur
            possible_moves = cur.possible_move_finder()
            for move in possible_moves:
                new_board = deepcopy(cur.board)
                (y_start, x_start, direction) = move
                new_board = new_board.move(x_start, y_start, direction)
                frontier.append(State(new_board, cur.f + 1, cur.depth + 1, cur))
    return None

def a_star(current_state, output_filename):
    pq = [(0, current_state.id, current_state)]
    heapq.heapify(pq)
    while len(pq) > 0:
        (val, id, cur) = heapq.heappop(pq)
        cur.print_board()
        if cur.board.goal_position() == (1,3):
            cur.output(cur, output_filename)
            return cur
        possible_moves = cur.possible_move_finder()
        for move in possible_moves:
                new_board = deepcopy(cur.board)
                (y_start, x_start, direction) = move
                new_board = new_board.move(x_start, y_start, direction)
                new_state = State(new_board, cur.g + 1, cur.depth + 1, cur, new_board.manhattan_distance())
                heappush(pq, (cur.g+1 + new_board.manhattan_distance(), new_state.id, new_state))
    return 



if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--inputfile",
    #     type=str,
    #     required=True,
    #     help="The input file that contains the puzzle."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file that contains the solution."
    # )
    # parser.add_argument(
    #     "--algo",
    #     type=str,
    #     required=True,
    #     choices=['astar', 'dfs'],
    #     help="The searching algorithm."
    # )
    # args = parser.parse_args()

    # read the board from the file
    # board = read_from_file(args.inputfile)
    board = read_from_file("inputfile1.txt")


    # if args.algo == 'astar':
    #     a_star(State(board, 0, 0, None, board.manhattan_distance()), args.outputfile)
    # else:
    #     dfs(State(board, 0, 0), args.outputfile)
    
    board_state = State(board, 0,0,None, board.manhattan_distance())
    # final = dfs(board_state)
    a_star(board_state, "outputnew.txt")
