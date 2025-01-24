# main.py

import tkinter as tk
from controllers.maze_app import MazeApp


def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
