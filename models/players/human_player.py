from models.move import Move
class HumanPlayer:
  def __init__(self, color):
    self.color = color


  def play(self, board):
    rowInp = int(input("Linha: "))
    colInp = int(input("Coluna: "))
    move = Move(rowInp, colInp)
    while move not in board.valid_moves(self.color):
      print("Movimento invalido.Insira um valido")
      print(board)
      rowInp = int(input("Linha: "))
      colInp = int(input("Coluna: "))
      move = Move(rowInp, colInp)
    return move
