from asciimatics.screen import Screen
import random
import time


def tiny_snake(screen):
    w, h = screen.width, screen.height
    head = (w // 2, h // 2)
    direction = (1, 0)
    body = []
    food = (random.randint(1, w - 2), random.randint(1, h - 2))

    while True:
        screen.clear()

        banner = "Mercury-CLI, Made by FourteenIP Dev Team"
        instructions = "Press 'q' to quit, Arrow keys to move"
        screen.print_at(banner, max(0, (w - len(banner)) // 2), 0)
        screen.print_at(instructions, max(0, (w - len(instructions)) // 2), 1)

        screen.print_at("@", head[0], head[1])
        screen.print_at("*", food[0], food[1])
        for bx, by in body:
            screen.print_at("o", bx, by)
        screen.refresh()

        key = screen.get_key()
        if key in (ord("q"),):
            return
        if key == Screen.KEY_LEFT:
            direction = (-1, 0)
        if key == Screen.KEY_RIGHT:
            direction = (1, 0)
        if key == Screen.KEY_UP:
            direction = (0, -1)
        if key == Screen.KEY_DOWN:
            direction = (0, 1)

        head = ((head[0] + direction[0]) % w, (head[1] + direction[1]) % h)
        body.insert(0, head)
        if head == food:
            food = (random.randint(1, w - 2), random.randint(1, h - 2))
        else:
            if body:
                body.pop()

        time.sleep(0.08)


def main():
    Screen.wrapper(tiny_snake)
