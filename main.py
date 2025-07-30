
import customtkinter as ctk

class GomokuBoard:
    def __init__(self, canvas, size=19, cell_size=30):
        self.canvas = canvas
        self.size = size
        self.cell_size = cell_size
        self.turn = 0
        self.draw_board()

    def draw_board(self):
        # Draw clickable points at intersections
        def on_point_click(event, row, col):
            # Example: highlight the clicked point
            x = col * self.cell_size + self.cell_size
            y = row * self.cell_size + self.cell_size
            r = 10
            if self.turn % 2 == 0:
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black", width=2)
            else:
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="white", width=2)
            self.turn += 1
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
                r = 3
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
    board_size = 19
    cell_size = 40
    canvas_size = (board_size + 1) * cell_size
    canvas = ctk.CTkCanvas(root, width=canvas_size, height=canvas_size)
    canvas.pack(padx=10, pady=10)
    GomokuBoard(canvas, size=board_size, cell_size=cell_size)
    root.mainloop()

if __name__ == "__main__":
    main()

