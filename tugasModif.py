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

    def __init__(self, canvas, x, y, hits):
        self.width = 72
        self.height = 22
        self.hits = hits
        cfg = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=cfg['color'], outline='#111111', tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits]['color'])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.level = 1
        self.width = 650
        self.height = 500
        
        # Tema warna latar belakang gelap futuristik
        self.canvas = tk.Canvas(self, bg='#0f0f1a',
                                width=self.width,
                                height=self.height, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 430)
        self.items[self.paddle.item] = self.paddle
        
        self.build_level()

        self.hud = None
        self.score_hud = None
        self.level_hud = None
        
        self.setup_game()
        self.canvas.focus_set()
        
        # Menggunakan kontrol tombol panah dengan responsivitas tinggi
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))
        self.canvas.bind('<a>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<d>', lambda _: self.paddle.move(20))

    def build_level(self):
        # Menyusun pola balok berlapis dari level kesulitan 1 sampai 4
        for x in range(12, self.width - 12, 76):
            self.add_brick(x + 36, 50, 4)
            self.add_brick(x + 36, 76, 3)
            self.add_brick(x + 36, 102, 2)
            self.add_brick(x + 36, 128, 1)

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(self.width/2, self.height/2,
                                   'PRESS SPACE TO LAUNCH', '#00ffcc', 22)
        self.canvas.bind('<space>', lambda _: self.start_game())
