import random


class Bot:
    """
    Класс работы бота (игрок-комптютер)
    """

    def __init__(self):
        self.choiced_checker = None
        self.choiced_checker_pos = None
        
    def _choose_move(self, all_possible, turn_type):
        """
        Выбирает ход
        """
        
        if turn_type == 'cuts':
            return all_possible[self.choiced_checker][0]
        else:
            move = random.choice(all_possible[self.choiced_checker])
            return move

    def _choose_checker(self, all_possible, all_checkers):
        """
        Выбирает фишку
        """

        keys_list = []
        
        for keys in all_possible.keys():
            keys_list.append(keys)
        
        self.choiced_checker = random.choice(keys_list)

        for checker in all_checkers:
            if checker.pos == self.choiced_checker:
                self.choiced_checker_pos = all_possible[checker.pos]
                return checker
