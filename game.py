import time

import pygame

import logic, config, bot


class Game():
    """
    Класс игрового окна
    """

    def __init__(self):
        pygame.init()

        self.bot = bot.Bot()
        self.bot_activate = True
    
        self.line_colour = config.BLACK
        self.font = pygame.font.SysFont('ubuntu', 24)
        self.check_font()

        self.game_over = False

        self.SCREEN_SIZE = (800, 630)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption('Senegal Checkers')

        self.background = pygame.image.load('./wood_2.jpg')
        self.screen.blit(self.background, (0, 0))

        self.draw_field()

        self.playboard = logic.Playboard(self.screen)

        self.draw_markup()
        self.draw_info()
    
    def start_game(self):
        """
        Главный игровой цикл
        """        

        while not self.game_over:
            self.screen_update()

            self.playboard.find_all_possible_move()
            self.playboard.check_end_game()

            if self.playboard.end_game:
                self.playboard.added_score()
                self.draw_win_info()
                time.sleep(3)
                self.playboard.__init__(self.screen)
            
            for event in pygame.event.get():
                
                turn_bot = self.playboard.turn_color == 'BLACK'
                if self.bot_activate == True and turn_bot:
                    time.sleep(1)

                    self.playboard.pick_checker(self.bot._choose_checker(
                        self.playboard.all_possible_move,
                        self.playboard.all_checkers
                    ))

                    self.playboard.get_empty_cells()

                    self.playboard.release_checker(self.bot._choose_move(
                        self.playboard.all_possible_move,
                        self.playboard.turn_type
                    ))
                    break

                if event.type == pygame.QUIT:
                    self.game_over = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.playboard.button_down()
                    break
                        
                if event.type == pygame.MOUSEBUTTONUP:
                    self.playboard.button_up()
                    self.screen_update()
                    break

            pygame.display.update()
    
    def screen_update(self):
        """
        Обновление экрана        
        """

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))
        self.draw_field()
        self.playboard.draw_chekers()
        self.draw_markup()
        self.draw_info()
    
        self.playboard.check_end_game()

    def draw_field(self):
        """
        Рисует игровое поле
        """

        HEIGHT = config.BOARD_SIZE[0]
        WIDTH = config.BOARD_SIZE[1]
        coords = {'x': 130, 'y': 130}

        self._draw_lines(WIDTH + 1, coords,
                         None, self.SCREEN_SIZE[1] - 50)
        self._draw_lines(WIDTH + 1, coords,
                         self.SCREEN_SIZE[0] - 130, None)

        # Рисование диагональных линий по центру доски
        pygame.draw.line(self.screen, self.line_colour,
                         [coords['x'] + config.CELLS_SIZE * 2,
                          coords['y'] + config.CELLS_SIZE * 2],
                         [coords['x'] + config.CELLS_SIZE * 4,
                          coords['y'] + config.CELLS_SIZE * 3], 2)
        pygame.draw.line(self.screen, self.line_colour,
                         [coords['x'] + config.CELLS_SIZE * 2,
                          coords['y'] + config.CELLS_SIZE * 3],
                         [coords['x'] + config.CELLS_SIZE * 4,
                          coords['y'] + config.CELLS_SIZE * 2], 2)

        self._draw_contour()
    
    def _draw_lines(self, range_, start_coords, fin_x, fin_y):
        """
        Расчерчивает игровое поле линиями
        """
        
        coords = start_coords.copy()
        
        for _ in range(range_):
            if not fin_x:
                pygame.draw.line(self.screen, self.line_colour,
                                 [coords['x'], coords['y']],
                                 [coords['x'], fin_y], 2)
                coords['x'] += config.CELLS_SIZE
            elif not fin_y:
                pygame.draw.line(self.screen, self.line_colour,
                                 [coords['x'], coords['y']],
                                 [fin_x, coords['y']], 2)
                coords['y'] += config.CELLS_SIZE
        
    def _draw_contour(self, points=[[120, 120], [120, 590],
                                    [680, 590], [680, 120]]):
        """
        Рисует контур
        """

        coef = -1
        for i in points:
            pygame.draw.line(self.screen, self.line_colour,
                             points[coef], points[coef+1], 5)
            coef += 1    
    
    def draw_info(self):
        """
        Добавляет информационные надписи
        """

        colour = {'WHITE': 'БЕЛЫЕ', 'BLACK': 'ЧЕРНЫЕ'}

        text_white_score = f'Счет белых: {self.playboard.score["WHITE"]}'
        text_black_score = f'Счет черных: {self.playboard.score["BLACK"]}'
        text_turn_colour = f'Текущий ход: {colour[self.playboard.turn_color]}'

        follow_white = self.font.render(text_white_score, 1, self.line_colour)
        follow_black = self.font.render(text_black_score, 1, self.line_colour)
        follow_turn = self.font.render(text_turn_colour, 1, self.line_colour)

        self.screen.blit(follow_white, (20, 20))
        self.screen.blit(follow_black, (610, 20))
        self.screen.blit(follow_turn, (280, 20))

        pygame.display.update()

    def draw_markup(self):
        """
        Добавляет разметку доски (буквы/цифры)
        """

        for side in range(4):
            if side == 0:
                coords = [95, 165]
            elif side == 1:
                coords = [165, 600]
            elif side == 2:
                coords = [695, 165]
            else:
                coords = [165, 85]

            for char in range(config.BOARD_SIZE[side % 2]):
                if side % 2 == 0:
                    follow = self.font.render(str(char+1), 1, self.line_colour)
                    self.screen.blit(follow, coords)

                    coords[1] += 90
                else:
                    follow = self.font.render(
                        self.playboard.chars_coords[char], 1, self.line_colour)
                    self.screen.blit(follow, coords)

                    coords[0] += 90


    def draw_win_info(self):
        """
        Показывает информацию о победителе
        """

        if self.playboard.score['WHITE'] > self.playboard.score['BLACK']:
            colour = 'БЕЛЫЕ'
            coords = (190, 326)
        else:
            colour = 'ЧЕРНЫЕ'
            coords = (173, 326)
        
        if (f := 'arial') in pygame.font.get_fonts():
            font = pygame.font.SysFont(f, 48)
        else:
            font = pygame.font.SysFont('ubuntu', 48)

        text = f'{colour} ВЫИГРАЛИ'
        follow = font.render(text, 1, config.WHITE)
        self.screen.blit(follow, coords)

        pygame.display.update()

    def check_font(self):
        """
        Проверка наличия шрифта в системе
        """

        if (f := 'arial') in pygame.font.get_fonts():
            self.font = pygame.font.SysFont(f, 24)


if __name__ == '__main__':
    g = Game()
    g.start_game()
