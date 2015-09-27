#!/usr/bin/python


try:
    # from random import randint
    import easygui
    import os
    import json
    from sfml.graphics import RenderWindow, Color, Font, Text, \
        Image, View, Rectangle, Texture, Sprite, TransformableDrawable, \
        VertexArray, PrimitiveType
    from sfml.window import VideoMode, Style, CloseEvent, ContextSettings, \
        Keyboard, KeyEvent
    from sfml.system import Clock, Time, seconds, Vector2
    from sfml.audio import Music
except Exception as e:
    print e
    exit(1)


def alert(title, text):
    easygui.msgbox(text, title)

# WINDOW
WIDTH, HEIGHT, BPP = 800, 600, 32
SETTINGS = ContextSettings()
SETTINGS.antialiasing_level = 8
TITLE = "Simple Game in PySFML"

# PATH's
ROOT = os.getcwd() + '/'
ASSETS_PATH = os.getcwd() + '/assets/'
MUSICS = ASSETS_PATH + 'musics/'
FONTS = ASSETS_PATH + 'fonts/'
SPRITES = ASSETS_PATH + 'sprites/'

asset = {
    'icon': (ROOT + 'icon.png'),
    'mario': (SPRITES + 'mario.png'),
    'bg': (SPRITES + 'bg.png'),
    'fps_font': (FONTS+'FreePixel.ttf'),
}

# Print all assets
for key, value in asset.items():
    # -/+ aling left or right
    # 20  space
    # s   formt string
    # %   firt % is scape
    print ('%-20s%-20s' % (key, value))


class GameObject(object):
    def __init__(self):
        self.sprite = None
        self.x = None
        self.y = None

    def update(self, delta):
        pass

    def draw(self, window):
        window.draw(self.sprite)


def load_animations(path):
    try:
        with open(path) as data_json:
            return json.load(data_json)
    except Exception as e:
        alert("Load Animations", e)


class Animation(object):
    """
    """
    def __init__(self, name, animation, texture):
        try:
            self.texture = texture
            self.animation = animation
            self.name = name
            self.frames = self.set_frames(self.name)

        except IOError, e:
            alert(self.__name__, e)
            exit(1)

    def set_frames(self, name):
        frames = []
        if self.animation:
            for frame in self.animation[name]:
                x, y = frame['x'], frame['y']
                w, h = frame['w'], frame['h']
                frames.append(Rectangle((x, y), (w, h)))
            return frames


class AnimatedSprite(TransformableDrawable):
    def __init__(self, frametime=seconds(0.1), paused=False, looped=True):
        super(AnimatedSprite, self).__init__()

        self.animation = None
        self.frametime = frametime
        self.paused = paused
        self.looped = looped

        self.current_time = None
        self.current_frame = 0

        self.texture = None

        self.vertices = VertexArray(PrimitiveType.QUADS, 4)

    def set_animation(self, animation):
        self.animation = animation
        self.texture = animation.texture
        self.current_frame = 0
        self.set_frame(0)

    def play(self, animation=None):
        if animation and self.animation is not animation:
            self.set_animation(animation)
        self.paused = False

    def pause(self):
        self.paused = True

    def stop(self):
        self.paused = True
        self.current_frame = 0
        self.set_frame(self.current_frame)

    def set_color(self, color):
        for i in self.vertices:
            i.color = color

    def local_bounds(self):
        rect = self.animation.frames[self.current_frame]

        width = abs(rect.width)
        height = abs(rect.height)
        return Rectangle((0.0, 0.0), (width, height))

    @property
    def global_bounds(self):
        return self.transform.transform_rectangle(self.local_bounds())

    def set_frame(self, frame, reset_time=True):
        if self.animation:
            rect = self.animation.frames[frame]

            self.vertices[0].position = Vector2(0.0, 0.0)
            self.vertices[1].position = Vector2(0.0, rect.height)
            self.vertices[2].position = Vector2(rect.width, rect.height)
            self.vertices[3].position = Vector2(rect.width, 0.0)

            left = rect.left + 0.0001
            right = left + rect.width
            top = rect.top
            bottom = top + rect.height

            self.vertices[0].tex_coords = Vector2(left, top)
            self.vertices[1].tex_coords = Vector2(left, bottom)
            self.vertices[2].tex_coords = Vector2(right, bottom)
            self.vertices[3].tex_coords = Vector2(right, top)

        if reset_time:
            self.current_time = Time.ZERO

    def update(self, delta):
        if not self.paused and self.animation:
            self.current_time += delta

            if self.current_time >= self.frametime:
                self.current_time -= self.frametime

                if self.current_frame + 1 < len(self.animation.frames):
                    self.current_frame += 1

                else:
                    self.current_frame = 0

                    if not self.looped:
                        self.paused = True

                self.set_frame(self.current_frame, False)

    def draw(self, target, states):
        if self.animation and self.texture:
            states.transform *= self.transform
            states.texture = self.texture
            target.draw(self.vertices, states)


