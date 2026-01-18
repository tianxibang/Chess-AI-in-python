import time
from ChessAI import ChessAI
class ChessLogic:
    global FILE_A
    global FILE_H
    global FILE_B
    global FILE_G
    global RANK_TWO
    global RANK_SEVEN
    global RANK_ONE
    global RANK_EIGHT
    FILE_A = 0x8080808080808080
    FILE_H = 0x0101010101010101
    FILE_B = 0b01000000_01000000_01000000_01000000_01000000_01000000_01000000_01000000
    FILE_G = 0b00000010_00000010_00000010_00000010_00000010_00000010_00000010_00000010

    RANK_ONE = 0b11111111
    RANK_TWO = 0b11111111_00000000
    RANK_SEVEN = 0b11111111_00000000_00000000_00000000_00000000_00000000_00000000
    RANK_EIGHT = 0b11111111_00000000_00000000_00000000_00000000_00000000_00000000_00000000

    def __init__(self):
        self.current_board = self.starting_pos()
        self.current_move = 0
        
        # CREATE THE LOOKUP TABLE
        self.notation_map = {}
        files = "abcdefgh"
        for r in range(1, 9):
            for f_idx, f_char in enumerate(files):
                # Calculate the bitmask once on startup
                shift = ((r - 1) * 8) + (7 - f_idx)
                self.notation_map[f_char + str(r)] = 1 << shift

    # Replace the old function with this:
    def turn_notation_binary(self, notation):
        return self.notation_map[notation]

    def starting_pos(self):
        #black lower case, white upper case
        starting_board_dict ={
            "r":["a8","h8"], "n":["b8","g8"], "b":["c8", "f8"], "k":["e8"], "q":["d8"],
            "p":["a7","b7","c7","d7", "f7","g7","h7"],
            "R":["a1","h1"], "N":["b1","g1"], "B":["c1", "f1"], "K":["e1"], "Q":["d1"],
            "P":["a2","b2","c2","d2","e7","f2","g2","h2"],
            
        }        
        return starting_board_dict

    def bitboard_to_square(sefl, bitboard):
        if isinstance(bitboard, tuple):
            bitboard = bitboard[0]
        index = bitboard.bit_length() - 1
        file = chr(ord('a') + (7 - (index % 8)))  # flip horizontal
        rank = str((index // 8) + 1)             # rank 1 = bottom
        return file + rank

    def make_bitboard(self, piece):
        self.bitboard = 0
        position_list = self.current_board[piece]
        for position in position_list:
            self.bitboard = self.bitboard | self.turn_notation_binary(position)
        return self.bitboard
    
    def make_bitboard_of_all_pieces_by_player(self, player):
        white_bitboard = self.make_bitboard("P") | self.make_bitboard("R") | self.make_bitboard("N") | self.make_bitboard("B") | self.make_bitboard("Q") | self.make_bitboard("K")
        black_bitboard = self.make_bitboard("p") | self.make_bitboard("r") | self.make_bitboard("n") | self.make_bitboard("b") | self.make_bitboard("q") | self.make_bitboard("k")
        if player == "white":
            return white_bitboard
        elif player == "black":
            return black_bitboard
        else:
            return white_bitboard | black_bitboard

    def is_checkmate(self):
        return False
    
    def is_check(self, king_bitboard, player):
        return
    

    def check_block(self, test_bitmap, player, white_occ, black_occ):
        # Determine "own" pieces based on player
        own_pieces = white_occ if player == "white" else black_occ
        both_pieces = white_occ | black_occ

        # Test if out of bounds below (0) or above (board limit)
        if test_bitmap == 0 or test_bitmap >= 18446744073709551616:
            return "break"
        # Test if blocked by own piece (can't take)
        elif (test_bitmap & own_pieces) > 0:
            return "break"
        # Test if blocked by enemy piece (can take)
        elif (test_bitmap & both_pieces) > 0:
            return test_bitmap
        # Square is empty
        else:
            return
        
    def return_king_moves(self, move_piece_bitboard, player, white_occ, black_occ):
        list_of_moves = []
        directions = (
            (-8, None), (8, None), (-1, FILE_H), (1, FILE_A),
            (7, FILE_A), (9, FILE_H), (-7, FILE_A), (-9, FILE_H),
        )

        for shift, edge_mask in directions:
            test = move_piece_bitboard
            if edge_mask and (test & edge_mask):
                continue
            test = (test << shift) if shift > 0 else (test >> -shift)

            # Pass occupancies to check_block
            result = self.check_block(test, player, white_occ, black_occ)
            
            if result == "break" or self.is_check(): # is_check() is still slow, but that's a separate fix
                continue
            elif isinstance(result, int):
                list_of_moves.append(result)
            else:
                list_of_moves.append(test)

        return (move_piece_bitboard, tuple(list_of_moves))

    def return_knight_moves(self, move_piece_bitboard, player, white_occ, black_occ):
        list_of_moves = []
        directions = (
            (15, FILE_A), (-15, FILE_A), (10, FILE_A|FILE_B), (-6, FILE_A|FILE_B),
            (17, FILE_H), (-17, FILE_H), (6, FILE_H|FILE_G), (-10, FILE_H|FILE_G)
        )

        for shift, edge_mask in directions:
            test = move_piece_bitboard
            if edge_mask and (test & edge_mask):
                continue
            test = (test << shift) if shift > 0 else (test >> -shift)

            # Pass occupancies to check_block
            result = self.check_block(test, player, white_occ, black_occ)
            
            if result == "break":
                continue
            elif isinstance(result, int):
                list_of_moves.append(result)
            else:
                list_of_moves.append(test)

        return (move_piece_bitboard, tuple(list_of_moves))

    def return_straight_moves(self, move_piece_bitboard, player, white_occ, black_occ):
        list_of_moves = []
        directions = ((-8, None), (8, None), (-1, FILE_H), (1, FILE_A))

        for shift, edge_mask in directions:
            test = move_piece_bitboard
            while True:
                if edge_mask and (test & edge_mask):
                    break
                test = (test << shift) if shift > 0 else (test >> -shift)

                # Pass occupancies to check_block
                result = self.check_block(test, player, white_occ, black_occ)

                if result == "break":
                    break
                elif isinstance(result, int):
                    list_of_moves.append(result)
                    break
                else:
                    list_of_moves.append(test)

        return (move_piece_bitboard, tuple(list_of_moves))
      
    def return_diagonal_moves(self, move_piece_bitboard, player, white_occ, black_occ):
        list_of_moves = []
        directions = ((7, FILE_A), (9, FILE_H), (-7, FILE_A), (-9, FILE_H))

        for shift, edge_mask in directions:
            test = move_piece_bitboard
            while True:
                if edge_mask and (test & edge_mask):
                    break
                test = (test << shift) if shift > 0 else (test >> -shift)
                # Pass occupancies to check_block
                result = self.check_block(test, player, white_occ, black_occ)

                if result == "break":
                    break
                elif isinstance(result, int):
                    list_of_moves.append(result)
                    break
                else:
                    list_of_moves.append(test)

        return (move_piece_bitboard, tuple(list_of_moves))

    def return_pawn_moves(self, move_piece_bitboard, player, white_occ, black_occ):
        list_of_moves = []
        both_occ = white_occ | black_occ
        
        if player == "white":
            # 1. Forward Move (1 square)
            test = move_piece_bitboard << 8
            if (test != 0 and test < 18446744073709551616) and not (test & both_occ):
                # Promotion check
                if test & RANK_EIGHT != 0:
                    list_of_moves.append((test, "promote"))
                else:
                    list_of_moves.append(test)
                
                # 2. Double Forward Move (from Rank 2)
                if move_piece_bitboard & RANK_TWO:
                    test_double = move_piece_bitboard << 16
                    if not (test_double & both_occ):
                        list_of_moves.append(test_double)

                
            # 3. Capture Up-Left (Shift 9)
            # Must NOT be on File A to capture left
            if not (move_piece_bitboard & FILE_A):
                capture_left = move_piece_bitboard << 9
                if capture_left & black_occ:
                    if capture_left & RANK_EIGHT != 0:
                        list_of_moves.append((capture_left, "promote"))
                    else:
                        list_of_moves.append(capture_left)
            
            # 4. Capture Up-Right (Shift 7)
            # Must NOT be on File H to capture right
            if not (move_piece_bitboard & FILE_H):
                capture_right = move_piece_bitboard << 7
                if capture_right & black_occ:
                    if capture_right & RANK_EIGHT != 0:
                        list_of_moves.append((capture_right, "promote"))
                    else:
                        list_of_moves.append(capture_right)
        else:
            # 1. Forward Move (1 square)
            test = move_piece_bitboard >> 8
            if (test != 0 and test < 18446744073709551616) and not (test & both_occ):
                # Promotion check
                if test & RANK_EIGHT != 0:
                    list_of_moves.append((test, "promote"))
                else:
                    list_of_moves.append(test)
                
                # 2. Double Forward Move (from Rank 7)
                if move_piece_bitboard & RANK_SEVEN:
                    test_double = move_piece_bitboard >> 16
                    if not (test_double & both_occ):
                        list_of_moves.append(test_double)

            # 3. Capture Up-Left (Shift 9)
            # Must NOT be on File A to capture left
            if not (move_piece_bitboard & FILE_A):
                capture_left = move_piece_bitboard >> 9
                if capture_left & white_occ:
                    if capture_left & RANK_ONE != 0:
                        list_of_moves.append((capture_left, "promote"))
                    else:
                        list_of_moves.append(capture_left)
            
            # 4. Capture Up-Right (Shift 7)
            # Must NOT be on File H to capture right
            if not (move_piece_bitboard & FILE_H):
                capture_right = move_piece_bitboard >> 7
                if capture_right & white_occ:
                    if capture_left & RANK_ONE != 0:
                        list_of_moves.append((capture_right, "promote"))
                    else:
                        list_of_moves.append(capture_right)

        return (move_piece_bitboard, tuple(list_of_moves))
    
    def get_single_piece_bitboard(self, bitboard):
        single_piece_bitboard_list = []
        
        while bitboard:
            # 1. Isolate the rightmost bit (piece)
            lsb = bitboard & -bitboard
            single_piece_bitboard_list.append(lsb)
            
            # 2. Remove that bit and continue
            bitboard ^= lsb
            
        return single_piece_bitboard_list

    def return_possible_moves(self, player):
        # 1. OPTIMIZATION: Calculate Occupancies ONCE
        white_occ = self.make_bitboard_of_all_pieces_by_player("white")
        black_occ = self.make_bitboard_of_all_pieces_by_player("black")

        # 2. Pass these into the move functions
        Q_moves_notation = list()
        for Qpos in self.get_single_piece_bitboard(self.make_bitboard("Q" if player == "white" else "q")):
            diag = (self.return_diagonal_moves(Qpos, player, white_occ, black_occ))
            stra = (self.return_straight_moves(Qpos, player, white_occ, black_occ))
            combined = diag[0], diag[1] + stra[1]
            Q_moves_notation.append(combined)

        R_moves_notation = list()
        for Rpos in self.get_single_piece_bitboard(self.make_bitboard("R" if player == "white" else "r")):
            R_moves_notation.append(self.return_straight_moves(Rpos, player, white_occ, black_occ))

        B_moves_notation = list()
        for Rpos in self.get_single_piece_bitboard(self.make_bitboard("B" if player == "white" else "b")):
            B_moves_notation.append(self.return_diagonal_moves(Rpos, player, white_occ, black_occ))

        P_moves_notation = list()
        for Ppos in self.get_single_piece_bitboard(self.make_bitboard("P" if player == "white" else "p")):
            pawn = self.return_pawn_moves(Ppos, player, white_occ, black_occ)
            P_moves_notation.append(pawn)

        N_moves_notation = list()
        for Npos in self.get_single_piece_bitboard(self.make_bitboard("N" if player == "white" else "n")):
            N_moves_notation.append(self.return_knight_moves(Npos, player, white_occ, black_occ))

        K_moves_notation = list()

        return Q_moves_notation, R_moves_notation, B_moves_notation, P_moves_notation, N_moves_notation, K_moves_notation
    
    def update_position(self, move):
        print(f"Updating position: {move}")
        original_pos = move[0:2]
        new_pos = move[2:4]
        promotion = move[4:5]
        print("promotion value:", promotion)
        for piece in self.current_board:
            if new_pos in self.current_board.get(piece):
                print("Removing Piece:", piece)
                self.current_board[piece].remove(new_pos)
            if promotion and original_pos in self.current_board.get(piece):
                print("Moving and Promoting")
                print(original_pos)
                if self.current_move+1 % 2 == 1:
                    # white
                    self.current_board[piece].remove(original_pos)
                    self.current_board[promotion.upper()].append(new_pos)
                else:
                    # black
                    self.current_board[piece].remove(original_pos)
                    self.current_board[promotion.lower()].append(new_pos)
            elif original_pos in self.current_board.get(piece):
                print("Piece found:", piece)
                self.current_board[piece].remove(original_pos)
                self.current_board[piece].append(new_pos)
        self.current_move += 1
        return 
    
    def input_move(self, move, moveset):
        original_pos = move[:2]
        new_pos = move[2:4]
        promotion = move[4:5]
        original_pos_bit = self.turn_notation_binary(original_pos)
        new_pos_bit = self.turn_notation_binary(new_pos)
        for pieces in moveset:
            for piece in pieces:
                if original_pos_bit == piece[0]:
                    for destination in piece[1]:
                        if new_pos_bit == destination[0] if promotion else destination:
                            self.update_position(move)
                            return
        raise Exception("Invalid move")

    def print_possible_moves(self, moveset):
        i = 0
        for piece in moveset:
            if i == 0:
                print("Q")
            elif i == 1:
                print("R")
            elif i == 2:
                print("B")
            elif i == 3:
                print("P")
            elif i == 4:
                print("N",)
            i += 1
            for move in piece:
                for newpos in move[1]:
                    print(self.bitboard_to_square(move[0]), end="")
                    print(self.bitboard_to_square(newpos), "promote" if isinstance(newpos, tuple) else "", end=", ")
            print("\n")



    def print_board_from_dict(self, board_dict):
        # 1. Create an empty 8x8 grid represented by dots
        # We use a list of lists. Row 0 is Rank 8 (top), Row 7 is Rank 1 (bottom)
        grid = [['.' for _ in range(8)] for _ in range(8)]

        # 2. Populate the grid
        for piece_char, positions in board_dict.items():
            for pos in positions:
                # Convert file (a-h) to col (0-7)
                file_char = pos[0]
                col = ord(file_char) - ord('a')

                # Convert rank (1-8) to row (0-7)
                # Rank 8 is row 0, Rank 1 is row 7
                rank_num = int(pos[1])
                row = 8 - rank_num

                grid[row][col] = piece_char

        # 3. Print the board with labels
        print("\n  a b c d e f g h")
        print("  ---------------")
        for i, row in enumerate(grid):
            # Print Rank number (8 down to 1) on the left
            rank_label = 8 - i
            print(f"{rank_label}|{' '.join(row)}|{rank_label}")
        print("  ---------------")
        print("  a b c d e f g h\n")


    def run(self):
        if __name__ == "__main__":
            ai = ChessAI(self)
            while not self.is_checkmate():

                
                # White
                start_time = time.time()
                self.print_board_from_dict(self.current_board)
                res = self.return_possible_moves("white")
                end_time = time.time()
                duration = end_time - start_time
                self.print_possible_moves(res)
                print(f"\nTime taken: {duration:.4f} seconds")
                move = str(input(f"Move: {self.current_move} What's your move?\n"))
                self.input_move(move, res)
                

                # Black
                start_time = time.time()
                res = self.return_possible_moves("black")
                end_time = time.time()
                duration = end_time - start_time
                print(f"\nTime taken: {duration:.4f} seconds")
                move = ai.random()
                print(move)
                self.input_move(move, res)


logic = ChessLogic()
logic.run()   