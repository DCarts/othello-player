from controllers.board_controller import BoardController
from models.move                  import Move
from models.board                 import Board
import pstats
import cProfile

controller = BoardController()
# controller.init_game()
cProfile.run('controller.init_game()', 'pstats')
p = pstats.Stats('pstats')
def doit():
  p.sort_stats('cumulative').print_stats(30)
  p.sort_stats('time').print_stats(100)
print 'doit!'
