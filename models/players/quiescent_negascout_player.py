class QuiescentNegascoutPlayer:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 16

  ts_len = 0
  ts_mean = 0
  ts_max = 0

  t_table = dict()

  myweights = ((60.0, 30.0,  0.0,  10.0, 0.0),
               (25.0, 15.0, 30.0, 30.0, 0.0),
               (15.0,  0.0, 50.0, 20.0, 15.0))
  
  def __init__(self, color):
    self.color = color
    self.fixImports()
    self.dangerous_raw = i64(0)
    self.dangerous = (ONE << i64(63), # top left
                      ONE << i64(56), # top right
                      ONE << i64(7),  # lower left
                      ONE,            # lower right
                      ONE << i64(54),
                      ONE << i64(49),
                      ONE << i64(14),
                      ONE << i64(9))
    for at in self.dangerous[:4]:
      self.dangerous_raw |= at
    
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
    print "Quiescent negascout last: ", last
    print "Quiescent negascout mean: ", self.ts_mean
    print "Quiescent negascout max: ", self.ts_max

  def play(self, board):
    start = timer()
    self.target = start+3
    self.overtime = False
    
    bb = bb_from(board, self.color)
    bbmove = None
    
    self.last_time = 0
    self.last_cost, self.last_move = None, None
    depth = 0
    while ((self.target - timer()) > 0.1 and depth < self.MAX_DEPTH):
      depth += 1
      before = timer()
      cost, move = self.negascout(1, depth, self.inf_neg, self.inf_pos, 2, bb)
      if self.overtime:
        depth -= 1
        break
      self.last_cost, self.last_move = cost, move
      if abs(cost) > 9999: # endgame
        break
      self.last_time = timer() - before
    print "reached depth ", depth
    next_move = Move(*bbm_to_tuple(self.last_move))
    end = timer()
    self.update_time(end-start)
    return next_move

  
  def negascout(self, color, depth, alpha, beta, credit, node):
    if ((self.target - timer()) < 0.1):
      self.overtime = True
      return 0, None # cabo o tempo
    
    from_t = self.t_table[node] if node in self.t_table else None
    if from_t != None and from_t[2] >= depth: # vamos usar esse valor :)
      return from_t[0], from_t[1]

    moves_raw = find_moves(node)
    
    if (not moves_raw):
      if find_moves(node.change_player_c()):
        # Passa a vez
        otherTurn = self.negascout(-color, depth, -beta, -alpha, credit,  node.change_player_c())
        return (- otherTurn[0], None)
      else:
        # folha! game over!
        score = h_score_final(node)
        self.t_table[node] = score, None, depth
        return score, None
    
    if moves_raw & self.dangerous_raw and depth == 0 and credit:
      credit -= 1
      depth = 1
    if (depth == 0):
      # folha! segue o jogo!
      score = h_evaluate_dynamic(node)
      self.t_table[node] = score, None, depth
      return h_evaluate_custom(node, self.myweights), None
    else:
      moves = bits_iter(moves_raw)
      if len(moves) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1

      current_boards = [(node.fullplay_c(move), move) for move in moves]
      current_boards.sort(reverse = True, key = lambda x: -self.negascout(-color, depth // 2, -beta, -alpha, credit, x[0])[0])
      
      last_best = current_boards[0][0]
      best = (self.inf_neg, moves[0])
      for current, move in current_boards:
        if current == last_best:
          score = -self.negascout(-color, depth-1, -beta, -alpha, credit,  current)[0], move
        else:
          score = -self.negascout(-color, depth-1, -alpha-1, -alpha, credit,  current)[0], move
          if (alpha < score[0]) and (score[0] < beta):
            score = -self.negascout(-color, depth-1, -beta, -score[0], credit,  current)[0], move

        best = max(best, score, key=itemgetter(0))
        alpha = max(alpha, best[0])
        if alpha >= beta: # corta! inutil continuar!
          break;

      if self.overtime:
        return 0, None
      else:
        self.t_table[node] = best[0], best[1], depth 
        return best
        
