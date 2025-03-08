import cv2
import numpy as np

def preprocess_maze(image):
    """Preprocess the maze and fill small gaps using morphological operations."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Fill small gaps using morphological closing
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    return cleaned


def preprocess_image(image_path):
    """Load and preprocess the maze image with improved line detection."""
    # Load image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Edge detection using Canny (we'll keep this as initial step)
    edges = cv2.Canny(blurred, 50, 150)

    # Apply Hough Line Transform to detect straight lines
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180,
                            threshold=50, minLineLength=30, maxLineGap=10)

    # Create a blank image to draw the detected lines
    line_image = np.zeros_like(image)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), 255, 2)

    # Combine the original edges with the detected lines
    combined = cv2.bitwise_or(edges, line_image)

    return image, combined  # Return original image and the combined edge+line image


def adjust_grid_lines_to_maze(h_grid_lines, v_grid_lines, processed_maze):
    """
    Adjusts detected grid lines so that they align with the strongest detected walls in the processed_maze.
    """
    adjusted_h_lines = []
    adjusted_v_lines = []

    def find_nearest_wall(y_or_x, axis="horizontal", search_range=5):
        """
        Finds the closest strong edge (wall) near the detected grid line.
        axis can be "horizontal" (y-coordinates) or "vertical" (x-coordinates).
        """
        if axis == "horizontal":
            strip = processed_maze[max(0, y_or_x - search_range): min(y_or_x + search_range, processed_maze.shape[0]), :]
            summed_values = np.sum(strip, axis=1)  # Sum along rows to find strong horizontal lines
        else:
            strip = processed_maze[:, max(0, y_or_x - search_range): min(y_or_x + search_range, processed_maze.shape[1])]
            summed_values = np.sum(strip, axis=0)  # Sum along columns to find strong vertical lines

        strongest_idx = np.argmax(summed_values)
        return max(0, y_or_x - search_range + strongest_idx)

    # Adjust horizontal lines
    for y in h_grid_lines:
        adjusted_h_lines.append(find_nearest_wall(y, axis="horizontal"))

    # Adjust vertical lines
    for x in v_grid_lines:
        adjusted_v_lines.append(find_nearest_wall(x, axis="vertical"))

    return adjusted_h_lines, adjusted_v_lines


def extract_maze_structure(edges, original_image=None):
    """
    Use Hough Transform and morphological operations to clean up the maze structure.
    """
    # Apply Hough Line Transform to find straight lines
    rho = 1  # Distance resolution in pixels
    theta = np.pi / 180  # Angular resolution in radians
    threshold = 50  # Minimum number of votes
    min_line_length = 30  # Minimum line length
    max_line_gap = 10  # Maximum allowed gap between line segments

    lines = cv2.HoughLinesP(edges, rho, theta, threshold,
                            minLineLength=min_line_length,
                            maxLineGap=max_line_gap)

    # Create an empty mask to draw detected lines
    line_mask = np.zeros_like(edges)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_mask, (x1, y1), (x2, y2), 255, 2)

    # Combine detected lines with original edges
    combined = cv2.bitwise_or(edges, line_mask)

    # Apply morphological operations to clean up and connect broken lines
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(combined, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)

    return eroded


def build_grid_from_hough_lines(binary_image):
    """
    Build a grid structure directly from Hough lines.
    This can be more reliable than relying on edge detection alone.
    """
    h, w = binary_image.shape

    # Apply Hough Transform with probabilistic implementation
    lines = cv2.HoughLinesP(binary_image, rho=1, theta=np.pi / 180,
                            threshold=50, minLineLength=max(h, w) // 20,
                            maxLineGap=max(h, w) // 20)

    # Create separate images for horizontal and vertical lines
    h_line_img = np.zeros_like(binary_image)
    v_line_img = np.zeros_like(binary_image)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx, dy = abs(x2 - x1), abs(y2 - y1)

            # Horizontal line
            if dy < dx / 3:  # Angle threshold for horizontal
                cv2.line(h_line_img, (x1, y1), (x2, y2), 255, 1)
            # Vertical line
            elif dx < dy / 3:  # Angle threshold for vertical
                cv2.line(v_line_img, (x1, y1), (x2, y2), 255, 1)

    # Extract horizontal and vertical line positions
    h_grid_lines = []
    v_grid_lines = []

    # For horizontal lines, scan each row and find where lines are present
    for y in range(h):
        if np.sum(h_line_img[y, :]) > w / 10:  # If significant number of pixels are white
            h_grid_lines.append(y)

    # For vertical lines, scan each column and find where lines are present
    for x in range(w):
        if np.sum(v_line_img[:, x]) > h / 10:  # If significant number of pixels are white
            v_grid_lines.append(x)

    # Group nearby lines to avoid duplicates
    h_grid_lines = group_nearby_lines(h_grid_lines)
    v_grid_lines = group_nearby_lines(v_grid_lines)

    return h_grid_lines, v_grid_lines, h_line_img, v_line_img

def detect_grid_lines(binary_image):
    """
    Detect grid lines using Hough Transform to handle broken lines.
    Returns sorted lists of horizontal and vertical grid lines.
    """
    h, w = binary_image.shape

    # Apply Hough Line Transform to find straight lines
    lines = cv2.HoughLinesP(binary_image, rho=1, theta=np.pi / 180,
                            threshold=50, minLineLength=max(h, w) // 8,
                            maxLineGap=max(h, w) // 16)

    h_lines = []  # Store horizontal lines (y-coordinates)
    v_lines = []  # Store vertical lines (x-coordinates)

    h_line_img = np.zeros_like(binary_image)
    v_line_img = np.zeros_like(binary_image)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate line angle to determine if horizontal or vertical
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            # Horizontal line (angle close to 0 or 180 degrees)
            if angle < 20 or angle > 160:
                # Use the average y-coordinate
                avg_y = (y1 + y2) // 2
                h_lines.append(avg_y)
                cv2.line(h_line_img, (x1, y1), (x2, y2), 255, 2)

            # Vertical line (angle close to 90 degrees)
            elif 70 < angle < 110:
                # Use the average x-coordinate
                avg_x = (x1 + x2) // 2
                v_lines.append(avg_x)
                cv2.line(v_line_img, (x1, y1), (x2, y2), 255, 2)

    # Group nearby lines to avoid duplicates
    h_lines = group_nearby_lines(h_lines)
    v_lines = group_nearby_lines(v_lines)

    # Ensure we have grid lines even if detection is poor
    if len(h_lines) < 2:
        h_lines = [0, h - 1]  # Fallback to image boundaries
    if len(v_lines) < 2:
        v_lines = [0, w - 1]  # Fallback to image boundaries

    # Debug visualization if needed
    # cv2.imshow("Horizontal Lines", h_line_img)
    # cv2.imshow("Vertical Lines", v_line_img)
    # cv2.waitKey(1)

    return h_lines, v_lines


def group_nearby_lines(lines, threshold=10):
    """Group lines that are close to each other to remove duplicates."""
    if not lines:
        return []

    lines.sort()
    grouped_lines = [lines[0]]

    for i in range(1, len(lines)):
        if abs(lines[i] - grouped_lines[-1]) > threshold:
            grouped_lines.append(lines[i])

    return grouped_lines

def visualize_detected_grid(image, h_grid_lines, v_grid_lines,processed_maze):
    """Draw detected grid lines on the image for debugging."""
    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for y in h_grid_lines:
        cv2.line(image_color, (0, y), (image.shape[1] - 1, y), (255, 0, 0), 1)  # Blue Horizontal Lines

    for x in v_grid_lines:
        cv2.line(image_color, (x, 0), (x, image.shape[0] - 1), (0, 255, 0), 1)  # Green Vertical Lines

    wall_mask = processed_maze > 0
    image_color[wall_mask] = (0, 0, 255)

    cv2.imshow("Detected Grid", image_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def find_openings_in_outer_walls(image, processed_maze, h_grid_lines, v_grid_lines):
    """Find openings (discontinuities) in the outermost walls."""
    h, w = processed_maze.shape

    # Identify outermost grid lines
    if not h_grid_lines or not v_grid_lines:
        return []

    top_line = min(h_grid_lines)
    bottom_line = max(h_grid_lines)
    left_line = min(v_grid_lines)
    right_line = max(v_grid_lines)

    # Create a mask of the outermost walls
    outer_wall_mask = np.zeros_like(processed_maze)

    # Mark horizontal walls
    outer_wall_mask[top_line, left_line:right_line + 1] = processed_maze[top_line, left_line:right_line + 1]
    outer_wall_mask[bottom_line, left_line:right_line + 1] = processed_maze[bottom_line, left_line:right_line + 1]

    # Mark vertical walls
    outer_wall_mask[top_line:bottom_line + 1, left_line] = processed_maze[top_line:bottom_line + 1, left_line]
    outer_wall_mask[top_line:bottom_line + 1, right_line] = processed_maze[top_line:bottom_line + 1, right_line]

    # Create a complete perimeter mask (what the wall should look like if complete)
    complete_wall_mask = np.zeros_like(processed_maze)
    complete_wall_mask[top_line, left_line:right_line + 1] = 255
    complete_wall_mask[bottom_line, left_line:right_line + 1] = 255
    complete_wall_mask[top_line:bottom_line + 1, left_line] = 255
    complete_wall_mask[top_line:bottom_line + 1, right_line] = 255

    # Find the difference (where walls should be but aren't)
    difference = complete_wall_mask - outer_wall_mask

    # Find openings (connected regions in the difference mask)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(difference)

    # Filter out small components (noise)
    min_size = 5  # Minimum number of pixels to be considered an opening
    openings = []

    for i in range(1, num_labels):  # Skip the background label 0
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            # Get the coordinates of this opening
            opening_mask = (labels == i)

            # Determine if horizontal or vertical opening
            y_coords, x_coords = np.where(opening_mask)

            # Check if opening is on horizontal or vertical wall
            is_horizontal = np.any(y_coords == top_line) or np.any(y_coords == bottom_line)
            is_vertical = np.any(x_coords == left_line) or np.any(x_coords == right_line)

            # Add to list with type and coordinates
            if is_horizontal:
                y = top_line if np.any(y_coords == top_line) else bottom_line
                x_min, x_max = np.min(x_coords), np.max(x_coords)
                openings.append(("horizontal", y, x_min, x_max))
            elif is_vertical:
                x = left_line if np.any(x_coords == left_line) else right_line
                y_min, y_max = np.min(y_coords), np.max(y_coords)
                openings.append(("vertical", x, y_min, y_max))

    return openings


def determine_cell_from_opening(opening, h_grid_lines, v_grid_lines):
    """
    Determine the exact cell adjacent to an opening.
    The cell is a square with the red opening line as one of its boundaries.
    """
    opening_type, *coords = opening

    if opening_type == "horizontal":
        y, x_min, x_max = coords
        opening_length = x_max - x_min
        opening_center = (x_min + x_max) // 2

        # Determine if the opening is on the top or bottom wall
        is_top = y == min(h_grid_lines)

        if is_top:
            # Opening is on top wall, cell is directly below
            cell_top = y
            cell_bottom = y + opening_length
            cell_left = x_min
            cell_right = x_max
        else:
            # Opening is on bottom wall, cell is directly above
            cell_bottom = y
            cell_top = y - opening_length
            cell_left = x_min
            cell_right = x_max

    elif opening_type == "vertical":
        x, y_min, y_max = coords
        opening_length = y_max - y_min
        opening_center = (y_min + y_max) // 2

        # Determine if the opening is on the left or right wall
        is_left = x == min(v_grid_lines)

        if is_left:
            # Opening is on left wall, cell is directly to the right
            cell_left = x
            cell_right = x + opening_length
            cell_top = y_min
            cell_bottom = y_max
        else:
            # Opening is on right wall, cell is directly to the left
            cell_right = x
            cell_left = x - opening_length
            cell_top = y_min
            cell_bottom = y_max

    return (cell_top, cell_left, cell_bottom, cell_right)


def estimate_wall_thickness(processed_maze):
    """Estimate the average wall thickness in the maze."""
    # Find all wall pixels
    wall_pixels = np.where(processed_maze > 0)

    if len(wall_pixels[0]) == 0:
        return 3  # Default value if no walls detected

    # Use horizontal runs of wall pixels to estimate thickness
    thickness_counts = []
    for row in range(processed_maze.shape[0]):
        row_pixels = processed_maze[row, :]
        runs = np.where(np.diff(np.concatenate(([0], row_pixels > 0, [0]))) != 0)[0]

        if len(runs) >= 2:
            for i in range(0, len(runs) - 1, 2):
                if i + 1 < len(runs):
                    thickness = runs[i + 1] - runs[i]
                    if 1 < thickness < 20:  # Filter out unreasonable values
                        thickness_counts.append(thickness)

    if thickness_counts:
        # Use median to avoid outliers
        return int(np.median(thickness_counts))
    else:
        return 3  # Default value if estimation fails


def extract_clean_maze(image, processed_maze, h_grid_lines, v_grid_lines, openings, nearest_cells):
    """
    Extract a clean representation of the maze with black walls and red entry/exit cells.
    Adjusts alignment issues and creates a clean binary maze.
    """
    h, w = image.shape

    # Create a blank white canvas for the clean maze
    clean_maze = np.ones((h, w, 3), dtype=np.uint8) * 255

    # Estimate wall thickness
    wall_thickness = estimate_wall_thickness(processed_maze)

    # Get wall mask
    wall_mask = processed_maze > 0

    # Draw all walls in black
    clean_maze[wall_mask] = (0, 0, 0)  # Black walls

    # Refine the nearest cells for better alignment
    refined_cells = []
    for opening, (cell_top, cell_left, cell_bottom, cell_right) in zip(openings, nearest_cells):
        opening_type, *coords = opening

        # Calculate the half thickness for adjustment
        half_thickness = max(1, wall_thickness // 2)

        # Adjust cell boundaries for better alignment based on wall thickness
        if opening_type == "horizontal":
            y, x_min, x_max = coords
            cell_width = x_max - x_min

            if y == min(h_grid_lines):  # Top wall opening
                # Adjust top boundary to account for wall thickness
                top_adj = y + half_thickness
                # Make cell square shaped
                bottom_adj = top_adj + cell_width
                # Adjust horizontal bounds to account for wall thickness
                left_adj = x_min + half_thickness
                right_adj = x_max - half_thickness

                refined_cells.append((top_adj, left_adj, bottom_adj, right_adj))
            else:  # Bottom wall opening
                # Adjust bottom boundary to account for wall thickness
                bottom_adj = y - half_thickness
                # Make cell square shaped
                top_adj = bottom_adj - cell_width
                # Adjust horizontal bounds to account for wall thickness
                left_adj = x_min + half_thickness
                right_adj = x_max - half_thickness

                refined_cells.append((top_adj, left_adj, bottom_adj, right_adj))

        elif opening_type == "vertical":
            x, y_min, y_max = coords
            cell_height = y_max - y_min

            if x == min(v_grid_lines):  # Left wall opening
                # Adjust left boundary to account for wall thickness
                left_adj = x + half_thickness
                # Make cell square shaped
                right_adj = left_adj + cell_height
                # Adjust vertical bounds to account for wall thickness
                top_adj = y_min + half_thickness
                bottom_adj = y_max - half_thickness

                refined_cells.append((top_adj, left_adj, bottom_adj, right_adj))
            else:  # Right wall opening
                # Adjust right boundary to account for wall thickness
                right_adj = x - half_thickness
                # Make cell square shaped
                left_adj = right_adj - cell_height
                # Adjust vertical bounds to account for wall thickness
                top_adj = y_min + half_thickness
                bottom_adj = y_max - half_thickness

                refined_cells.append((top_adj, left_adj, bottom_adj, right_adj))

    # Draw entry/exit cells in red
    for cell_top, cell_left, cell_bottom, cell_right in refined_cells:
        # Ensure coordinates are within image bounds
        cell_top = max(0, min(int(cell_top), h - 1))
        cell_bottom = max(0, min(int(cell_bottom), h - 1))
        cell_left = max(0, min(int(cell_left), w - 1))
        cell_right = max(0, min(int(cell_right), w - 1))

        # Create a cell mask
        cell_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.rectangle(cell_mask, (cell_left, cell_top), (cell_right, cell_bottom), 255, -1)

        # Remove wall pixels from the cell mask to prevent overlap
        cell_mask[wall_mask] = 0

        # Apply red color to the cell area
        cell_area = cell_mask > 0
        clean_maze[cell_area] = (0, 0, 255)  # Red color

        # Draw cell boundaries with the correct thickness to match walls
        # We'll draw them in red but exclude walls
        for thickness in range(1, wall_thickness + 1):
            # Top edge
            if cell_top - thickness >= 0:
                top_line = np.zeros((h, w), dtype=np.uint8)
                cv2.line(top_line, (cell_left, cell_top), (cell_right, cell_top), 255, thickness)
                top_line[wall_mask] = 0  # Don't draw over walls
                clean_maze[top_line > 0] = (0, 0, 255)

            # Bottom edge
            if cell_bottom + thickness < h:
                bottom_line = np.zeros((h, w), dtype=np.uint8)
                cv2.line(bottom_line, (cell_left, cell_bottom), (cell_right, cell_bottom), 255, thickness)
                bottom_line[wall_mask] = 0  # Don't draw over walls
                clean_maze[bottom_line > 0] = (0, 0, 255)

            # Left edge
            if cell_left - thickness >= 0:
                left_line = np.zeros((h, w), dtype=np.uint8)
                cv2.line(left_line, (cell_left, cell_top), (cell_left, cell_bottom), 255, thickness)
                left_line[wall_mask] = 0  # Don't draw over walls
                clean_maze[left_line > 0] = (0, 0, 255)

            # Right edge
            if cell_right + thickness < w:
                right_line = np.zeros((h, w), dtype=np.uint8)
                cv2.line(right_line, (cell_right, cell_top), (cell_right, cell_bottom), 255, thickness)
                right_line[wall_mask] = 0  # Don't draw over walls
                clean_maze[right_line > 0] = (0, 0, 255)

    return clean_maze

def draw_results(image, processed_maze, h_grid_lines, v_grid_lines, openings, nearest_cells):
    """Draw maze with outermost grid lines highlighted, opening lines in red, and nearest cells in blue."""
    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    h, w = image.shape

    # Draw all walls in green first
    wall_mask = processed_maze > 0
    image_color[wall_mask] = (0, 255, 0)

    # Identify outermost grid lines
    if not h_grid_lines or not v_grid_lines:
        return image_color

    top_line = min(h_grid_lines)
    bottom_line = max(h_grid_lines)
    left_line = min(v_grid_lines)
    right_line = max(v_grid_lines)

    # Thickness of the highlighted lines
    thickness = 2

    # Draw horizontal outermost grid lines in blue
    for i in range(max(0, top_line - thickness), min(h, top_line + thickness + 1)):
        row_mask = wall_mask[i, :]
        if np.any(row_mask):
            image_color[i, row_mask] = (255, 0, 0)  # Blue

    for i in range(max(0, bottom_line - thickness), min(h, bottom_line + thickness + 1)):
        row_mask = wall_mask[i, :]
        if np.any(row_mask):
            image_color[i, row_mask] = (255, 0, 0)  # Blue

    # Draw vertical outermost grid lines in blue
    for j in range(max(0, left_line - thickness), min(w, left_line + thickness + 1)):
        col_mask = wall_mask[:, j]
        if np.any(col_mask):
            image_color[col_mask, j] = (255, 0, 0)  # Blue

    for j in range(max(0, right_line - thickness), min(w, right_line + thickness + 1)):
        col_mask = wall_mask[:, j]
        if np.any(col_mask):
            image_color[col_mask, j] = (255, 0, 0)  # Blue

    # Draw opening lines in red
    line_thickness = 3  # Thickness of the red opening lines

    for opening_type, *coords in openings:
        if opening_type == "horizontal":
            y, x_min, x_max = coords
            cv2.line(image_color, (x_min, y), (x_max, y), (0, 0, 255), line_thickness)
        elif opening_type == "vertical":
            x, y_min, y_max = coords
            cv2.line(image_color, (x, y_min), (x, y_max), (0, 0, 255), line_thickness)

    # Fill nearest cells with blue color
    for cell_top, cell_left, cell_bottom, cell_right in nearest_cells:
        # Ensure coordinates are within image bounds
        cell_top = max(0, min(cell_top, h - 1))
        cell_bottom = max(0, min(cell_bottom, h - 1))
        cell_left = max(0, min(cell_left, w - 1))
        cell_right = max(0, min(cell_right, w - 1))

        # Create a mask for the cell area (excluding the wall pixels)
        cell_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.rectangle(cell_mask, (cell_left, cell_top), (cell_right, cell_bottom), 255, -1)

        # Remove wall pixels from the cell mask
        cell_mask[wall_mask] = 0

        # Apply the blue color to the cell area
        cell_area = cell_mask > 0
        image_color[cell_area] = (90, 39, 255)  # Light blue color

        # Draw cell borders (except for the red opening line)
        if cell_top > 0:
            cv2.line(image_color, (cell_left, cell_top), (cell_right, cell_top), (90, 39, 255), 2)
        if cell_bottom < h - 1:
            cv2.line(image_color, (cell_left, cell_bottom), (cell_right, cell_bottom), (90, 39, 255), 2)
        if cell_left > 0:
            cv2.line(image_color, (cell_left, cell_top), (cell_left, cell_bottom), (90, 39, 255), 2)
        if cell_right < w - 1:
            cv2.line(image_color, (cell_right, cell_top), (cell_right, cell_bottom), (90, 39, 255), 2)

    return image_color

def find_start_end_nodes(clean_maze):
    """
    Finds both red nodes in the cleaned maze image.
    Returns pixel coordinates of the start and end nodes.
    """
    # Convert to HSV for color detection
    hsv = cv2.cvtColor(clean_maze, cv2.COLOR_BGR2HSV)

    # Define red color range (two ranges for different shades of red)
    red_lower1 = np.array([0, 50, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 50, 50])
    red_upper2 = np.array([180, 255, 255])

    # Create masks for red color
    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = red_mask1 | red_mask2  # Combine both masks

    # Find contours for all red regions
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) < 2:
        print("⚠ Error: Could not detect two distinct red nodes. Check the image processing.")
        return None, None

    # Sort the red regions by x-coordinate (leftmost first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the centers of the two largest red regions
    start_coords, end_coords = None, None
    for i, contour in enumerate(contours[:2]):  # Take the first two detected red regions
        M = cv2.moments(contour)
        if M["m00"] != 0:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            if i == 0:
                start_coords = (center_x, center_y)  # Assign first detected red node as Start
            else:
                end_coords = (center_x, center_y)  # Assign second detected red node as End

    return start_coords, end_coords
