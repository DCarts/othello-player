from controllers.test_controller  import TestBoardController
from models.move                  import Move
from models.board                 import Board
import pstats
import cProfile

branco = 0
bj = ""
preto = 0
nj = ""
peso = [0,0]
for x in xrange(0,16):
        controller = TestBoardController(2,3)        
	# controller.init_game()
	# def doit():
	#   p = pstats.Stats('pstats')
	#   p.sort_stats('cumulative').print_stats(30)
	#   p.sort_stats('time').print_stats(100)
	# cProfile.run('controller.init_game()', 'pstats')
        win = controller.init_game()
        bj = controller.white_player
        nj = controller.black_player
        score = controller._score()
        peso[0] += score[0]
        peso[1] += score[1]
        #Ganha branca
        if(win == 1):
                branco += 1
        #Ganha Negra
        elif(win == 2):
                preto += 1
        print 'doit!'
        print peso        
print bj, nj
print branco, preto
