from models.players.bitboard import *
from views.console_board_view import ConsoleBoardView

inf_pos = float("inf")
inf_neg = -inf_pos

def bitcount(x):
  count = 0
  while (x):
    x &= (x-ONE)
    count += 1
  return count

def h_movements(bb):
  return bitcount(find_moves(bb)) - bitcount(find_moves(bb.change_player_c()))

def h_score(bb):
  count_a = bitcount(bb.me)
  count_b = bitcount(bb.op)
  if count_a > count_b:
    return inf_pos
  elif count_b > count_a:
    return inf_neg
  else:
    return 0
  
  
  
