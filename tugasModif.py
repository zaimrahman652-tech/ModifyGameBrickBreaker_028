import tkinter as tk
import random


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 11
        self.direction = [random.choice([-1, 1]), -1]
        self.speed = 10  # Kecepatan dasar
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='#ffffff', outline='#00ffcc', width=2)
        super(Ball, self).__init__(canvas, item)

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


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100  # Paddle sedikit lebih lebar agar asyik dimainkan
        self.height = 14
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#ff007f', outline='#ffffff', width=2)
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
                
    def enlarge(self):
        # Fitur Power-up: Memperlebar paddle
        coords = self.get_position()
        current_width = coords[2] - coords[0]
        if current_width < 150:
            self.canvas.coords(self.item, coords[0] - 15, coords[1], coords[2] + 15, coords[3])


class Brick(GameObject):
    # Penambahan variasi warna dan skor poin per balok
    COLORS = {
        1: {'color': '#e74c3c', 'score': 10},  # Merah (1 Hit)
        2: {'color': '#3498db', 'score': 20},  # Biru (2 Hits)
        3: {'color': '#f1c40f', 'score': 30},  # Kuning (3 Hits)
        4: {'color': '#9b59b6', 'score': 50}   # Ungu (4 Hits - Paling Keras)
    }
