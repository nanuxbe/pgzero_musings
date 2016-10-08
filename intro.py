alien = Actor('alien')
alien.pos = 100, 56

WIDTH = 320
HEIGHT = 240

def draw():
    screen.clear()
    alien.draw()


def update():
    alien.left += 2
    if alien.left > WIDTH:
        alien.right = 0

def set_alien_hurt():
    alien.image = 'alien_hurt'
    sounds.eep.play()
    print('Eek!')
    clock.schedule_unique(set_alien_normal, 1.0)


def set_alien_normal():
    alien.image = 'alien'

def on_mouse_down(pos):
    if alien.collidepoint(pos):
        set_alien_hurt()
    else:
        print('You missed me!')
