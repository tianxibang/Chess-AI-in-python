import sys
import random
# Make sure these imports match your folder structure
from Chess import ChessLogic
from ChessAI import ChessAI

def main():
    # 1. Initialize the board
    logic = ChessLogic()
    ai = ChessAI(logic)
    
    # We maintain the turn color locally
    turn = "white"

    while True:
        try:
            # 2. Read command from GUI
            command_line = sys.stdin.readline()
            if not command_line:
                break
                
            command_line = command_line.strip()
            if not command_line:
                continue

            parts = command_line.split()
            cmd = parts[0]

            # --- UCI HANDSHAKE ---
            if cmd == "uci":
                print("id name PythonChessBot")
                print("id author You")
                print("uciok")
                sys.stdout.flush()

            elif cmd == "isready":
                print("readyok")
                sys.stdout.flush()

            elif cmd == "ucinewgame":
                logic = ChessLogic()
                turn = "white"

            # --- POSITION HANDLING ---
            elif cmd == "position":
                # Example: "position startpos moves e2e4 e7e5"
                if "startpos" in parts:
                    logic = ChessLogic() # Reset board
                    turn = "white"
                
                if "moves" in parts:
                    idx = parts.index("moves")
                    move_list = parts[idx+1:]
                    for move in move_list:
                        # We must generate valid moves to pass to input_move
                        # because input_move checks validity against them.
                        valid_moves = logic.return_possible_moves(turn)
                        try:
                            logic.input_move(move, valid_moves)
                        except Exception:
                            # Ignore invalid moves sent by GUI to prevent crash
                            pass
                        
                        # Flip turn
                        turn = "black" if turn == "white" else "white"

            # --- GO (THINK) ---
            elif cmd == "go":
                # The GUI is asking for a move
                valid_moves = logic.return_possible_moves(turn)
                
                # Check for game over before asking AI
                state = logic.get_game_state(turn)
                if state in ["checkmate", "stalemate"]:
                    # UCI doesn't strictly require sending bestmove if mated, 
                    # but it's good practice to do nothing or resign.
                    pass
                
                best_move = ai.random(turn)
                
                if best_move:
                    # Apply it internally to keep sync (optional but safer)
                    logic.input_move(best_move, valid_moves)
                    turn = "black" if turn == "white" else "white"
                    print(f"bestmove {best_move}")
                else:
                    # No moves? Resign or just send (none)
                    print("bestmove (none)")
                
                sys.stdout.flush()

            elif cmd == "quit":
                break

        except Exception as e:
            # Log errors silently to a file so GUI doesn't crash
            # with open("bot_log.txt", "a") as f: f.write(str(e) + "\n")
            pass

if __name__ == "__main__":
    main()