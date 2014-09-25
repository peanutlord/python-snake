import curses
import random
from pygame import time
import argparse
import sys

class Snake():
    
    stdscr = None
    
    width = 50
    height = 30
    
    snake = [(width / 2, height / 2)]
    apple = ()
    
    DIRECTION_RIGHT = curses.KEY_RIGHT
    DIRECTION_LEFT  = curses.KEY_LEFT
    DIRECTION_UP    = curses.KEY_UP
    DIRECTION_DOWN  = curses.KEY_DOWN
    
    CURRENT_DIRECTION = DIRECTION_RIGHT
    
    TOKEN_WALL  = '#'
    TOKEN_SNAKE = 'S'
    TOKEN_APPLE = 'A'
    
    COLOR_WALL  = 1
    COLOR_SNAKE = 2
    COLOR_APPLE = 3
    
    # Cheat Options
    _noClip = False
    delay = 500
    
    def __init__(self, stdscr, *args, **kwargs):
        """Initializes the game with some options
        """
        self.stdscr = stdscr
        self._configureCurses()
        self._configureColors()
        self._configureGame(kwargs)
        
        # We need the ticks
        time.Clock()
        
        # Spawn the first apple
        self._spawnApple()
        
    def _configureCurses(self):
        # We don't want getch to block the terminal
        self.stdscr.nodelay(True)
        
        # No mouse cursor
        curses.curs_set(0)
        
        # Allow print
        curses.echo()
        
    def _configureColors(self):
        """Configures the colors; atm not supported I guess?

        """
        curses.init_pair(self.COLOR_WALL, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_SNAKE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_APPLE, curses.COLOR_RED, curses.COLOR_BLACK)
    
    def _configureGame(self, options):
        """Reads the options from the cmd and sets them for the game

        """
        self._noClip = int(options['noClip']) == 1
        self.delay = int(options['delay']) if int(options['delay']) is not -1 else 500
    
    def _draw(self):
        """Draws the game board
        """
        # Clear the board
        self.stdscr.erase()
        
        self.stdscr.hline(0, 0, self.TOKEN_WALL, self.width)
        self.stdscr.hline(self.height-1, 0, self.TOKEN_WALL, self.width)
        
        self.stdscr.vline(0, 0, self.TOKEN_WALL, self.height)
        self.stdscr.vline(0, self.width-1, self.TOKEN_WALL, self.height)

        # Draw the snake
        for s in self.snake:
            self.stdscr.addstr(s[1], s[0], self.TOKEN_SNAKE)
            
        # Draw apple
        self.stdscr.addstr(self.apple[1], self.apple[0], self.TOKEN_APPLE)

        self.stdscr.refresh()
        
    def _eatsApple(self):
        """Returns if the snake head is eating the apple

        """
        head = self.snake[0]
        return head[0] == self.apple[0] and head[1] == self.apple[1]
    
    def _spawnApple(self):
        """Spawns a new apple

        """
        x, y = 0, 0
        while True:
            x = random.choice(range(1, self.width - 1))
            y = random.choice(range(1, self.height - 1))
            
            if (x, y) not in self.snake:
                break
            
        self.apple = (x, y)
        
    def _getDirection(self):
        """Reads the current direction from ncurses

        """
        c = self.stdscr.getch()

        if c in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            self.CURRENT_DIRECTION = c
    
    def _collides(self):
        """Returns if the snake hits something

        """
        head = self.snake[0]
        
        # Stop hit yourself
        if head in self.snake[1:]:
            return True
        
        if self._noClip is False:
            return head[0] == 0 or head[0] == self.width - 1 or head[1] == 0 or head[1] == self.height - 1
        
        return False
    
    def _moveSnake(self):
        """Moves the snake in the set direction
        """
        # Current Position of the snake head
        x, y = self.snake[0]
        if self.CURRENT_DIRECTION == self.DIRECTION_UP:
            # Our coordinate system is in the fourth sqaure, so we need to
            # decrease y in order to get up (to increase to get down)
            y = y - 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_DOWN:
            y = y + 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_LEFT:
            x = x - 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_RIGHT:
            x = x + 1

        self.snake = [(x, y)] + self.snake

        # If the snake eats the apple we don't need to throw away the tail
        if not self._eatsApple():
            self.snake.pop()

        # @todo we removed the noClip on purpose
    
    def run(self):
        """Runs the main game loop


        """
        FPS = 1.0 / 8.0
        lastScreenUpdate = time.get_ticks()
        
        run = True
        while run:
            if time.get_ticks() -lastScreenUpdate < FPS:
                continue
            
            self._getDirection()
            self._moveSnake()
            
            if self._collides():
                run = False
            
            if self._eatsApple():
                self._spawnApple()
            
            self._draw()
            
            # Slow things down a bit...
            lastScreenUpdate = time.get_ticks() + self.delay
        
        # @todo write gameover message
    
def main(stdscr):
    args = vars(parse_cmd_args())

    s = Snake(stdscr, **args)
    s.run()

def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--noClip', nargs='?', default=0)
    parser.add_argument('--delay', nargs='?', default=-1)
    
    return parser.parse_args(sys.argv[1:])
    
if __name__ == '__main__':
    curses.wrapper(main)