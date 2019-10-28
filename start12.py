from controllers.test_controller  import TestBoardController
from models.move                  import Move
from models.board                 import Board
import pstats
import cProfile

controller = TestBoardController(1,2)
# controller.init_game()
def doit():
  p = pstats.Stats('pstats')
  p.sort_stats('cumulative').print_stats(30)
  p.sort_stats('time').print_stats(100)
cProfile.run('controller.init_game()', 'pstats')
print 'doit!'
