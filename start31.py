from controllers.test_controller  import TestBoardController
from models.move                  import Move
from models.board                 import Board
import pstats
import cProfile

me = 0
ele = 0
for x in xrange(0,8):
	controller = TestBoardController(2,1)
	# controller.init_game()
	# def doit():
	#   p = pstats.Stats('pstats')
	#   p.sort_stats('cumulative').print_stats(30)
	#   p.sort_stats('time').print_stats(100)
	# cProfile.run('controller.init_game()', 'pstats')
	win = controller.init_game()
	if(win == 1):
		ele += 1
	elif(win == 2):
		me += 1
	print 'doit!'
print me, ele
