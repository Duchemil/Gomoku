import customtkinter as ctk

class GomokuBoard:
    def __init__(self, canvas, turn_label, size=19, cell_size=30):
        self.canvas = canvas
        self.turn_label = turn_label
        self.size = size
        self.cell_size = cell_size
        self.turn = 0
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.draw_board()
        self.update_turn_label()

    def update_turn_label(self):
        player = "Black" if self.turn % 2 == 0 else "White"
        self.turn_label.configure(text=f"Current turn: {player}")

    def is_win(self, row, col):
        """ Check for winning condition by checking rows, columns, and diagonals with a total of 5 in a row. """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Check in the positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == self.board[row][col]:
                count += 1
                r += dr
                c += dc
            # Check in the negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == self.board[row][col]:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False
    
    def reset_board(self):
        self.turn = 0
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.canvas.delete("all")
        self.draw_board()
        self.update_turn_label()

    def draw_board(self):
        # Draw clickable points at intersections
        def on_point_click(event, row, col):
            x = col * self.cell_size + self.cell_size
            y = row * self.cell_size + self.cell_size
            r = 15
            if self.board[row][col] is not None:
                return  # Ignore if already played
            if self.turn % 2 == 0:
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black", width=2)
                self.board[row][col] = '1'
            else:
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="white", width=2)
                self.board[row][col] = '2'
            if self.is_win(row, col):
                self.turn_label.configure(text=f"{'Black' if self.board[row][col]=='1' else 'White'} wins!")
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
    turn_label.pack(side="bottom", padx=10, pady=10)

    board = GomokuBoard(canvas, turn_label, size=board_size, cell_size=cell_size)

    reset_btn = ctk.CTkButton(frame, text="Reset Game", command=board.reset_board)
    reset_btn.pack(side="right", padx=20, pady=10, fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()

