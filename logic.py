import pygame

import config


class Playboard:
    """
    Класс логики игры
    """

    def __init__(self, screen):
        self.BOARD = config.BOARD.copy()
        self.screen = screen
        self.picked_checker = None
        self.turn_type = None
        self.turn_color = 'WHITE'
        self.turn_previous = 'BLACK'
        self.chars_coords = 'ABCDEF'
        self.end_game = False

        self.all_possible_move = None
        self.all_checkers = pygame.sprite.Group()
        self.all_empty_cells = []

        self.draw_chekers()
        self.get_empty_cells()

        self.score = {'WHITE': 0, 'BLACK': 0}

    def draw_chekers(self):
        """
        Создание и отрисовка фишек на доске
        """

        self.all_checkers = pygame.sprite.Group()

        coord = [175, 175]
        colour = {'b': 'BLACK', 'w': 'WHITE'}
        count = 1

        for pos in self.BOARD.keys():
            
            if self.BOARD[pos] == 'b' or self.BOARD[pos] == 'w':
                self.all_checkers.add(
                        Checkers(config.CHECKERS_SIZE,
                        pos, tuple(coord), colour[self.BOARD[pos]],
                        f'./Images/checker_{self.BOARD[pos]}.png')
                    )
            coord[0] += config.CELLS_SIZE
            count += 1

            if count > 6:
                count = 1
                coord[0] = 175
                coord[1] += config.CELLS_SIZE
        
        self.all_checkers.draw(self.screen)

    def check_end_game(self):
        """
        Проверка на завершение игры
        """

        self.all_possible_move = self.find_all_possible_move()
        
        if len(self.all_possible_move) == 0:
            return True

        white_min_pos = 1
        black_max_pos = 5

        for checker in self.all_checkers:
            if checker.colour == 'WHITE' and \
                    (m := int(checker.pos[1])) > white_min_pos:
                white_min_pos = m
            elif checker.colour == 'BLACK' and \
                    (m := int(checker.pos[1])) < black_max_pos:
                black_max_pos = m

        return white_min_pos < black_max_pos

    def added_score(self):
        for checker in self.all_checkers:
            if checker.colour == 'WHITE' and checker.pos[1] == '1':
                self.score['WHITE'] += 1
            elif checker.colour == 'BLACK' and checker.pos[1] == '5':
                self.score['BLACK'] += 1

    def button_down(self):
        """
        Действие при нажатии на кнопку мыши
        """
        
        self.end_game = self.check_end_game()
        
    def button_up(self):
        """
        Действие при отпуске кнопки мыши
        """

        if self.picked_checker == None:
            self.all_possible_move = self.find_all_possible_move()
            self.pick_checker(self.get_checker_pos())
        elif self.put_in_place():
            self.picked_checker = None
        else:
            self.all_possible_move = self.find_all_possible_move()
            self.get_empty_cells()
            if (cells := self.get_cells_pos()):
                self.release_checker(cells[0])
        
    def pick_checker(self, current_checker):
        """
        Взять фишку
        """
        
        if current_checker and current_checker.colour == self.turn_color and \
                current_checker.pos in self.all_possible_move.keys():
            self.picked_checker = current_checker

    def release_checker(self, cells_pos):
        """
        Положить фишку
        """
   
        if cells_pos in self.all_possible_move[self.picked_checker.pos]:
            self.BOARD[self.picked_checker.pos] = 0
            self.BOARD[cells_pos] = self.picked_checker.colour[0].lower()

            if self.turn_type == 'cuts':
                self.BOARD[self.all_possible_move[
                    self.picked_checker.pos][1]] = 0
                self.score[self.turn_color] += 1
                self.picked_checker.pos = cells_pos
                self.turn_previous = self.turn_color

            self.change_colour_turn()
            self.picked_checker = None

            pygame.display.update()

    def put_in_place(self):
        """
        Проверка на клик мышкой по уже взятой фишке
        """

        mouse_pos = list(pygame.mouse.get_pos())
        c = list(self.picked_checker.coords)

        return c[0] - 45 < mouse_pos[0] < c[0] + 45 and \
               c[1] - 45 < mouse_pos[1] < c[1] + 45

    def get_empty_cells(self):
        """
        Получает список всехпустых клеток
        """

        self.all_empty_cells = []

        coord = [175, 175]
        count = 1

        for pos in self.BOARD.keys():
            if self.BOARD[pos] == 0:
                self.all_empty_cells.append((pos, tuple(coord)))
            coord[0] += config.CELLS_SIZE
            count += 1

            if count > 6:
                count = 1
                coord[0] = 175
                coord[1] += config.CELLS_SIZE

    def get_cells_pos(self):
        """
        Получить позицию выбранной пустой ячейки (при клике мыши)
        """

        mouse_pos = list(pygame.mouse.get_pos())
        for cells in self.all_empty_cells:
            c = list(list(cells)[1])
            correct_pos = c[0] - 45 < mouse_pos[0] < c[0] + 45 and \
                          c[1] - 45 < mouse_pos[1] < c[1] + 45
 
            if correct_pos:
                return cells

    def get_checker_pos(self):
        """
        Получить позицию выбранной фишки (при клике мыши)
        """

        mouse_pos = list(pygame.mouse.get_pos())

        for checker in self.all_checkers:
            c = list(checker.coords)
            correct_pos = c[0] - 45 < mouse_pos[0] < c[0] + 45 and \
                          c[1] - 45 < mouse_pos[1] < c[1] + 45
            
            if correct_pos:
                return checker

    def change_colour_turn(self):
        """
        Меняет цвет хода
        """
        
        change = {'WHITE': 'BLACK', 'BLACK': 'WHITE'}
        self.turn_color = change[self.turn_color]
        self.check_end_game()

    def check_edge_board(self, checker):
        """
        Проверка фишки у края доски со стороны соперника
        """

        return checker.colour == 'BLACK' and checker.pos[1] == '5' or\
                checker.colour == 'WHITE' and checker.pos[1] == '1'
        
    def find_all_possible_move(self):
        """
        Найти возможные варианты хода
        """

        possible_move = {}
        possible_cuts = {}

        for checker in self.all_checkers:
            if self.check_edge_board(checker):
                continue

            elif checker.colour == self.turn_color:
                near_cells = []  # Соседние клетки
                via_one = []  # Клетки через одну

                near_cells += self._find_left_right(checker.pos, 1)
                near_cells += self._find_up_down(checker.pos, 1)

                via_one += self._find_left_right(checker.pos, 2)
                via_one += self._find_up_down(checker.pos, 2)

                opponent_colour = {'WHITE': 'b', 'BLACK': 'w'}
                opponent = opponent_colour[checker.colour]

                for i in range(len(via_one)):
                    if via_one[i] and near_cells[i] and 0 in via_one[i] and \
                            opponent in near_cells[i]:
                        possible_cuts[checker.pos] = [list(via_one[i])[0],
                                                      list(near_cells[i])[0]]
                
                if not possible_cuts:
                    for i in range(len(near_cells)):
                        if self.turn_color == 'WHITE' and i == 3 or \
                            self.turn_color == 'BLACK' and i == 2:
                            continue

                        elif near_cells[i] and 0 in near_cells[i]:
                            if checker.pos in possible_move.keys():
                                possible_move[checker.pos].append(
                                    list(near_cells[i])[0])
                            else:
                                possible_move[checker.pos] = [list(
                                    near_cells[i])[0]]

        if possible_cuts:
            self.turn_type = 'cuts'
            return possible_cuts
            
        else:
            self.turn_type = 'move'
            return possible_move


    def _find_left_right(self, position, distance):
        """
        Возращает занятость сосденей клетки слева-справа на указанной
        дистанции
        """
        
        coef = -distance
        left_right = [None, None]
        for s in range(2):
            index_char = self.chars_coords.find(position[0]) + coef
            if 0 <= index_char < 6:
                new_position = self.chars_coords[index_char] + position[1]
                left_right[s] = (new_position, self.BOARD[new_position])
            coef = -coef
        
        return left_right
                
    def _find_up_down(self, position, distance):
        """
        Возращает занятость сосденей клетки сверху-снизу на указанной
        дистанции
        """

        coef = -distance
        up_down = [None, None]
        for s in range(2):
            index_int = int(position[1]) + coef
            if 0 < index_int < 6:
                new_position = position[0] + str(index_int)
                up_down[s] = (new_position, self.BOARD[new_position])
            coef = -coef

        return up_down


class Checkers(pygame.sprite.Sprite):
    """
    Класс фишек (шашек)
    """

    def __init__(self, size, pos, coords, colour, filename):
        self.pos = pos
        self.coords = coords
        self.colour = colour

        pygame.sprite.Sprite.__init__(self)
        picture = pygame.image.load(filename).convert_alpha()

        self.image = pygame.transform.scale(picture, (size, size))
        self.rect = self.image.get_rect(center=self.coords)

