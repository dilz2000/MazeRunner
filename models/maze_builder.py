from models.maze_image import MazeL


def build_maze_from_detected_grid(h_grid_lines, v_grid_lines, processed_maze):
    """
    Constructs a structured maze from detected grid lines and the processed maze image.
    """
    maze = MazeL(h_grid_lines, v_grid_lines, processed_maze)
    return maze
