from .controllers.test_controller_hill  import TestBoardControllerHill
from .models.move                  import Move
from .models.board                 import Board
import pstats
import cProfile
from random import seed
from random import randint
import copy
mismaLinea = 0
q1 = 1
pesoAntes = [[57.0, 32.0, 9.0, 2.0], [-4.0, 1.0, 60.0, 43.0], [17.0, -3.0, 64.0, 22.0]]
pesoDepois = [[57.0, 32.0, 9.0, 2.0], [-7.0, -2.0, 57.0, 52.0], [17.0, -3.0, 64.0, 22.0]]
peso1 = [0, 0]
peso2 = [0, 0]
ganhadas1 = [4, 1]
ganhadas2 = [2, 3]
mexer = 1

for x in range(0,0):
        controller = TestBoardControllerHill(4,0,pesoAntes)        
        win = controller.init_game()
        score = controller._score()        
        peso1[0] += score[0]
        peso1[1] += score[1]
        if(win == 1):
                ganhadas1[0] += 1
        elif(win == 2):
                ganhadas1[1] += 1
print("Inicio", "/", end=' ')
print(pesoAntes, end=' ')
print(ganhadas1,"/", end=' ')
print(peso1)
tent = 0
while(1):
        if(4 > ganhadas2[0]):
                mismaLinea += 1
                pesoDepois[q1] = copy.copy(pesoAntes[q1])
                mexer = randint(0, 3)
                print(mexer)
        else:
                mismaLinea = 0
                pesoAntes[q1] = copy.copy(pesoDepois[q1])
                ganhadas1 = copy.copy(ganhadas2)
                print("nao mexer")
        if(mismaLinea == 3):
                mismaLinea = 0
                q1 += 1
                q1 = q1%3
        for x in range(0,4):
                if(x == mexer):
                        pesoDepois[q1][x] += 9.0
                else:
                        pesoDepois[q1][x] -= 3.0
        peso2 = [0,0]
        ganhadas2 = [0,0]
        print("tentativa", tent, "/", end=' ')
        print(pesoDepois)
        for x in range(0,5):
                controller = TestBoardControllerHill(4,0,pesoDepois)        
                win = controller.init_game()
                score = controller._score()
                peso2[0] += score[0]
                peso2[1] += score[1]
                if(win == 1):
                        ganhadas2[0] += 1
                elif(win == 2):
                        ganhadas2[1] += 1
        print("Resultado", tent, "/", end=' ')
        print(ganhadas2,"/", end=' ')
        print(peso2)
        tent += 1
                        
        
                
                
                
        

