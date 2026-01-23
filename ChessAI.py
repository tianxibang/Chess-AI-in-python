import random
class ChessAI:
    def __init__(self, board_logic):
        self.board = board_logic

    def random(self, player):
        moves = self.board.return_possible_moves(player)
        moves_notation_list = list()
        
        for piece_moves in moves:
            for move_data in piece_moves:
                # move_data is typically [origin_bitboard, [dest_bitboards...]]
                origin_bit = move_data[0]
                destinations = move_data[1]
                
                for newpos in destinations:
                    # Check for promotion tuple: (bitboard, "promote")
                    if isinstance(newpos, tuple):
                        dest_bit = newpos[0]
                        # For a random bot, we'll always promote to Queen ('q')
                        originalpos = str(self.board.bitboard_to_square(origin_bit))
                        dest_pos = str(self.board.bitboard_to_square(dest_bit))
                        move_notation = originalpos + dest_pos + "q"
                        moves_notation_list.append(move_notation)
                    else:
                        originalpos = str(self.board.bitboard_to_square(origin_bit))
                        move_notation = originalpos + str(self.board.bitboard_to_square(newpos))
                        moves_notation_list.append(move_notation)

        if not moves_notation_list:
            return None # No moves available
            
        return random.choice(moves_notation_list)