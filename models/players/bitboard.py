from numpy import uint64 as i64
from copy import deepcopy
from models.move import Move
from models.board import Board
  
ZERO = i64(0)
ONE = i64(1)
TWO = i64(2)
THREE = i64(3)
FOUR = i64(4)
SIZE = i64(8)
SIZEM1 = i64(7)
SIZEP1 = i64(9)

BB_UP = i64(0xFFFFFFFFFFFFFF00)
BB_DOWN = i64(0x00FFFFFFFFFFFFFF)
BB_LEFT = i64(0xFEFEFEFEFEFEFEFE)
BB_RIGHT = i64(0x7F7F7F7F7F7F7F7F)
BB_UP_LEFT = i64(0xFEFEFEFEFEFEFE00)
BB_UP_RIGHT = i64(0x7F7F7F7F7F7F7F00)
BB_DOWN_LEFT = i64(0x00FEFEFEFEFEFEFE)
BB_DOWN_RIGHT = i64(0x007F7F7F7F7F7F7F)

BB_UPDOWN = BB_UP & BB_DOWN
BB_LEFTRIGHT = BB_LEFT & BB_RIGHT
BB_UPLEFTDOWNRIGHT = BB_UP_LEFT & BB_DOWN_RIGHT
BB_UPRIGHTDOWNLEFT = BB_UP_RIGHT & BB_DOWN_LEFT

def next_up(x):
  return (x << SIZE) & BB_UP
def next_down(x):
  return (x >> SIZE) & BB_DOWN
def next_left(x):
  return (x << ONE) & BB_LEFT
def next_right(x):
  return (x >> ONE) & BB_RIGHT
def next_up_left(x):
  return (x << SIZEP1) & BB_UP_LEFT
def next_up_right(x):
  return (x << SIZEM1) & BB_UP_RIGHT
def next_down_left(x):
  return (x >> SIZEM1) & BB_DOWN_LEFT
def next_down_right(x):
  return (x >> SIZEP1) & BB_DOWN_RIGHT

next_move_directions = (next_up,
         next_down,
         next_left,
         next_right,
         next_up_left,
         next_up_right,
         next_down_left,
         next_down_right)

def print_bbn(bbn):
  """imprime um numero 64 bits em bitboard 8x8"""
  mask = i64(1) << i64(63)
  for i in range(8):
    line = ""
    for j in range(8):
      line += ("1" if bbn & mask else "0")
      mask >>= i64(1)
    print(line)

def print_pov(bb):
  """imprime um tabuleiro do meu ponto de vista"""
  mask = i64(1) << i64(63)
  for i in range(8):
    line = ""
    for j in range(8):
      if (bb.me & mask):
        line += 'M'
      elif (bb.op & mask):
        line += 'O'
      else:
        line += '.'
      mask >>= i64(1)
    print(line)

def bitcount(x):
  """conta quantos bits '1' o numero x possui"""
  count = 0.0
  while (x):
    x &= (x-ONE)
    count += 1
  return count

def empty_nbors(bb):
  """retorna as posicoes vazias vizinhas a
    pecas minhas e pecas do inimigo"""
  me_nbors = i64(0)
  op_nbors = i64(0)
  for direction in next_move_directions:
    me_nbors |= (direction(bb.me) & empty)
    op_nbors |= (direction(bb.op) & empty)
  return me_nbors, op_nbors

def find_moves(bb):
  """acha movimentos possiveis para mim"""
  me = bb.me
  op = bb.op
  empty = bb.get_empty()
  
  moves = i64(0)
  
  viable      = op & BB_UPDOWN
  candidates  = viable & (me << SIZE)
  candidates |= viable & (candidates << SIZE)
  candidates |= viable & (candidates << SIZE)
  candidates |= viable & (candidates << SIZE)
  candidates |= viable & (candidates << SIZE)
  candidates |= viable & (candidates << SIZE)
  moves      |= empty  & (candidates << SIZE)
  
  viable      = op & BB_UPDOWN
  candidates  = viable & (me >> SIZE)
  candidates |= viable & (candidates >> SIZE)
  candidates |= viable & (candidates >> SIZE)
  candidates |= viable & (candidates >> SIZE)
  candidates |= viable & (candidates >> SIZE)
  candidates |= viable & (candidates >> SIZE)
  moves      |= empty  & (candidates >> SIZE)
  
  viable      = op & BB_LEFTRIGHT
  candidates  = viable & (me << ONE)
  candidates |= viable & (candidates << ONE)
  candidates |= viable & (candidates << ONE)
  candidates |= viable & (candidates << ONE)
  candidates |= viable & (candidates << ONE)
  candidates |= viable & (candidates << ONE)
  moves      |= empty  & (candidates << ONE)
  
  viable      = op & BB_LEFTRIGHT
  candidates  = viable & (me >> ONE)
  candidates |= viable & (candidates >> ONE)
  candidates |= viable & (candidates >> ONE)
  candidates |= viable & (candidates >> ONE)
  candidates |= viable & (candidates >> ONE)
  candidates |= viable & (candidates >> ONE)
  moves      |= empty  & (candidates >> ONE)
  
  viable      = op & BB_UPLEFTDOWNRIGHT
  candidates  = viable & (me << SIZEP1)
  candidates |= viable & (candidates << SIZEP1)
  candidates |= viable & (candidates << SIZEP1)
  candidates |= viable & (candidates << SIZEP1)
  candidates |= viable & (candidates << SIZEP1)
  candidates |= viable & (candidates << SIZEP1)
  moves      |= empty  & (candidates << SIZEP1)
  
  viable      = op & BB_UPRIGHTDOWNLEFT
  candidates  = viable & (me << SIZEM1)
  candidates |= viable & (candidates << SIZEM1)
  candidates |= viable & (candidates << SIZEM1)
  candidates |= viable & (candidates << SIZEM1)
  candidates |= viable & (candidates << SIZEM1)
  candidates |= viable & (candidates << SIZEM1)
  moves      |= empty  & (candidates << SIZEM1)
  
  viable      = op & BB_UPRIGHTDOWNLEFT
  candidates  = viable & (me >> SIZEM1)
  candidates |= viable & (candidates >> SIZEM1)
  candidates |= viable & (candidates >> SIZEM1)
  candidates |= viable & (candidates >> SIZEM1)
  candidates |= viable & (candidates >> SIZEM1)
  candidates |= viable & (candidates >> SIZEM1)
  moves      |= empty  & (candidates >> SIZEM1)
  
  viable      = op & BB_UPLEFTDOWNRIGHT
  candidates  = viable & (me >> SIZEP1)
  candidates |= viable & (candidates >> SIZEP1)
  candidates |= viable & (candidates >> SIZEP1)
  candidates |= viable & (candidates >> SIZEP1)
  candidates |= viable & (candidates >> SIZEP1)
  candidates |= viable & (candidates >> SIZEP1)
  moves      |= empty  & (candidates >> SIZEP1)
  
  return moves

