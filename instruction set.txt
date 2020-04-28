#_________________________instructions from server to arduino_________________________

inst = "update,0,1,2,5,6,10,14,18,19,22,23,24,"
'''
    chessboard location index:
        0, 1, 2, 3, 4,
        5, 6, 7, 8, 9,
        10,11,12,13,14,
        15,16,17,18,19,
        20,21,22,23,24.
    After 'update chessboard' instruction follows 12 integers, separated by ','. 
        Integer 0~5 is location index of red chessmen.
        Integer 6~11 is location index of blue chessmen.
    Location index == -1 means this chessman is dead. 
'''

inst = "abort,"
'''
    'abort' instruction means something unexpected happened or one player has won, and the server has ended running this game.
    Arduino should also stop the game immediately.
'''

inst = 'win,'
'''
    Receiving 'win,' arduino player has won the game.
    Arduino should end the game. To start another game, run the game file on your PC again. 
'''

inst = 'lose,'
'''
    Receiving 'lose,' means this arduino player has lost the game.
    Arduino should end the game. To start another game, run the game file on your PC again. 
'''
inst = 'wait,'
'''
    When an arduino has established TCP connection with the server, and the server is waiting for another aruidno to start the game, it will send 'wait' back to arduino.
        If there's already a player waiting, the server will directly send 'update chessboard' instruction to start the game. 
    Arduino should do something to show the player that the server has received this request, and is waiting for another player.
'''

inst = "move,3,"
'''
    After 'move' instruction follows 1 integer, indicating the index of chessman.
    "move,3" means red chessman 3 should select a location to move to.
'''

#_________________________instructions from arduino to server_________________________
inst = "move,3,7,"
'''
    After 'move' instruction follows 2 integer, indicating the index of chessman, 
        and the place it is moving to, respectively.
    "move,3,7" means red chessman 3 should move to location 7 in the chessboard.
'''

inst = 'abort,'
'''
    'abort' instruction means something unexpected happened, and the Arduino has ended running this game.
    Server should also stop the game immediately, and send abort instruction to the other arduino.
''' 


#deprecated instruction. Server will automatically reply once arduino links to it.
inst = 'start,'
'''
    Arduino use 'start' instruction to request starting a game.
    The server should send 'abort', 'wait', or 'update chessboard'(meaning the game begins) instruction in response.
'''