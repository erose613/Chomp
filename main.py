import numpy as np
import threading
from typing import List, Set, Tuple
import ipywidgets as widgets
from IPython.display import display

m,n = 4,7
init = frozenset((x,y) for x in range(m) for y in range(n))

board = init

def memoize(f):
    cache = dict()
    def memof(x):
        try: return cache[x]
        except:
            cache[x] = f(x)
            return cache[x]
    return memof

def moves(board):
    return [frozenset([(x,y) for (x,y) in board if x < px or y < py]) for (px,py) in board]

@memoize
def wins(board):
    if not board: return True
    return any(not wins(move) for move in moves(board))

def make_move(i: int, j: int, board: frozenset):
  new_board = set()
  for ii,jj in board:
    if ii < i or jj < j: new_board.add((ii,jj))
  return frozenset(new_board)

def check_move(i: int, j: int):
  if (i, j) == (0, 0): return False
  new_board = make_move(i, j, board)
  res = True
  for ii, jj in new_board:
    new_new_board = make_move(ii, jj, new_board)
    res = res and wins(new_new_board)
  return res

def list_good_moves():
  res = []
  for i, j in board:
    if check_move(i, j): res.append((i,j))
  return res

def on_button_click(btn):
  global board, clicks, barrier, lock
  btn.disabled = True
  btn.style.button_color = 'white'
  clicked_index = buttons.index(btn)
  row, col = divmod(clicked_index, n)
  board = make_move(m - row - 1, col, board)
  # Disable buttons above and to the right
  for i in range(row+1):
      for j in range(col, n):
          index = i * n + j
          if index < len(buttons):
              buttons[index].disabled = True
              buttons[index].style.button_color = 'white'
  barrier.wait()


def run_game():
  global board, clicks
  while board:
    good_moves = list_good_moves()
    try:
        i, j = good_moves[0]
        index = (m - i - 1) * n + j
        click_thread = threading.Thread(target=on_button_click, args=(buttons[index],))
        click_thread.start()
    except IndexError:
        raise Exception("No Good Moves Left")
    barrier.wait()
if __name__ == "__main__":
  lock = threading.Lock()
  barrier = threading.Barrier(3)
  buttons = []
  
  for row in range(m):
      for col in range(n):
        button = widgets.Button(
          description = "",
          layout=widgets.Layout(width='45px', height='30px'),  # Adjust the size
          style=widgets.ButtonStyle(button_color='chocolate', font_weight='bold', font_size='8px'))
        button.on_click(lambda event, btn=button: on_button_click(btn))
        buttons.append(button)
  
  grid = widgets.GridBox(buttons, layout=widgets.Layout(grid_template_columns=f"repeat({n}, 46px)"))
  display(grid)
  
  game_thread = threading.Thread(target=run_game)
  game_thread.start()
