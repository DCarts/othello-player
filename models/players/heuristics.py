# -*- coding: cp1252 -*-
from models.players.bitboard import *
from views.console_board_view import ConsoleBoardView
from math import exp
from numpy import uint64 as i64
from timeit import default_timer as timer
import csv

inf_pos = float("inf")
inf_neg = -inf_pos

mask_h = i64(0xFF00000000000000) # horizontal
mask_v = i64(0x8080808080808080) # vertical
mask_d1 = i64(0x8040201008040201) # diagonal up-left -> down-right
mask_d2 = i64(0x0102040810204080) # diagonal up-right -> down-left

ONE = i64(1)
THREE = i64(3)

def precalc_mask_stability():
  ONE = i64(1)
  THREE = i64(3)
  masks = dict()

  for ni in range(8):
    for nj in range(8):
      i = i64(ni)
      j = i64(nj)
      at = (ONE << j) << (i << THREE)
      mask_ij = (mask_h >> i) | (mask_v >> (j << THREE))
      if (i > j):
        mask_ij |= (mask_d1 << ((i - j) << THREE))
      else:
        mask_ij |= (mask_d1 >> ((j - i) << THREE))
      d = i64(7) - i
      if (d > j):
        mask_ij |= (mask_d2 << ((d - j) << THREE))
      else:
        mask_ij |= (mask_d2 >> ((j - d) << THREE))
      
      masks[at] = mask_ij

  return masks

masks = precalc_mask_stability()

def fake_norm(x, y):
  return 0 if (x + y) == 0 else 100*(x-y)/(x+y)

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

  return fake_norm(op_frontier, me_frontier)

def h_potential_movements_est_2(bb):
  """ numero de movimentos potencial estimado
  (isto e, nr. de pecas inimigas vizinhas a casas vazias )"""
  me_frontier, op_frontier = empty_nbors(bb)
  return fake_norm(op_frontier, me_frontier)


def h_stability_3(bb): # fastest?
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida )"""
  occupied = bb.me | bb.op
  me_stables = 0
  op_stables = 0
  
  #stables
  at = i64(1)
  for k in range(64):
    if at & occupied:
      if (masks[at] & occupied) == occupied:
        if at & bb.me:
          me_stables += 1
        else:
          op_stables += 1
    at <<= ONE
  return fake_norm(me_stables, op_stables)


def h_stability(bb):
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida )"""
  occupied = bb.me | bb.op
  
  me_stables = 0
  op_stables = 0
  
  me_moves_raw = find_moves(bb)
  op_moves_raw = find_moves(bb.change_player_c())
  all_moves = me_moves_raw | op_moves_raw
  
  me_unstables_raw = i64(0)
  op_unstables_raw = i64(0)
  
  #stables
  at = i64(1)
  for k in range(64):
    if at & occupied:
      if (masks[at] & occupied) == occupied:
        if at & bb.me:
          me_stables += 1
        else:
          op_stables += 1
    #unstables
    elif at & all_moves:
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
    at <<= ONE

  me_unstables = bitcount(me_unstables_raw)
  op_unstables = bitcount(op_unstables_raw)
  return fake_norm(me_stables-me_unstables, op_stables-op_unstables)


def h_stability_old(bb): # 20% mais lerda
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida )"""
  occupied = bb.me | bb.op
  
  me_stables = 0
  op_stables = 0
  
  me_moves = find_moves_iter(bb)
  op_moves = find_moves_iter(bb.change_player_c())
  
  me_unstables_raw = i64(0)
  op_unstables_raw = i64(0)
  
  #stables
  at = i64(1)
  for ni in range(8):
    for nj in range(8):
      i = i64(ni)
      j = i64(nj)
      at = (ONE << j) << (i << THREE)
      if at & occupied:
        mask_ij = masks[at]
        if (mask_ij & occupied) == occupied:
          if at & bb.me:
            me_stables += 1
          else:
            op_stables += 1
  #unstables
  for next_dir in next_move_directions:
    for move in op_moves:
      walk = next_dir(move)
      line = i64(0)
      while (walk & bb.me):
        line |= walk
        walk = next_dir(walk)
      if (walk & bb.op):
        me_unstables_raw |= line
    for move in me_moves:
      walk = next_dir(move)
      line = i64(0)
      while (walk & bb.op):
        line |= walk
        walk = next_dir(walk)
      if (walk & bb.me):
        op_unstables_raw |= line

  me_unstables = bitcount(me_unstables_raw)
  op_unstables = bitcount(op_unstables_raw)
  return fake_norm(me_stables-me_unstables, op_stables-op_unstables)

def h_score(bb):
  """ nr. de pontos que cada jogador tem """
  return fake_norm(bitcount(bb.me), bitcount(bb.op))


corners = (ONE << i64(63), # top left
           ONE << i64(56), # top right
           ONE << i64(7),  # lower left
           ONE)            # lower right

def h_corners(bb):
  """ nr. de cantos que cada jogador tem """
  me_corners = 0
  op_corners = 0
  for corner in corners:
    if bb.me & corner:
      me_corners += 1
    elif bb.op & corner:
      op_corners += 1
      
  return fake_norm(me_corners, op_corners)

def h_score_final(bb):
  """ se empatou = 0
      se venci = infinito
      se perdi = val. normal"""
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
  return 5*h1 + 10*h2 + 30*h3 + 20*h4 + 20*h5

##weights = ((35, 20, 35, 10, 0),
##           (23,8,39,30,0),
##           (5,0,30,15,45))

weights = ((90, 10, 0, 0, 0),
           (45,5,20,30,0),
           (10,0,30,20,40))

##weights = ((100,0,0,0,0),
##           (100,0,0,0,0),
##           (100,0,0,0,0))

splits = (4,34,64)

def h_evaluate_dynamic(bb):
  move_count = bitcount(bb.me | bb.op)
  h1 = h_movements(bb)
  h2 = h_potential_movements_est(bb)
  h3 = h_stability(bb)
  h4 = h_corners(bb)
  h5 = h_score(bb)
  values = h1, h2, h3, h4, h5
  coeffs = [exp((move_count-k)*(move_count-k)/400) for k in splits]
  val = sum(c * sum(v * w for v, w in zip(values, w)) for c,w in zip(coeffs,weights))
  
  return val
  
  
