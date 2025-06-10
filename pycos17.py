from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from kivy.vector import Vector
from kivy.graphics import Ellipse, Rectangle
from kivy.clock import Clock
import os
import random
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
#LabelBase.register('msjh', 'c:\Windows\Fonts\msjh.ttc')

# Refactor: 一致性
SPEED_INIT = 3
SCORE_INIT = 0
RACKET_WIDTH_INIT = 200
LIFE_INIT = 3

class Ball(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = [0, 0]
        self.size = (50, 50)
        with self.canvas:
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def move(self):
        self.pos = Vector(*self.speed) + self.pos

    def on_pos(self, instance, value):
        self.ellipse.pos = self.pos

class Racket(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = [0, 0]
        self.size = [200, 25]
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def move(self):
        self.pos = Vector(*self.speed) + self.pos

    def on_pos(self, instance, value):
        self.rect.pos = self.pos

    # Refactor
    def change_width(self, racket_width):
        self.size[0] = racket_width
        self.canvas.clear()
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)

class Playground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = Ball()
        self.add_widget(self.ball)
        self.racket = Racket()
        self.add_widget(self.racket)
        self.refresh_rate = 1/60
        
        # Refactor
        f = open('racket_ball.txt')
        l = f.readlines()
        f.close()
        self.score = 0
        self.speed = 1
        self.life = 3
        self.highscore=int(l[4])
        self.scoreboard = create_label("", [100, 50] , self)
        self.set_score(self.score)
        self.speedboard = create_label("", [100, 50] , self)
        self.set_speed(self.speed)
        self.lifeboard = create_label("", [100, 50] , self)
        self.set_life(self.life)
        self.highscoreboard = create_label("", [100, 50] , self)
        self.set_highscore(self.highscore)
        
        self.sound = SoundLoader.load('mixkit-hard-horror-hit-drum-565s.wav')

        # Refactor
        self.close_button = create_button('Close', [60, 30], self, self.close_confirm)
        self.restart_button = create_button('Restart', [60, 30], self, self.restart_app)
        self.pause_button = create_button('', [60, 30], self, self.pause_app)
        self.set_pause(False)

    # Refactor: 一致性
    def set_score(self, score):
        self.score = score
        self.scoreboard.text = "Score: " + str(self.score)

    # Refactor: 一致性
    def set_speed(self, speed):
        self.speed = speed
        self.speedboard.text = "Speed: " + str(self.speed)

    def set_life(self, life):
        self.life = life
        self.lifeboard.text = "Life: " + str(self.life)
    
    def set_highscore(self, highscore):
        self.highscore = highscore
        self.highscoreboard.text = "Highscore: " + str(self.highscore)

        
    def close_confirm(self, event):
        root = Widget()
        
        # Refactor
        msg = create_label("Are you sure?", [100, 50], root)
        close_button = create_button('Close', [60, 30], root, self.close_app)
        cancel_button = create_button('Cancel', [60, 30], root, self.cancel_popup)
        
        popup = Popup(title="Close App", content=root, size_hint=(.6, .6), auto_dismiss=False)
        popup.open()

        self.close_popup = popup
        msg.center = popup.center
        close_button.pos = [popup.x + 10, popup.y + 10]
        cancel_button.pos = [close_button.x + close_button.width + 10, popup.y + 10]
        
        # Refactor: 一致性
        self.set_pause(True)

    def cancel_popup(self, event):
        self.close_popup.dismiss()

    def close_app(self, event):
        ballapp.stop()
        save_data(self.speed, self.score, self.racket.size[0], self.life)

    def restart_app_life(self, event):
        self.restart_app(event)
        self.life_reduce_popup.dismiss()
        self.on_size(None, None)

    def restart_app(self, event):
        # Refactor
        self.set_speed(SPEED_INIT)
        self.set_score(SCORE_INIT)
        self.set_life(LIFE_INIT)
        self.racket.change_width(RACKET_WIDTH_INIT)
        
        self.ball.speed = [self.speed, self.speed]
        self.on_size(None, None)

    def pause_app(self, event):
        # Refactor
        self.is_pause = not self.is_pause
        self.set_pause(self.is_pause)

    # Refactor: 一致性
    def set_pause(self, is_pause):
        self.is_pause = is_pause
        self.pause_button.text = 'Play' if self.is_pause else 'Pause'

    def on_size(self, instance, value):
        self.ball.center = self.center
        self.racket.y = 100
        self.racket.center_x = self.center[0]
        self.scoreboard.pos = [0, self.height - 50]
        self.speedboard.pos = [100, self.height - 50]
        self.lifeboard.pos = [200, self.height - 50]
        self.highscoreboard.pos = [300, self.height - 50]
        
        self.close_button.pos = [self.width - self.close_button.size[0], 0]
        self.restart_button.pos = [self.close_button.x - self.restart_button.size[0], 0]
        self.pause_button.pos = [self.restart_button.x - self.pause_button.size[0], 0]

    def cont_app(self, event):
        self.life_reduce_popup.dismiss()
        if self.life > 0:
            self.on_size(None, None)
            self.set_pause(False)

    def life_reduce_popup_func(self):
        root = Widget()

        close_button = None
        if self.life <= 0:
            msg = create_label("Life: " + str(self.life) + ". Want to restart", [100, 50], root)
            the_button = create_button('Restart', [60, 30], root, self.restart_app_life) 
            close_button = create_button('No', [60, 30], root, self.cont_app) 
                
        else:
            msg = create_label("Life: " + str(self.life), [100, 50], root)
            the_button = create_button('Continue', [60, 30], root, self.cont_app)
        
        popup = Popup(title="Life reduction", content=root, size_hint=(.6, .6), auto_dismiss=False)
        popup.open()
        self.life_reduce_popup = popup

        msg.center = popup.center
        the_button.pos = [popup.x + 10, popup.y + 10]
        if close_button != None:
            close_button.pos = [the_button.x + the_button.width + 10, popup.y + 10]
        self.set_pause(True)
        
    def update(self, dt):
        if self.is_pause:
            return
        # 決定球的動作
        try:
            for ball in [self.ball]:
                for i, wall_length in [[0, self.width], [1, self.height]]:
                    if ball.pos[i] >= (wall_length - ball.size[0]) or ball.pos[i] <= 0:
                        if i == 1:
                            if ball.pos[i] <= 0:
                                self.life -= 1
                                self.set_life(self.life)
                                self.life_reduce_popup_func()
                                
                        self.sound.play()
                        self.score += 1

                        if self.score % 5 == 0:
                            #a = 1/(int(speed) - int(speed))
                            self.speed += 1
                            
                            # Refactor
                            self.set_speed(self.speed)
                            
                            self.racket.size[0] = self.racket.size[0] - 20
                            if self.racket.size[0] < 10:
                                self.racket.size[0] = 10

                            # Refactor
                            self.racket.change_width(self.racket.width)

                        # Refactor
                        self.set_score(self.score)
                        
                        rnd = self.speed
                        ball.speed[i] = -(ball.speed[i] / abs(ball.speed[i]))*rnd
                        ball.speed[1 - i] = (ball.speed[1-i]/ abs(ball.speed[1-i]))*rnd

                        if ball.pos[i] < 0:
                            ball.pos[i] = 0
                        if ball.pos[i] > wall_length-ball.size[0]:
                            ball.pos[i] = wall_length-ball.size[0]
                ball.move()
                # 碰到球拍
                if self.racket.collide_widget(ball):
                    self.sound.play()
                    if self.ball.speed[1] < 0:
                        self.ball.y = self.racket.y + self.racket.height + 1
                    else:
                        self.ball.y = self.racket.y - self.ball.height - 1
                    ball.speed = [ball.speed[0], -ball.speed[1]]
        except Exception as err:
            root = Widget()

            # Refactor
            msg = create_label(str(err), [100, 50], root)
            close_button = create_button('Close', [60, 30], root, self.close_app)
            
            popup = Popup(title="Error occurred", content=root, size_hint=(.6, .6), auto_dismiss=False)
            popup.open()

            msg.center = popup.center
            close_button.pos = [popup.x + 10, popup.y + 10]
            self.set_pause(True)
            save_data(self.speed, self.score, self.racket.size[0])

    def on_touch_move(self, touch):
        if self.is_pause:
            return
        self.racket.center_x = touch.x

class BallApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.playground = Playground()

    def build(self):
        if not hasattr(self, 'refresh_rate'):
            self.playground.refresh_rate = 1.0/60.0
        Clock.schedule_interval(self.playground.update, self.refresh_rate)
        return self.playground

# Refactor
def create_button(btn_text, btn_size, parent_widget, press_handler):
    _button = Button()
    _button.text = btn_text
    _button.size = btn_size 
    parent_widget.add_widget(_button)
    _button.bind(on_press=press_handler)

    return _button

# Refactor
def create_label(label_text, label_size, parent_widget):
    _label = Label()
    _label.text = label_text
    _label.size = label_size
    parent_widget.add_widget(_label)

    return _label

# Refactor
def save_data(speed, score, racket_width, life):
    f = open('racket_ball.txt', 'w')
    f.write(str(speed))
    f.write("\n" + str(score))
    f.write("\n" + str(racket_width))
    f.write("\n" + str(life))
    if(score>highscore):
        f.write("\n" + str(score))
    else:
        f.write("\n" + str(highscore))
    f.close()

if __name__ == '__main__':
    # ----- 設定寫在這之下 -----
    refresh_rate = 1.0/60.0 # 畫面更新頻率
    # ----- 設定寫在這之上 -----
    try:
        f = open('racket_ball.txt')
        l = f.readlines()
        f.close()
        speed = int(l[0])
        score = int(l[1])
        racket_width = int(l[2])
        life = int(l[3])
        highscore = int(l[4])
    except Exception as err:
        print(str(err))
        exit()
    
    ballapp = BallApp()
    ballapp.refresh_rate = refresh_rate
    
    # Refactor
    ballapp.playground.set_speed(speed)
    ballapp.playground.set_score(score)
    ballapp.playground.set_life(life)
    ballapp.playground.racket.change_width(racket_width)

    ballapp.playground.ball.speed = [speed, speed]

    from kivy.core.window import Window
    Window.size = (800, 500)
    ballapp.run()
    
    # Refactor
    save_data(ballapp.playground.speed, ballapp.playground.score, ballapp.playground.racket.size[0], ballapp.playground.life)
    
    
    
   