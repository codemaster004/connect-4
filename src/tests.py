
game_won = False
player = True
print(1 if game_won and player else -1 if game_won and not player else 0)

game_won = False
player = False
print(1 if game_won and player else -1 if game_won and not player else 0)

game_won = True
player = True
print(1 if game_won and player else -1 if game_won and not player else 0)

game_won = True
player = False
print(1 if game_won and player else -1 if game_won and not player else 0)
