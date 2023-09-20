# Hua-Rong-Dao-Solver
I implemented a program using both Depth-First Search and A* Search to solve the Hua Rong Dao puzzle. 

I have considered the variant of the puzzle with 4 kinds of pieces: 1 2x2 piece; 5 1x2 pieces and 4 1x1 pieces. 

The goal is to find the sequence of moves that results in the least piece moves for the 2x2 piece to be above the bottom opening.

Each command specifies the search algorithm, one plain-text input file, and one plain-text output file
containing the solution found by the search algorithm.

In the input and output files, I have represented each state in the following format:

- Each state is a grid of 20 characters.
- The grid has 5 rows with 4 characters per row.
- The empty squares are denoted by the period symbol.
- The 2x2 piece is denoted by 1.
- The single pieces are denoted by 2.
- A horizontal 1x2 piece is denoted by < on the left and > on the right.
- A vertical 1x2 piece is denoted by ^ on the top and v on the bottom (lower cased letter v).

eg. 
^^^^
vvvv
22..
11<>
1122

The innput file contains one state, representing a puzzle's initial state.

The output file contains a sequence of states. The first state in the sequence is the initial
configuration of the puzzle. The last state is a goal state. There is one empty line between any two
consecutive states.

Given, A* search requires an admissible heuristic function to find an optimal solution, I have implemented the Mnhattan distance
heuristic for this problem.
