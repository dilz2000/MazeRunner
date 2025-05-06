# 🧩 MazeRunners: Advanced Maze Generation & Pathfinding System
  
  **An intelligent maze generation, extraction & pathfinding visualization platform**
  
</div>

## ✨ Features

- **Dynamic Maze Generation**: Creates perfect mazes with guaranteed solutions using Kruskal's algorithm
- **Computer Vision Integration**: Extract mazes from images using advanced CV techniques
- **Multiple Pathfinding Algorithms**:
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
  - Dijkstra's Algorithm
  - A* Algorithm
  - Greedy Best-First Search
  - Iterative Deepening DFS (IDDFS)
  - Jump Point Search (JPS)
- **Interactive Visualization**: See algorithms work in real-time with customizable animation speed
- **Custom Maze Editing**: Create your own maze challenges by adding or removing walls
- **Performance Measurement**: Compare algorithm efficiency across different maze sizes
- **Image-to-Maze Conversion**: Upload images of mazes and solve them 


## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/dilz2000/MazeRunner.git

# Navigate to the project directory

# Run the main application
python main.py
```

## 🎮 Usage

1. **Generate a Maze**: Select maze size and generate
2. **Import from Image**: Upload an image of a maze 
3. **Choose Algorithm**: Select pathfinding algorithm
4. **Solve**: Visualize the algorithm in action
5. **Custom Editing**: Draw and erase walls to modify the maze
6. **Reset**: Remove solution path

## 🏗️ Project Structure

```
MazeRunners/
├── models/            # Defines structure of maze and grid cells
├── solvers/           # Implements different path-finding algorithms
├── views/             # Visualizes maze using Tkinter
├── controllers/       # Handles UI logic and user interaction
├── image_processor.py # Image processing
└── main.py            # Main entry point of application
```

## 🧠 Technical Details

### Maze Generation

We use **Kruskal's Algorithm** with disjoint-set (Union-Find) to generate perfect mazes with exactly one path between any two points. This approach:

- Creates balanced maze structures with distributed pathways
- Avoids predictable patterns found in DFS-generated mazes
- Guarantees solvability while maintaining challenge

### Computer Vision Maze Extraction

Our system extracts mazes from images through several sophisticated steps:

#### Image Preprocessing
- Grayscale conversion and Gaussian blur for noise reduction
- Adaptive Canny edge detection with dynamic thresholding
- Wall thickness estimation from edge patterns

#### Grid Detection
- Adaptive Hough Line Transform based on estimated wall thickness
- Dual-method approach combining standard and probabilistic line detection
- Line clustering and merging with 10px proximity threshold

#### Maze Reconstruction
- Wall alignment verification with original maze lines
- Start/end point detection using HSV color space and border gap analysis
- Cell-by-cell maze structure reconstruction based on pixel intensity along grid lines

### Pathfinding Optimization

Each algorithm is optimized differently:

- **A*** uses Manhattan distance heuristic to prioritize promising paths
- **Jump Point Search** skips redundant nodes for faster exploration
- **IDDFS** limits search depth to save memory 
- **Greedy BFS** offers fast (but sometimes suboptimal) solutions

### Visualization

Built with Tkinter, our visualization:
- Uses color-coding to show visited nodes (yellow) and final path (blue)
- Implements non-blocking animation with Canvas.after()
- Provides real-time feedback on algorithm progress
- Supports display of extracted image mazes alongside generated ones

## 👥 Team MazeRunners

- [Team Member 1](https://github.com/dilz2000) - Dilranga Dissanayake
- [Team Member 2](https://github.com/NipuniTennakoon) - Nipuni Tennakoon
- [Team Member 3](https://github.com/Thithira-Paranawithana) - Thithira Paranawithana


## 🙏 Acknowledgements

- Thanks to all contributors who have helped with this project
- Special thanks to Department of Computer Engineering, University of Sri Jayewardenepura for guidance
