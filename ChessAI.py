import random
class ChessAI:
    def __init__(self, board_logic):
        self.board = board_logic

    def random(self, player):
        moves = self.board.return_possible_moves(player)
        moves_notation_list = list()
        for piece in moves:
            for moves in piece:
                    for newpos in moves[1]:
                         originalpos = str(self.board.bitboard_to_square(moves[0]))
                         move_notation = originalpos + str(self.board.bitboard_to_square(newpos))
                         moves_notation_list.append(move_notation)
                         choice = random.choice(moves_notation_list)
        return choice