class Player(GameObject):
    """
    """
    def __init__(self, window, sprite, texture, x, y):
        super(Player, self).__init__()
        self.window = window
        self.sprite = sprite
        self.texture = texture
        self.x = x
        self.y = y
        self.speed = 40.0

        # Animations
        self.animation = load_animations("assets/animations/player.anim")

        # Animation Walk R
        self.walk_r = Animation("walk", self.animation, self.texture)

        # Animation Walk L
        self.walk_l = Animation("walk", self.animation, self.texture)

        # Animation Stopped
        self.stopped = Animation("stopped", self.animation, self.texture)

        self.current_animation = self.stopped
        self.anim_sprite = AnimatedSprite(seconds(0.1), True, False)
        self.anim_sprite.position = Vector2(0, 0)

    def animate(self, animation):
        self.current_animation = animation

    def draw(self, window):
        window.draw(self.anim_sprite)

    def update(self, delta):
        self.moviment = Vector2(0.0, 0.0)

        self.anim_sprite.play(self.current_animation)

        if Keyboard.is_key_pressed(Keyboard.D):
            self.moviment += Vector2(self.speed, 0)
            self.animate(self.walk_r)
        elif Keyboard.is_key_pressed(Keyboard.A):
            self.moviment += Vector2(-self.speed, 0)
            self.current_animation = self.walk_l
        else:
            self.anim_sprite.stop()

        self.anim_sprite.update(delta)
        self.anim_sprite.move(self.moviment * delta.seconds)

        self.sprite.move(Vector2(0.0, 0.0)*delta.seconds)
        for e in self.window.events:
            pass


class FPS(GameObject):
    def __init__(self, text, pos, color=Color.GREEN):
        super(FPS, self).__init__()
        self.text = text
        self.pos = pos

    def update(self, text):
        self.text = text

    def draw(self, window):
        window.draw(self.text)


class Game(object):
    """..."""
    def __init__(self):
        # Load Assets
        self.load_content()

        self.window = RenderWindow(VideoMode(WIDTH, HEIGHT, BPP), TITLE,
                                   Style.CLOSE | Style.TITLEBAR,
                                   SETTINGS)
        self.window.framerate_limit = 60
        self.window.icon = self.icon.pixels

        # Clock
        self.clock = Clock()
        self.time_since_last_update = Time.ZERO
        self.FPS = seconds(1.0/30.0)

        # View
        self.view = View(Rectangle((0, 0), (WIDTH, HEIGHT)))
        # self.view.reset(Rectangle((0, 0), (WIDTH, HEIGHT)))
        self.view.viewport = (0.0, 0.0, 1.0, 1.0)

        self.hud = View(Rectangle((0, 0), (WIDTH, HEIGHT)))
        self.hud.viewport = (0.0, 0.0, 1, 1.0)

        # attr: font, text, pos, color=Color.GREEN
        self.fps_pos = Vector2(15, 15)
        self.fps_text_content = '...'
        self.fps_text = Text(self.fps_text_content,
                             self.fps_font, 14)

        self.fps = FPS(self.fps_text,
                       self.fps_pos)

        # PLAYER
        self.player_spt = Sprite(self.player_texture)
        self.player = Player(self.window,
                             self.player_spt,
                             self.player_texture, 0, 0)

        self.bg = Sprite(self.bg)

    def run(self):
        # zoom = 1
        while self.window.is_open:
            for event in self.window.events:
                if type(event) is KeyEvent:
                    if event.pressed:
                        if event.code is Keyboard.ESCAPE:
                            self.window.close()

                # close evt
                if type(event) is CloseEvent:
                    self.window.close()

            dt = self.clock.elapsed_time
            self.clock.restart()

            # self.view.center = self.player_spt.position

            self.fps_text_content = 'FPS: %s' % (1.0/dt.seconds)
            self.fps_text.string = self.fps_text_content

            self.update(dt)
            self.draw()

    def update(self, delta):
        self.player.update(delta)

    def draw(self):
        self.window.clear()
        #
        self.window.view = self.view
        self.window.draw(self.bg)
        self.player.draw(self.window)

        self.window.view = self.hud

        self.fps.draw(self.window)
        self.window.display()

    def load_content(self):
        try:
            self.icon = self.asset('I', asset['icon'])
            self.player_texture = self.asset('S', asset['mario'])
            self.bg = self.asset('S', asset['bg'])
            self.fps_font = self.asset('F', asset['fps_font'])

        except Exception as e:
            alert('Error loading file', e)
            exit(1)

    def asset(self, category, name):
        # M : Music [ogg, wav, flac, aiff, au, raw, paf, svx, nist, voc, ircam,
        # w64, mat4, mat5 pvf, htk, sds, avr, sd2, caf, wve, mpc2k, rf64.]
        if category is 'M':
            return Music.from_file(name)

        # F : Font [TrueType, Type 1, CFF, OpenType, SFNT, X11 PCF,
        # Windows FNT, BDF, PFR and Type 42]
        if category is 'F':
            return Font.from_file(name)

        # S : Sprite [bmp, png, tga, jpg, gif, psd, hdr and pic]
        if category is 'S':
            return Texture.from_file(name)

        if category is 'I':
            return Image.from_file(name)


if __name__ == '__main__':
    Game().run()
