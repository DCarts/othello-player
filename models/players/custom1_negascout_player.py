class Custom1NegascoutPlayer:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 16

  ts_len = 0
  ts_mean = 0
  ts_max = 0

  t_table = dict()

  myweights = ((60.0, 35.0,  0.0,  5.0),
               ( 5.0, 10.0, 45.0, 40.0),
               (20.0,  0.0, 55.0, 25.0))

  name = "1"
  
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
    for at in self.dangerous[4:]:
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
    print "Custom", self.name, "negascout last:", last
    print "Custom", self.name, "negascout mean:", self.ts_mean
    print "Custom", self.name, "negascout max:", self.ts_max

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
      cost, move = self.negascout(1, depth, self.inf_neg, self.inf_pos, bb)
      if self.overtime:
        depth -= 1
        break
      self.last_cost, self.last_move = cost, move
      if abs(cost) > 9998: # endgame
        break
      self.last_time = timer() - before
    print "reached depth ", depth
    next_move = Move(*bbm_to_tuple(self.last_move))
    end = timer()
    self.update_time(end-start)
    return next_move

  
  def negascout(self, color, depth, alpha, beta, node):
    if ((self.target - timer()) < 0.1):
      self.overtime = True
      return 0, None # cabo o tempo
    
    from_t = self.t_table[node] if node in self.t_table else None
    if from_t != None and from_t[2] >= depth: # se tem salvo com depth maior, vamos usar :)
      return from_t[0], from_t[1]

    moves_raw = find_moves(node)
    
    if (not moves_raw): # se nao temos movimentos
      if find_moves(node.change_player_c()): # se o inimigo tem movimentos
        # Passa a vez
        otherTurn = self.negascout(-color, depth, -beta, -alpha, node.change_player_c())
        return (- otherTurn[0], None)
      else:
        # nao ha mais movimentos! folha! game over!
        score = h_score_final(node)
        self.t_table[node] = score, None, depth
        return score, None
    
    if (depth == 0):
      # horizonte da busca! folha! segue o jogo!
      score = h_evaluate_custom_noscore(node, self.myweights)
      self.t_table[node] = score, None, depth
      return score, None
    else:
      moves = bits_iter(moves_raw)
      if len(moves) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1

      # ordenando movimentos por custo avaliado pela busca de profundidade com profundidade 1/2 da que queremos (shallow)
      current_boards = [(node.fullplay_c(move), move) for move in moves]
      current_boards.sort(reverse = True, key = lambda x: -self.negascout(-color, depth // 2, -beta, -alpha, x[0])[0])
      
      last_best = current_boards[0][0]
      best = (self.inf_neg, moves[0])
      for current, move in current_boards:
        # negascout
        if current == last_best:
          score = -self.negascout(-color, depth-1, -beta, -alpha, current)[0], move
        else:
          # null window search
          score = -self.negascout(-color, depth-1, -alpha-1, -alpha, current)[0], move
          if (alpha < score[0]) and (score[0] < beta):
            # null window deu ruim, busca completa entao
            score = -self.negascout(-color, depth-1, -beta, -score[0], current)[0], move

        best = max(best, score, key=itemgetter(0))
        alpha = max(alpha, best[0])

        # corte alpha-beta
        if alpha >= beta: # corta! inutil continuar!
          break;

      if self.overtime: # acabou o tempo, cancela, valores possivelmente sujos
        return 0, None
      else:
        # salva o valor e movimento que calculamos e retorna
        self.t_table[node] = best[0], best[1], depth 
        return best
