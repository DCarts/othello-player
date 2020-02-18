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
pesoAntes = [[75.0, 26.0, -9.0, 8.0], [-7.0, 22.0, 45.0, 40.0], [20.0, 0.0, 55.0, 25.0]]
pesoDepois = [[75.0, 26.0, -9.0, 8.0], [-10.0, 19.0, 54.0, 37.0], [20.0, 0.0, 55.0, 25.0]]
peso1 = [0, 0]
peso2 = [0, 0]
ganhadas1 = [1, 4]
ganhadas2 = [3, 2]
mexer = 2

for x in range(0,0):
        controller = TestBoardControllerHill(0,4,pesoAntes)        
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
        if(4 > ganhadas2[1]):
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
                controller = TestBoardControllerHill(0,4,pesoDepois)        
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
                        
        
                
                
                
        

