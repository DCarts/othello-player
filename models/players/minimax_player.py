class MinimaxPlayer:

  from operator import itemgetter

  inf_pos = float("inf")
  inf_neg = -inf_pos
  
  MAX_DEPTH = 2
  
  def __init__(self, color):
    self.color = color

  def play(self, board):
    return self.minimax(True, self.MAX_DEPTH, (board,self.color))[1]
      
  def h_movimentos(self, board):
    return len(board.valid_moves(self.color)) - len(board.valid_moves(board._opponent(self.color)))

  def h_score(self, board):
    score = board.score()
    if self.color is board.WHITE:
      return self.inf_pos if score[0] > score[1] else self.inf_neg
    else:
      return self.inf_pos if score[1] > score[0] else self.inf_neg

  def minimax(self, isMaxNode, depth, node):
    board = node[0]
    player = node[1]
    moves = board.valid_moves(player)
    
    if (depth is 0) or (len(moves) is 0):
      if len(moves) != 0:
        return self.h_movimentos(board), None
      if len(board.valid_moves(board._opponent(player))) != 0:
        return self.h_movimentos(board), None
      return self.h_score(board), None
    
    else:
      best = None
      if isMaxNode:
        best = (self.inf_neg, moves[0])
        for move in moves:
          current = board.get_clone()
          current.play(move, player)
          best = max(best, (self.minimax(not isMaxNode, depth-1, (current,board._opponent(player)))[0], move), key=self.itemgetter(0))
      else:
        best = (self.inf_pos, moves[0])
        for move in moves:
          current = board.get_clone()
          current.play(move, player)
          best = min(best, (self.minimax(not isMaxNode, depth-1, (current,board._opponent(player)))[0], move), key=self.itemgetter(0))
      
      
      return best
        
