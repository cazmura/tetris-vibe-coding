import pygame
import random

# 色の定義
COLORS = [
    (0, 0, 0),        # 黒（背景）
    (120, 37, 179),   # 紫
    (100, 179, 179),  # シアン
    (80, 34, 22),     # 茶
    (80, 134, 22),    # 緑
    (180, 34, 22),    # 赤
    (180, 34, 122),   # ピンク
]

# テトリミノの形状
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 2, 5, 6]],  # O
    [[5, 6, 8, 9], [1, 5, 6, 10]],  # S
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
    [[4, 5, 9, 10], [2, 6, 5, 9]]  # Z
]

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        self.figure = None
        self.x = 100  # 左端からの距離を100ピクセルに設定
        self.y = 60   # 上端からの距離を60ピクセルに設定
        self.zoom = 30
        self.figure_type = 0
        self.figure_rotation = 0
        self.figure_x = 0  # 現在のブロックのx位置
        self.figure_y = 0  # 現在のブロックのy位置
        
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure_type = random.randint(0, len(SHAPES) - 1)
        self.figure_rotation = 0
        self.figure = SHAPES[self.figure_type][self.figure_rotation]
        self.figure_x = int(self.width / 2 - 2)  # 新しいブロックの初期x位置
        self.figure_y = 0  # 新しいブロックの初期y位置

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure:
                    if i + self.figure_y > self.height - 1 or \
                       j + self.figure_x > self.width - 1 or \
                       j + self.figure_x < 0 or \
                       self.field[i + self.figure_y][j + self.figure_x] > 0:
                        return True
        return False

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure:
                    self.field[i + self.figure_y][j + self.figure_x] = self.figure_type + 1
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1-1][j]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure_y += 1
        self.figure_y -= 1
        self.freeze()

    def go_down(self):
        self.figure_y += 1
        if self.intersects():
            self.figure_y -= 1
            self.freeze()

    def go_side(self, dx):
        old_x = self.figure_x
        self.figure_x += dx
        if self.intersects():
            self.figure_x = old_x

    def rotate(self):
        old_rotation = self.figure_rotation
        self.figure_rotation = (self.figure_rotation + 1) % len(SHAPES[self.figure_type])
        self.figure = SHAPES[self.figure_type][self.figure_rotation]
        if self.intersects():
            self.figure_rotation = old_rotation
            self.figure = SHAPES[self.figure_type][self.figure_rotation]

def main():
    pygame.init()
    size = (600, 700)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Tetris")

    # ゲームの初期化
    game = Tetris(20, 10)
    clock = pygame.time.Clock()
    fps = 25
    counter = 0
    pressing_down = False

    while True:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // 2) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                if event.key == pygame.K_SPACE:
                    game.go_space()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        screen.fill((255, 255, 255))

        # フィールドの描画
        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(screen, (128, 128, 128),
                               [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                if game.field[i][j] > 0:
                    pygame.draw.rect(screen, COLORS[game.field[i][j] - 1],
                                   [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

        # 落下中のブロックの描画
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure:
                        pygame.draw.rect(screen, COLORS[game.figure_type],
                                       [game.x + game.zoom * (j + game.figure_x) + 1,
                                        game.y + game.zoom * (i + game.figure_y) + 1,
                                        game.zoom - 2, game.zoom - 1])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(game.score), True, (0, 0, 0))
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        screen.blit(text, [20, 20])
        if game.state == "gameover":
            screen.blit(text_game_over, [150, 200])
            screen.blit(text_game_over1, [155, 265])

        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':
    main() 