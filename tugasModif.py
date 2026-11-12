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

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 410)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, color='white', size=24):
        font = ('Consolas', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       fill=color, font=font)

    def update_hud(self):
        lives_str = f'LIVES: {self.lives}'
        score_str = f'SCORE: {self.score}'
        level_str = f'LEVEL: {self.level}'

        if self.hud is None:
            self.hud = self.draw_text(65, 20, lives_str, '#ff007f', 12)
            self.score_hud = self.draw_text(self.width - 70, 20, score_str, '#00ffcc', 12)
            self.level_hud = self.draw_text(self.width / 2, 20, level_str, '#f1c40f', 12)
        else:
            self.canvas.itemconfig(self.hud, text=lives_str)
            self.canvas.itemconfig(self.score_hud, text=score_str)
            self.canvas.itemconfig(self.level_hud, text=level_str)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        
        if num_bricks == 0:
            self.ball.speed = None
            self.level += 1
            self.draw_text(self.width/2, self.height/2, f'LEVEL {self.level} CLEAR!', '#00ffcc', 28)
            self.after(2000, self.next_level)
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_hud()
            if self.lives < 0:
                self.draw_text(self.width/2, self.height/2, 'GAME OVER!', '#ff4d4d', 32)
                self.draw_text(self.width/2, self.height/2 + 40, 'Press R to Restart', '#ffffff', 14)
                self.canvas.bind('<r>', lambda _: self.restart_game())
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(30, self.game_loop)  # Kecepatan frame diperhalus

    def next_level(self):
        self.canvas.delete('all')
        self.items = {}
        self.paddle = Paddle(self.canvas, self.width/2, 430)
        self.items[self.paddle.item] = self.paddle
        self.build_level()
        self.setup_game()
        # Tingkatkan kecepatan bola di level berikutnya
        self.ball.speed += 2

    def restart_game(self):
        self.canvas.unbind('<r>')
        self.canvas.delete('all')
        self.items = {}
        self.lives = 3
        self.score = 0
        self.level = 1
        self.paddle = Paddle(self.canvas, self.width/2, 430)
        self.items[self.paddle.item] = self.paddle
        self.build_level()
        self.setup_game()

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        
        for obj in objects:
            if isinstance(obj, Brick):
                # Tambah skor dinamis berdasarkan jenis balok yang dihancurkan
                self.score += Brick.COLORS[obj.hits]['score']
                self.update_hud()
                
        self.ball.collide(objects)
