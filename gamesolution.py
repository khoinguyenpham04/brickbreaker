import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
# creating the game window
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
#Returns the position of this game object.
    def get_position(self):
        return self.canvas.coords(self.item)
#Moves this game object by a given amount.
    def move(self, x, y):
        self.canvas.move(self.item, x, y)
#Deletes this game object from the canvas.
    def delete(self):
        self.canvas.delete(self.item)

# creating the ball
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        # increase the below value to increase the speed of ball
        self.speed = 5
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)
#Returns the position of this game object.
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
#Returns the position of this game object.
    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

# creating the paddle
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

# creating the bricks
class Brick(GameObject):
    COLORS = {1: '#34D5EB', 2: '#347AEB', 3: '#3437EB'}

    def __init__(self, canvas, x, y, hits):
        self.width = 80
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)
    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])
            
# creating the game class
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 900
        self.height = 600
        self.canvas = tk.Canvas(self, bg= 'black',
                                width=self.width,
                                height=self.height,)
        
        self.canvas.pack()
        self.pack()
        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 400)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 70):
            self.add_brick(x + 40, 50, 3)
            self.add_brick(x + 40, 80, 2)
            self.add_brick(x + 40, 110, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-25))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(25))
#set up the game
    def setup_game(self): 
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200,
                                    'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 383)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()
# set up game loop
    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Breaker of Bricks')
# Load background PNG into a TK image (Needs PIL)
    image = Image.open(f"background.png")
    imageTk = ImageTk.PhotoImage(image)

    # Change width and heihgt to your width and height
    canvas = tk.Canvas(root, width=900, height=600)
    canvas.pack(fill = "both", expand = True) 
    
    canvas.create_image( 0, 0, image = imageTk,  
                        anchor = "nw")
    game = Game(root)
    game.mainloop()