def bits_iter(bbn):
  """cria um iterable para cada bit '1' da entrada"""
  bits = []
  append = bits.append # atalho pra funcao bits.append(), fica mais rapido assim
  while (bbn):
    without_lsb = bbn & (bbn-ONE)
    append(bbn - without_lsb)
    bbn = without_lsb
  return bits

def find_moves_iter(bb):
  """iteravel dos movimentos possiveis para mim"""
  return bits_iter(find_moves(bb))

def bbm_to_tuple(bbm):
  """converte bit em bitboard para tupla de x, y"""
  i = 0
  j = 0
  movel = i64(bbm)
  movec = i64(bbm)
  while(movel):
    movel = next_up(movel)
    i += 1
  while(movec):
    movec = next_left(movec)
    j += 1
  return i, j

def tuple_to_bbm(move):
  """converte tupla de x, y para bit em bitboard"""
  bbm = i64(1) << i64(63)
  x = i64(move[0])
  y = i64(move[1])
  bbm >>= ((x-ONE) << 3) # x << 3 eh igual a x * 8
  bbm >>= (y-ONE)
  return bbm

def makeBoard(bb):
  """cria uma board da lib do victorlcampos tendo como entrada uma bitboard"""
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
  """classe que representa uma bitboard"""

  def __init__(self, me, op):
    self.me = i64(me)
    self.op = i64(op)

  def __eq__(self, other):
    return self.me == other.me and self.op == other.op

  def __hash__(self):
    return hash(self.me | self.op)

  def get_empty(self):
    """retorna as posicoes vazias da bitboard"""
    return ~(self.me | self.op)

  def clone(self):
    return BitBoard(deepcopy(self.me), deepcopy(self.op))

  def play(self, move):
    """aplica um movimento na bitboard"""
    empty = self.get_empty()

    walk = (move << SIZE) & BB_UP
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk << SIZE) & BB_UP
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move >> SIZE) & BB_DOWN
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk >> SIZE) & BB_DOWN
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move << ONE) & BB_LEFT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk << ONE) & BB_LEFT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move >> ONE) & BB_RIGHT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk >> ONE) & BB_RIGHT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move << SIZEP1) & BB_UP_LEFT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk << SIZEP1) & BB_UP_LEFT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move << SIZEM1) & BB_UP_RIGHT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk << SIZEM1) & BB_UP_RIGHT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move >> SIZEM1) & BB_DOWN_LEFT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk >> SIZEM1) & BB_DOWN_LEFT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    walk = (move >> SIZEP1) & BB_DOWN_RIGHT
    line = i64(0)
    while (walk & self.op):
      line |= walk
      walk = (walk >> SIZEP1) & BB_DOWN_RIGHT
    if (walk & self.me):
      self.op &= ~line
      self.me |= line

    self.me |= move
    return self

  def change_player(self):
    """troca o turno (quem vai fazer o
       proximo movimento) da bitboard"""
    self.me, self.op = self.op, self.me
    return self
  
  def play_c(self, move):
    """aplica um movimento numa copia da bitboard"""
    return self.clone().play(move)

  def change_player_c(self):
    """troca o turno (quem vai fazer o
       proximo movimento) numa copia da bitboard"""
    return self.clone().change_player()

  def fullplay_c(self, move):
    """aplica um movimento e troca o turno
       (quem vai fazer o proximo movimento)
       numa copia da bitboard"""
    return self.clone().play(move).change_player()
  

def bb_from(board, color):
  """converte uma board da lib do victorlcampos em uma BitBoard"""
  me = i64(0)
  op = i64(0)
  
  color_op = board._opponent(color)
  
  n = i64(64)
  for i in range(1, 9):
    for j in range(1, 9):
      n -= ONE
      if (board.get_square_color(i,j) == color):
        me |= ONE << n
      elif (board.get_square_color(i,j) == color_op):
        op |= ONE << n
  
  return BitBoard(me, op)
