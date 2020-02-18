# -*- coding: cp1252 -*-
from models.players.bitboard import *
from views.console_board_view import ConsoleBoardView
from math import exp
from numpy import uint64 as i64
from timeit import default_timer as timer
import csv

inf_pos = float("inf")
inf_neg = -inf_pos

mask_h  = i64(0x00000000000000FF) # horizontal
mask_v  = i64(0x0101010101010101) # vertical
mask_d1 = i64(0x8040201008040201) # diagonal up-left -> down-right
mask_d2 = i64(0x0102040810204080) # diagonal up-right -> down-left

mask_t_up      = i64(0x7E00000000000000)
mask_t_left    = i64(0x0080808080808000)
mask_t_right   = i64(0x0001010101010100)
mask_t_down    = i64(0x000000000000007E)
mask_t_corners = i64(0x8100000000000081)

ONE = i64(1)
THREE = i64(3)

def print_mask(m):
  for x in ['{0:064b}'.format(m)[i:i+8] for i in range(0, 64, 8)]:
    print(x)

masks = None
masks_dirs = None

def precalc_mask_stability():
  """calcula mascaras binarias pra auxiliar ao
     decidir se alguma peca eh estavel"""
  ONE = i64(1)
  THREE = i64(3)
  mymasks = dict()
  mymasks_dirs = dict()

  for ni in range(8):
    for nj in range(8):
      i = i64(ni)
      j = i64(nj)
      at = (ONE << j) << (i << THREE)
      if ((at | mask_t_corners) == mask_t_corners):
        mymasks[at] = at
        mymasks_dirs[at] = tuple()
      elif ((at | mask_t_up) == mask_t_up):
        mymasks[at] = i64(0xFF00000000000000)
        mymasks_dirs[at] = ((mask_h << (i << THREE)) & ~(at-ONE), (mask_h << (i << THREE)) & (at-ONE)),
      elif ((at | mask_t_left) == mask_t_left):
        mymasks[at] = i64(0x8080808080808080)
        mymasks_dirs[at] = ((mask_v << j) & ~(at-ONE), (mask_v << j) & (at-ONE)),
      elif ((at | mask_t_right) == mask_t_right):
        mymasks[at] = i64(0x0101010101010101)
        mymasks_dirs[at] = ((mask_v << j) & ~(at-ONE), (mask_v << j) & (at-ONE)),
      elif ((at | mask_t_down) == mask_t_down):
        mymasks[at] = i64(0x00000000000000FF)
        mymasks_dirs[at] = ((mask_h << (i << THREE)) & ~(at-ONE), (mask_h << (i << THREE)) & (at-ONE)),
      else:
        mask_ij = (mask_h << (i << THREE)) | (mask_v << j)
        mymasks_dirs[at] = ((mask_h << (i << THREE)) & ~(at-ONE), (mask_h << (i << THREE)) & (at-ONE)), ((mask_v << j) & ~(at-ONE), (mask_v << j) & (at-ONE))
        if (i > j):
          mask_ij |= (mask_d1 << ((i - j) << THREE))
          mymasks_dirs[at] += ((mask_d1 << ((i - j) << THREE)) & ~(at-ONE), (mask_d1 << ((i - j) << THREE)) & (at-ONE)),
        else:
          mask_ij |= (mask_d1 >> ((j - i) << THREE))
          mymasks_dirs[at] += ((mask_d1 >> ((j - i) << THREE)) & ~(at-ONE), (mask_d1 >> ((j - i) << THREE)) & (at-ONE)),
        d = i64(7) - i
        if (d > j):
          mask_ij |= (mask_d2 >> ((d - j) << THREE))
          mymasks_dirs[at] += ((mask_d2 >> ((d - j) << THREE)) & ~(at-ONE), (mask_d2 >> ((d - j) << THREE)) & (at-ONE)),
        else:
          mask_ij |= (mask_d2 << ((j - d) << THREE))
          mymasks_dirs[at] += ((mask_d2 << ((j - d) << THREE)) & ~(at-ONE), (mask_d2 << ((j - d) << THREE)) & (at-ONE)),
        mymasks[at] = mask_ij

  return mymasks, mymasks_dirs

