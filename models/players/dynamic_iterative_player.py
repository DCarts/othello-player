class Dynamic_Iterative_Player:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 16

  ts_len = 0
  ts_mean = 0
  ts_max = 0
  
  def __init__(self, color):
    self.color = color
    self.fixImports()
    self.dangerous = (ONE << i64(63), # top left
                      ONE << i64(56), # top right
                      ONE << i64(7),  # lower left
                      ONE,            # lower right
                      ONE << i64(54),
                      ONE << i64(49),
                      ONE << i64(14),
                      ONE << i64(9))     
    
  def fixImports(self):
    bb_globals = {}
    h_globals = {}
    exec(compile(open('./models/players/bitboard.py', "rb").read(), './models/players/bitboard.py', 'exec'), bb_globals)
    exec(compile(open('./models/players/heuristics.py', "rb").read(), './models/players/heuristics.py', 'exec'), h_globals)
    globals().update(bb_globals)
    globals().update(h_globals)
    global itemgetter
    global timer
    global i64
    global Move
    from models.move import Move
    from numpy import uint64 as i64
    from operator import itemgetter
    from timeit import default_timer as timer

  def update_time(self, last):
    self.ts_len += 1
    self.ts_mean = (self.ts_len-1)*self.ts_mean/self.ts_len + last/self.ts_len
    self.ts_max = max(self.ts_max, last)
    print("Dynamic Iterative last: ", last)
    print("Dynamic Iterative mean: ", self.ts_mean)
    print("Dynamic Iterative max: ", self.ts_max)

  def play(self, board):
    start = timer()
    self.target = start+3
    self.overtime = False
    
    bb = bb_from(board, self.color)
    bbmove = None
    
    self.last_time = 0
    self.last_cost, self.last_move = None, None
    depth = 0
    while (depth < self.MAX_DEPTH):
      depth += 1
      before = timer()
      cost, move = self.negamax(1, depth, self.inf_neg, self.inf_pos, bb)
      if self.overtime:
        depth -= 1
        break
      self.last_cost, self.last_move = cost, move
      self.last_time = timer() - before
      if abs(cost) > 9999: # endgame
        if cost > 0:
          print('ganhei')
        elif cost < 0:
          print('perdi')
        else:
          print('empatei')
        break 
    print("reached depth ", depth)
    next_move = Move(*bbm_to_tuple(self.last_move))
    end = timer()
    self.update_time(end-start)
    return next_move

  
  def negamax(self, color, depth, alpha, beta, node):
    if ((self.target - timer()) < 0.1):
      self.overtime = True
      return 0, None # cabo o tempo
    
    moves_raw = find_moves(node)
    
    if (not moves_raw):
      if find_moves(node.change_player_c()):
        # Passa a vez
        otherTurn = self.negamax(-color, depth, -beta, -alpha, node.change_player_c())
        return (- otherTurn[0], otherTurn[1])
      else:
        # folha! game over!
        return h_score_final(node), None
    
    if (depth == 0):
      # folha! segue o jogo!
      return h_evaluate_dynamic(node), None
    else:
      moves = bits_iter(moves_raw)
      if len(moves) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1
      best = (self.inf_neg, moves[0])
      for move in moves:
        current = node.fullplay_c(move)
        
        best = max(best, (
          -self.negamax(-color, depth-1, -beta, -alpha, current)[0],
          move), key=itemgetter(0))
        
        alpha = max(alpha, best[0])
        if alpha >= beta: # corta! inutil continuar!
          break;
        
      return (0, None) if self.overtime else best
        
