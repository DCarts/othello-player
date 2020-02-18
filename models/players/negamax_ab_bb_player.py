class Negamax_AB_BB_Player:
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 4

  ts_len = 0
  ts_mean = 0
  ts_max = 0
  
  def __init__(self, color):
    self.color = color
    self.fixImports()
    self.all_corners = (ONE << i64(63), # top left
                        ONE << i64(56), # top right
                        ONE << i64(7),  # lower left
                        ONE)            # lower right
    
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
    print("NegaMax Alpha-Beta with BitBoard last: ", last)
    print("NegaMax Alpha-Beta with BitBoard mean: ", self.ts_mean)
    print("NegaMax Alpha-Beta with BitBoard max: ", self.ts_max)

  def play(self, board):
    start = timer()
    bb = bb_from(board, self.color)
    bbmove = self.negamax(1, self.MAX_DEPTH, self.inf_neg, self.inf_pos, bb)[1]
    next_move = Move(*bbm_to_tuple(bbmove))
    end = timer()
    self.update_time(end-start)
    return next_move

  
  def negamax(self, color, depth, alpha, beta, node):
    moves = find_moves_iter(node)
    
    if (len(moves) == 0):
      if len(find_moves_iter(node.change_player_c())) != 0:
        # Passa a vez
        otherTurn = self.negamax(-color, depth, -beta, -alpha, node.change_player_c())
        return (- otherTurn[0], otherTurn[1])
      else:
        # folha! game over!
        return h_score_final(node), None
    
    if (depth == 0):
      # folha! segue o jogo!
      return h_evaluate(node), None
    else:
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
      return best
        
