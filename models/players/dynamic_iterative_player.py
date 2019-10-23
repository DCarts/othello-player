class Dynamic_Iterative_Player:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 12

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
    execfile('./models/players/bitboard.py', bb_globals)
    execfile('./models/players/heuristics.py', h_globals)
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
    print "Dynamic Iterative last: ", last
    print "Dynamic Iterative mean: ", self.ts_mean
    print "Dynamic Iterative max: ", self.ts_max

  def play(self, board):
    start = timer()
    self.target = start+3
    
    bb = bb_from(board, self.color)
    bbmove = None
    
    self.last_time = 0
    self.last_cost, self.last_move = None, None
    depth = 0
    while ((self.target - timer()) > 4*self.last_time and depth < self.MAX_DEPTH):
      depth += 1
      before = timer()
      self.last_cost, self.last_move = self.negamax(1, depth, self.inf_neg, self.inf_pos, bb)
      self.last_time = timer() - before
    print "reached depth ", depth
    next_move = Move(*bbm_to_tuple(self.last_move))
    end = timer()
    self.update_time(end-start)
    return next_move

  
  def negamax(self, color, depth, alpha, beta, node):
    moves = find_moves_iter(node)
    
    if (len(moves) is 0):
      if len(find_moves_iter(node.change_player_c())) != 0:
        # Passa a vez
        otherTurn = self.negamax(-color, depth, -beta, -alpha, node.change_player_c())
        return (- otherTurn[0], otherTurn[1])
      else:
        # folha! game over!
        return h_score_final(node), None
    
    if (depth is 0):
      # folha! segue o jogo!
      return h_evaluate_dynamic(node), None
    else:
      if len(moves) is 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1
      best = (self.inf_neg, moves[0])
      for move in moves:
        current = node.fullplay_c(move)
        extra_depth = 0
        if any(move is x for x in self.dangerous):
          # movimento perigoso
          # aumenta 2 profundidade pra esse node filho
          extra_depth = 2
        best = max(best, (
          -self.negamax(-color, depth-1 + extra_depth, -beta, -alpha, current)[0],
          move), key=itemgetter(0))
        alpha = max(alpha, best[0])
        if ((self.target - timer()) < self.last_time):
          return self.last_cost, self.last_move # cabo o tempo
        if alpha >= beta: # corta! inutil continuar!
          break;
      return best
        