masks, masks_dirs = precalc_mask_stability()

def fake_norm(x, y):
  """formula boba para colocar numeros entre -1 e 1"""
  return 0 if (x + y) == 0 else (x-y)/(x+y)

def h_movements(bb):
  """ numero de movimentos real"""
  me_moves = bitcount(find_moves(bb))
  op_moves = bitcount(find_moves(bb.change_player_c()))
  return fake_norm(me_moves, op_moves)

def h_potential_movements_est(bb):
  """ numero de movimentos potencial estimado
  (isto e, nr. de casas vazias vizinhas a pecas inimigas )"""
  empty = bb.get_empty()

  me_frontier = i64(0)
  op_frontier = i64(0)
  for dir_next in next_move_directions:
    me_frontier |= (dir_next(empty) & bb.me)
    op_frontier |= (dir_next(empty) & bb.op)

  return fake_norm(bitcount(op_frontier), bitcount(me_frontier))

def h_stability(bb):
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida, e nr.
  de pecas de cada jogador que pode ser
  revertida no proximo turno)"""
  
  me_moves_raw = find_moves(bb)
  op_moves_raw = find_moves(bb.change_player_c())
  
  me_unstables_raw = i64(0)
  op_unstables_raw = i64(0)

  moves_iter = bits_iter(me_moves_raw | op_moves_raw)
  #unstables
  for at in moves_iter:
    if at & me_moves_raw:
      for next_dir in next_move_directions:
        walk = next_dir(at)
        line = i64(0)
        while (walk & bb.op):
          line |= walk
          walk = next_dir(walk)
        if (walk & bb.me):
          op_unstables_raw |= line
    else:
      for next_dir in next_move_directions:
        walk = next_dir(at)
        line = i64(0)
        while (walk & bb.me):
          line |= walk
          walk = next_dir(walk)
        if (walk & bb.op):
          me_unstables_raw |= line

  me_unstables = bitcount(me_unstables_raw)
  op_unstables = bitcount(op_unstables_raw)

  me_stables = 0.0
  op_stables = 0.0

  occupied = bb.me | bb.op

  me_possible_stables_iter = bits_iter(bb.me & ~me_unstables_raw)
  op_possible_stables_iter = bits_iter(bb.op & ~op_unstables_raw)
  for at in me_possible_stables_iter:
    if (masks[at] | occupied) == occupied:
        me_stables += 1
    elif all(( (mask_left|mask_right|occupied) == occupied or (mask_left & bb.me) == mask_left or (mask_right & bb.me) == mask_right) for mask_left, mask_right in masks_dirs[at]):
        me_stables += 1
  for at in op_possible_stables_iter:
    if (masks[at] | occupied) == occupied:
        op_stables += 1
    elif all(( (mask_left|mask_right|occupied) == occupied or (mask_left & bb.op) == mask_left or (mask_right & bb.op) == mask_right) for mask_left, mask_right in masks_dirs[at]):
        op_stables += 1
  return fake_norm(me_stables+op_unstables, op_stables+me_unstables)

def h_stability_no_unstables(bb):
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida )"""
  occupied = bb.me | bb.op
  me_stables = 0.0
  op_stables = 0.0
  
  #stables
  for at in bits_iter(bb.me):
    if (masks[at] | occupied) == occupied:
        me_stables += 1
    elif all(( (mask_left|mask_right|occupied) == occupied or (mask_left & bb.me) == mask_left or (mask_right & bb.me) == mask_right) for mask_left, mask_right in masks_dirs[at]):
        me_stables += 1
  for at in bits_iter(bb.op):
    if (masks[at] | occupied) == occupied:
        op_stables += 1
    elif all(( (mask_left|mask_right|occupied) == occupied or (mask_left & bb.op) == mask_left or (mask_right & bb.op) == mask_right) for mask_left, mask_right in masks_dirs[at]):
        op_stables += 1
  
  return fake_norm(me_stables, op_stables)

