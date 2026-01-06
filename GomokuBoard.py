import customtkinter as ctk
from bitboard import play_move, has_five, is_double_three

class GomokuBoard:
    def __init__(self, canvas, turn_label, capture_label, size=19, cell_size=30):
        self.canvas = canvas
        self.turn_label = turn_label
        self.capture_label = capture_label
        self.size = size
        self.cell_size = cell_size
        self.turn = 0
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.bb_X = 0
        self.bb_O = 0
        self.game_over = False
        self.captured_X = 0
        self.captured_O = 0
        self.draw_board()
        self.update_turn_label()
        self.update_capture_label()

    def update_turn_label(self):
        player = "Black" if self.turn % 2 == 0 else "White"
        self.turn_label.configure(text=f"Current turn: {player}")

    def update_capture_label(self):
        self.capture_label.configure(text=f"Captures - Black: {self.captured_X} | White: {self.captured_O}")

    def reset_board(self):
        self.turn = 0
        self.bb_X = 0
        self.bb_O = 0
        self.game_over = False
        self.captured_X = 0
        self.captured_O = 0
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.canvas.delete("all")
        self.draw_board()
        self.update_turn_label()
        self.update_capture_label()

    def draw_board(self):
        # Draw clickable points at intersections
        def on_point_click(event, row, col):
            if self.game_over or self.board[row][col] is not None:
                return
            player = 'X' if self.turn % 2 == 0 else 'O'
            prev_bb_X, prev_bb_O = self.bb_X, self.bb_O
            try:
                self.bb_X, self.bb_O = play_move(self.bb_X, self.bb_O, row, col, player)
            except ValueError as e:
                # Show a brief UI message for illegal moves (e.g., double three)
                self.turn_label.configure(text=f"Illegal move: {e}")
                # Restore the normal turn label after a short delay
                self.canvas.after(1500, self.update_turn_label)
                return
            x = col * self.cell_size + self.cell_size
            y = row * self.cell_size + self.cell_size
            r = 15
            color = "black" if player == 'X' else "white"
            stone_id = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color, width=2)
            self.board[row][col] = {"player": player, "id": stone_id}

            captured_bits = (prev_bb_O & ~self.bb_O) if player == 'X' else (prev_bb_X & ~self.bb_X)
            captured_count = captured_bits.bit_count()
            while captured_bits:
                lsb = captured_bits & -captured_bits
                idx = lsb.bit_length() - 1
                cap_row, cap_col = divmod(idx, self.size)
                if self.board[cap_row][cap_col]:
                    self.canvas.delete(self.board[cap_row][cap_col]["id"])
                    self.board[cap_row][cap_col] = None
                captured_bits ^= lsb
            if captured_count:
                if player == 'X':
                    self.captured_X += captured_count
                else:
                    self.captured_O += captured_count
                self.update_capture_label()
            if ((player == 'X' and has_five(self.bb_X)) or (player == 'O' and has_five(self.bb_O))
                or (self.captured_X >= 10) or (self.captured_O >= 10)):
                winner = 'Black' if (player == 'X' and has_five(self.bb_X)) or self.captured_X >= 10 else 'White'
                self.turn_label.configure(text=f"{winner} wins!")
                self.game_over = True
            else:
                self.turn += 1
                self.update_turn_label()
            print(f"Clicked: {chr(ord('A')+row)}{col+1}")

        # Draw board squares
        for row in range(self.size):
            for col in range(self.size):
                x1 = col * self.cell_size + self.cell_size
                y1 = row * self.cell_size + self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "#986B41"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)

        for row in range(1, self.size):
            for col in range(1, self.size):
                x = col * self.cell_size + self.cell_size
                y = row * self.cell_size + self.cell_size
                r = 4.5
                point = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black", width=1)
                # Bind click event to each point
                def handler(event, row=row, col=col):
                    on_point_click(event, row, col)
                self.canvas.tag_bind(point, '<Button-1>', handler)

        # Draw row labels (A-S)
        for row in range(self.size):
            label = chr(ord('A') + row)
            x = self.cell_size // 2
            y = (row + 1) * self.cell_size + self.cell_size // 2
            self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"))

        # Draw column labels (1-19)
        for col in range(self.size):
            label = str(col + 1)
            x = (col + 1) * self.cell_size + self.cell_size // 2
            y = self.cell_size // 2
            self.canvas.create_text(x, y, text=label, font=("Arial", 14, "bold"))

def main():
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title("Gomoku 19x19 Board")
    root.resizable(False, False)
    board_size = 19
    cell_size = 40
    canvas_size = (board_size + 1) * cell_size

    frame = ctk.CTkFrame(root)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    canvas = ctk.CTkCanvas(frame, width=canvas_size, height=canvas_size)
    canvas.pack(side="left", padx=10, pady=10)

    turn_label = ctk.CTkLabel(frame, text="", font=("Arial", 16))
    turn_label.pack(side="bottom", padx=10, pady=4)

    capture_label = ctk.CTkLabel(frame, text="", font=("Arial", 14))
    capture_label.pack(side="bottom", padx=10, pady=4)

    board = GomokuBoard(canvas, turn_label, capture_label, size=board_size, cell_size=cell_size)

    reset_btn = ctk.CTkButton(frame, text="Reset Game", command=board.reset_board)
    reset_btn.pack(side="right", padx=20, pady=10, fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()

