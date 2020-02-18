class NegamaxABPlayer:

  # Diferenca para o MinimaxABPlayer: usa o tamanho verdadeiro do valid_moves

  from operator import itemgetter
  from models.move import Move
  from timeit import default_timer as timer
  
  inf_pos = float("inf")
  inf_neg = -inf_pos

  MAX_DEPTH = 3
  all_corners = [(1,1),(1,8),(8,1),(8,8)]

  ts_len = 0
  ts_mean = 0
  ts_max = 0
  
  def __init__(self, color):
    self.color = color

  def update_time(self, last):
    self.ts_len += 1
    self.ts_mean = (self.ts_len-1)*self.ts_mean/self.ts_len + last/self.ts_len
    self.ts_max = max(self.ts_max, last)
    print("NegaMax Alpha-Beta last: ", last)
    print("NegaMax Alpha-Beta mean: ", self.ts_mean)
    print("NegaMax Alpha-Beta max: ", self.ts_max)

  def play(self, board):
    start = self.timer()
    self.corners = [x for x in self.all_corners if board.get_square_color(*x) == board.EMPTY]
    next_move = self.negamax(1, self.MAX_DEPTH, self.inf_neg, self.inf_pos, (board,self.color))[1]
    end = self.timer()
    # self.update_time(end-start)
    return next_move
  
  def h_movimentos(self, board):
    return len(set(board.valid_moves(self.color))) \
           - len(set(board.valid_moves(board._opponent(self.color))))

  def h_movimentos_precomputed(self, board, color, movecount):
    if color == self.color:
      return movecount - len(set(board.valid_moves(board._opponent(self.color))))
    else:
      return len(set(board.valid_moves(self.color))) - movecount

  def h_score(self, board):
    score = board.score()
    if self.color == board.WHITE:
      return self.inf_pos if score[0] > score[1] else self.inf_neg
    else:
      return self.inf_pos if score[1] > score[0] else self.inf_neg

  def negamax(self, color, depth, alpha, beta, node):
    board = node[0]
    player = node[1]
    moves = board.valid_moves(player)
    
    if (len(set(moves)) == 0):
      if len(set(board.valid_moves(board._opponent(player)))) != 0:
        # Passa a vez
        otherTurn = self.negamax(-color, depth, -beta, -alpha, (board,board._opponent(player)))
        return (- otherTurn[0], otherTurn[1])
      else:
        # folha! game over!
        return color * self.h_score(board), None
    
    if (depth == 0):
      # folha! segue o jogo!
      return color * self.h_movimentos_precomputed(board, player, len(moves)), None
    else:
      if len(set(moves)) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1
      best = (self.inf_neg, moves[0])
      for move in moves:
        current = board.get_clone()
        current.play(move, player)
        extra_depth = 0
        best = max(best, (
          -self.negamax(-color, depth-1, -beta, -alpha, (current,board._opponent(player)))[0],
          move), key=self.itemgetter(0))
        alpha = max(alpha, best[0])
        if alpha >= beta: # corta! inutil continuar!
          break;
      return best
