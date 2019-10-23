class Iterative_Negascout_Player:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 16

  ts_len = 0
  ts_mean = 0
  ts_max = 0

  t_table = dict()
  
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
    print "Iterative negascout last: ", last
    print "Iterative negascout mean: ", self.ts_mean
    print "Iterative negascout max: ", self.ts_max

  def play(self, board):
    start = timer()
    self.target = start+3
    
    bb = bb_from(board, self.color)
    bbmove = None
    
    self.last_time = 0
    self.last_cost, self.last_move = None, None
    depth = 0
    while ((self.target - timer()) > 0.1 and depth < self.MAX_DEPTH):
      depth += 1
      before = timer()
      self.last_cost, self.last_move = self.negascout(1, depth, self.inf_neg, self.inf_pos, bb)
      self.last_time = timer() - before
    print "reached depth ", depth
    next_move = Move(*bbm_to_tuple(self.last_move))
    end = timer()
    self.update_time(end-start)
    return next_move

  def negascout(self, color, depth, alpha, beta, node):
    if ((self.target - timer()) < 0.1):
      return self.last_cost, self.last_move # cabo o tempo
    
    from_t = self.t_table[node] if node in self.t_table else None
    if from_t != None and from_t[2] >= depth: # vamos usar esse valor :)
      return from_t[0], from_t[1]
    
    moves = find_moves_iter(node)
    
    if (len(moves) == 0):
      if len(find_moves_iter(node.change_player_c())) != 0:
        # Passa a vez
        otherTurn = self.negascout(-color, depth, -beta, -alpha, node.change_player_c())
        return (- otherTurn[0], otherTurn[1])
      else:
        # folha! game over!
        score = h_score_final(node)
        self.t_table[node] = score, None, depth
        return score, None
    
    if (depth == 0):
      # folha! segue o jogo!
      score = h_evaluate_dynamic(node)
      self.t_table[node] = score, None, depth
      return h_evaluate_dynamic(node), None
    else:
      if len(moves) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1

      current_boards = [(node.fullplay_c(move), move) for move in moves]
      current_boards.sort(reverse = True, key = lambda x: (self.t_table[x[0]][0] if x[0] in self.t_table else 0))
      
      last_best = current_boards[0][0]
      best = (self.inf_neg, moves[0])
      for current, move in current_boards:
        #extra_depth = 0
        #if any(move == x for x in self.dangerous):
          # movimento perigoso
          # aumenta 2 profundidade pra esse node filho
          #extra_depth = 2

        if current == last_best:
          score = -self.negascout(-color, depth-1, -beta, -alpha, current)[0], move
        else:
          score = -self.negascout(-color, depth-1, -alpha-1, -alpha, current)[0], move
          if (alpha < score[0]) and (score[0] < beta):
            score = -self.negascout(-color, depth-1, -beta, -score[0], current)[0], move

        best = max(best, score, key=itemgetter(0))
        alpha = max(alpha, best[0])
        if alpha >= beta: # corta! inutil continuar!
          break;
      self.t_table[node] = best[0], best[1], depth
      return best
        