def h_score(bb):
  """ nr. de pontos que cada jogador tem """
  return fake_norm(bitcount(bb.me), bitcount(bb.op))


corners = (ONE << i64(63), # top left
           ONE << i64(56), # top right
           ONE << i64(7),  # lower left
           ONE)            # lower right

def h_corners(bb):
  """ nr. de cantos que cada jogador tem """
  me_corners = 0.0
  op_corners = 0.0
  for corner in corners:
    if bb.me & corner:
      me_corners += 1
    elif bb.op & corner:
      op_corners += 1
      
  return fake_norm(me_corners, op_corners)

def h_score_final(bb):
  """ se empatou = 0.0
      se venci = positivo
      se perdi = negativo"""
  count_a = bitcount(bb.me)
  count_b = bitcount(bb.op)
  return 99999 * (count_a - count_b)

def h_evaluate(bb):
  h1 = h_movements(bb)
  h2 = h_potential_movements_est(bb)
  h3 = h_stability(bb)
  h4 = h_corners(bb)
  h5 = h_score(bb)

  #pesos do alem
  return 5.0*h1 + 10.0*h2 + 30.0*h3 + 20.0*h4 + 20.0*h5

##weights = ((35, 20, 35, 10, 0),
##           (23,8,39,30,0),
##           (5,0,30,15,45))

weights = ((60.0, 35.0,  0.0,  5.0, 0.0),
           (30.0, 15.0, 25.0, 30.0, 0.0),
           (15.0,  0.0, 45.0, 20.0, 20.0))

##weights = ((100,0,0,0,0),
##           (100,0,0,0,0),
##           (100,0,0,0,0))

splits = ( 4.0, 34.0, 64.0)

def h_evaluate_dynamic(bb):
  move_count = bitcount(bb.me | bb.op)
  x = move_count
  h1 = h_movements(bb)
  h2 = h_potential_movements_est(bb)
  h3 = h_stability(bb)
  h4 = h_corners(bb)
  h5 = h_score(bb)
  values = h1, h2, h3, h4, h5
  coeffs = [exp(-(move_count-k)*(move_count-k)/400) for k in splits]
  return sum(c * sum(v * w for v, w in zip(values, w)) for c,w in zip(coeffs,weights))
  
def h_evaluate_dynamic_no_uns(bb):
  move_count = bitcount(bb.me | bb.op)
  h1 = h_movements(bb)
  h2 = h_potential_movements_est(bb)
  h3 = h_stability_no_unstables(bb)
  h4 = h_corners(bb)
  h5 = h_score(bb)
  values = h1, h2, h3, h4, h5
  coeffs = [exp(-(move_count-k)*(move_count-k)/400) for k in splits]
  return sum(c * sum(v * w for v, w in zip(values, w)) for c,w in zip(coeffs,weights))
  
def h_evaluate_custom(bb, myweights):
  move_count = bitcount(bb.me | bb.op)
  h1 = h_movements(bb)
  h2 = h_potential_movements_est(bb)
  h3 = h_stability_no_unstables(bb)
  h4 = h_corners(bb)
  h5 = h_score(bb)
  values = h1, h2, h3, h4, h5
  coeffs = [exp(-(move_count-k)*(move_count-k)/400) for k in splits]
  return sum(c * sum(v * w for v, w in zip(values, w)) for c,w in zip(coeffs,myweights))

def h_evaluate_custom_noscore(bb, myweights):
  move_count = bitcount(bb.me | bb.op)
  values = (h_movements(bb),
            h_potential_movements_est(bb),
            h_stability_no_unstables(bb),
            h_corners(bb))
  coeffs = [exp(-(move_count-k)*(move_count-k)/400) for k in splits]
  return sum(c * sum(v * w for v, w in zip(values, w)) for c,w in zip(coeffs,myweights))
  
  
