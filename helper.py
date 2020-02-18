# -*- coding: cp1252 -*-
from .models.players.bitboard import *
from .views.console_board_view import ConsoleBoardView
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
        print(mymasks_dirs[at])
      elif ((at | mask_t_up) == mask_t_up):
        mymasks[at] = i64(0xFF00000000000000)
        mymasks_dirs[at] = ((mask_h << (i << THREE)) & ~(at-ONE), (mask_h << (i << THREE)) & (at-ONE)),
        print(mymasks_dirs[at])
      elif ((at | mask_t_left) == mask_t_left):
        mymasks[at] = i64(0x8080808080808080)
        mymasks_dirs[at] = ((mask_v << j) & ~(at-ONE), (mask_v << j) & (at-ONE)),
        print(mymasks_dirs[at])
      elif ((at | mask_t_right) == mask_t_right):
        mymasks[at] = i64(0x0101010101010101)
        mymasks_dirs[at] = ((mask_v << j) & ~(at-ONE), (mask_v << j) & (at-ONE)),
        print(mymasks_dirs[at])
      elif ((at | mask_t_down) == mask_t_down):
        mymasks[at] = i64(0x00000000000000FF)
        mymasks_dirs[at] = ((mask_h << (i << THREE)) & ~(at-ONE), (mask_h << (i << THREE)) & (at-ONE)),
        print(mymasks_dirs[at])
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
        print(mymasks_dirs[at])
        mymasks[at] = mask_ij

  return mymasks, mymasks_dirs

masks, masks_dirs = precalc_mask_stability()

bb_test = BitBoard(0xD0A1E269930337D3,0x204000846870C820)
print_mask(bb_test.me)
print('') 
print_mask(bb_test.op)
print('')











def fake_norm(x, y):
  return 0 if (x + y) == 0 else 100*(x-y)/(x+y)

def h_stability(bb):
  """ estabilidade de cada jogador
  (isto e, nr. de pecas de cada jogador
  que nao pode mais ser revertida )"""
  
  me_moves_raw = find_moves(bb)
  op_moves_raw = find_moves(bb.change_player_c())
  
  me_unstables_raw = i64(0)
  op_unstables_raw = i64(0)

  moves_iter = bits_iter(me_moves_raw | op_moves_raw)
  #unstables
  at = i64(1)
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

  me_stables = 0
  op_stables = 0

  occupied = bb.me | bb.op
  all_unstables_raw = me_unstables_raw|op_unstables_raw

  possible_stables_iter = bits_iter(occupied & ~all_unstables_raw)
  for at in possible_stables_iter:
    if (masks[at] | occupied) == occupied:
      if at & bb.me:
        me_stables += 1
      else:
        op_stables += 1
  
  return fake_norm(me_stables+op_unstables, op_stables+me_unstables)
