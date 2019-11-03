import requests	

class ChinoPlayer:
  def __init__(self, color,p1,p2,p3):
    self.color = color

  def play(self, board):
    return self.getNearestCorner(board.valid_moves(self.color),board)

  def getNearestCorner(self, moves, board):
    movchino = self.fazerRequest(board)
    for move in moves:
    	# print move.x,move.y
    	if(move.x == (movchino // 9) and move.y == (movchino % 9)):
    		# print "chino", move
    		return move


  def fazerRequest(self,board):
    url = self.stringBoard(board,self.color)
    r = requests.get(url)
    mov = int(r.text)
    # print url
    # print mov
    return mov

  def stringBoard(self,board,color):
    url = "http://www.amy.hi-ho.ne.jp/cgi-bin/user/okuhara/breversi.pl?m=0&p="
    for i in range(1, 9):
      for j in range(1, 9):
        if (board.get_square_color(i,j) == '@'):
          url = url + "1"
        elif (board.get_square_color(i,j) == 'o'):
          url = url + "2"
        else:
          url = url + "0"

    if(color == '@'):
      url = url + "+1"
    else:
      url = url + "+2"
    return url
