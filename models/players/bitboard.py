import numpy as np
from copy import deepcopy
from models.move import Move
from models.board import Board
  
ZERO = np.uint64(0)
ONE = np.uint64(1)
SIZE = np.uint64(8)

BB_UP = np.uint64(0xFFFFFFFFFFFFFF00)
BB_DOWN = np.uint64(0x00FFFFFFFFFFFFFF)
BB_LEFT = np.uint64(0xFEFEFEFEFEFEFEFE)
BB_RIGHT = np.uint64(0x7F7F7F7F7F7F7F7F)
BB_UP_LEFT = np.uint64(0xFEFEFEFEFEFEFE00)
BB_UP_RIGHT = np.uint64(0x7F7F7F7F7F7F7F00)
BB_DOWN_LEFT = np.uint64(0x00FEFEFEFEFEFEFE)
BB_DOWN_RIGHT = np.uint64(0x007F7F7F7F7F7F7F)

def next_up(x):
  return (x << SIZE) & BB_UP
def next_down(x):
  return (x >> SIZE) & BB_DOWN
def next_left(x):
  return (x << ONE) & BB_LEFT
def next_right(x):
  return (x >> ONE) & BB_RIGHT
def next_up_left(x):
  return (x << (SIZE + ONE)) & BB_UP_LEFT
def next_up_right(x):
  return (x << (SIZE - ONE)) & BB_UP_RIGHT
def next_down_left(x):
  return (x >> (SIZE - ONE)) & BB_DOWN_LEFT
def next_down_right(x):
  return (x >> (SIZE + ONE)) & BB_DOWN_RIGHT

next_move_directions = [next_up,
         next_down,
         next_left,
         next_right,
         next_up_left,
         next_up_right,
         next_down_left,
         next_down_right]

def print_bbn(bbn):
  mask = np.uint64(1) << np.uint64(63)
  for i in range(8):
    line = ""
    for j in range(8):
      line += ("1" if bbn & mask else "0")
      mask >>= np.uint64(1)
    print line

def print_pov(bb):
  mask = np.uint64(1) << np.uint64(63)
  for i in range(8):
    line = ""
    for j in range(8):
      if (bb.me & mask):
        line += 'M'
      elif (bb.op & mask):
        line += 'O'
      else:
        line += '.'
      mask >>= np.uint64(1)
    print line

def find_moves(bb):
  me = bb.me
  op = bb.op
  empty = bb.get_empty()
  
  moves = np.uint64(0)
  candidates = op & (me << SIZE)
  for next_dir in next_move_directions:
    candidates = op & next_dir(me)
    while (candidates != ZERO):
      moves     |= empty & next_dir(candidates)
      candidates = op    & next_dir(candidates)
  return moves

def find_moves_iter(bb):
  moves_int = find_moves(bb)
  moves = ()
  while (moves_int):
    without_lsb = moves_int & (moves_int-ONE)
    moves += (moves_int - without_lsb,)
    moves_int = without_lsb
  return moves

def convert_move(bbm):
  i = 0
  j = 0
  movel = np.uint64(bbm)
  movec = np.uint64(bbm)
  while(movel):
    movel = next_up(movel)
    i += 1
  while(movec):
    movec = next_left(movec)
    j += 1
  return Move(i, j)

def get_move(move):
  bbm = np.uint64(1) << np.uint64(63)
  x = np.uint64(move.x)
  y = np.uint64(move.y)
  bbm >>= (SIZE*(x-ONE))
  bbm >>= (y-ONE)
  return bbm



def fazBoard(bb):
  board = Board(None)
  moves_int_a = bb.me
  moves_a = ()
  while (moves_int_a):
    without_lsb = moves_int_a & (moves_int_a-ONE)
    moves_a += (moves_int_a - without_lsb,)
    moves_int_a = without_lsb
  moves_int_b = bb.op
  moves_b = ()
  while (moves_int_b):
    without_lsb = moves_int_b & (moves_int_b-ONE)
    moves_b += (moves_int_b - without_lsb,)
    moves_int_b = without_lsb
  for move in moves_a:
    board.board[convert_move(move).x][convert_move(move).y] = board.BLACK
  for move in moves_b:
    board.board[convert_move(move).x][convert_move(move).y] = board.WHITE
  return board

class BitBoard:

  def __init__(self, me, op):
    self.me = me
    self.op = op

  def get_empty(self):
    return ~(self.me | self.op)

  def clone(self):
    return BitBoard(deepcopy(self.me), deepcopy(self.op))

  def play(self, move):
    me = self.me
    op = self.op
    empty = self.get_empty()

    for next_dir in next_move_directions:
      walk = next_dir(move)
      line = np.uint64(0)
      while (walk & op):
        line |= walk
        walk = next_dir(walk)
      if (walk & me):
        op &= ~line
        me |= line
    self.me = me | move
    self.op = op

    return self

  def change_player(self):
    self.me, self.op = self.op, self.me
    return self
  
  def play_c(self, move):
    return self.clone().play(move)

  def change_player_c(self):
    return self.clone().change_player()

  def fullplay_c(self, move):
    return self.clone().play(move).change_player()
  

def bb_from(board, color):
  me = np.uint64(0)
  op = np.uint64(0)
  
  color_op = board._opponent(color)
  
  n = np.uint64(64)
  for i in range(1, 9):
    for j in range(1, 9):
      n -= np.uint64(1)
      if (board.get_square_color(i,j) is color):
        me |= np.uint64(1) << n
      elif (board.get_square_color(i,j) is color_op):
        op |= np.uint64(1) << n
  
  return BitBoard(me, op)
