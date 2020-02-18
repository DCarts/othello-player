class MinimaxABPlayer:

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
    print("MiniMax Alpha-Beta last: ", last)
    print("MiniMax Alpha-Beta mean: ", self.ts_mean)
    print("MiniMax Alpha-Beta max: ", self.ts_max)

  def play(self, board):
    start = self.timer()
    self.corners = [x for x in self.all_corners if board.get_square_color(*x) == board.EMPTY]
    next_move = self.minimax(True, self.MAX_DEPTH, self.inf_neg, self.inf_pos, (board,self.color))[1]
    end = self.timer()
    # self.update_time(end - start)
    return next_move
      
  def h_movimentos(self, board):
    return len(board.valid_moves(self.color)) - len(board.valid_moves(board._opponent(self.color)))

  def h_movimentos_precomputed(self, board, color, movecount):
    if color == self.color:
      return movecount - len(board.valid_moves(board._opponent(self.color)))
    else:
      return len(board.valid_moves(self.color)) - movecount


  def h_score(self, board):
    score = board.score()
    if self.color == board.WHITE:
      return self.inf_pos if score[0] > score[1] else self.inf_neg
    else:
      return self.inf_pos if score[1] > score[0] else self.inf_neg

  def minimax(self, isMaxNode, depth, alpha, beta, node):
    board = node[0]
    player = node[1]
    moves = board.valid_moves(player)

    if (len(moves) == 0):
      if len(board.valid_moves(board._opponent(player))) != 0:
        # Passa a vez ( e de bonus desce 1 nivel a mais )
        return self.minimax(not isMaxNode, depth, alpha, beta, (board,board._opponent(player)))
      else:
        # folha! game over!
        return self.h_score(board), None
    elif (depth == 0):
      # folha! segue o jogo!
      return self.h_movimentos_precomputed(board, player, len(moves)), None
    
    else:
      if len(moves) == 1:
        # movimento forcado
        # aumenta 1 profundidade pro (unico) node filho
        depth += 1
      best = None
      if isMaxNode:
        best = (self.inf_neg, moves[0])
        for move in moves:
          current = board.get_clone()
          current.play(move, player)
          best = max(best, (self.minimax(not isMaxNode, depth-1, alpha, beta, (current,board._opponent(player)))[0], move), key=self.itemgetter(0))
          alpha = max(alpha, best[0])
          if best[0] >= beta: # corta! inutil pra mim!
            break
      else:
        best = (self.inf_pos, moves[0])
        for move in moves:
          current = board.get_clone()
          current.play(move, player)
          best = min(best, (self.minimax(not isMaxNode, depth-1, alpha, beta, (current,board._opponent(player)))[0], move), key=self.itemgetter(0))
          beta = min(beta, best[0])
          if best[0] <= alpha: # corta! inutil pra mim!
            break
      return best
        
