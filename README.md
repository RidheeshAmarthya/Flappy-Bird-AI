# Flappy Bird AI using NEAT

This project implements an AI that learns to play Flappy Bird using the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. The game is built using Pygame, and the AI is trained to navigate the bird through pipes.

## Features

- Faithful recreation of the Flappy Bird game mechanics
- Implementation of the NEAT algorithm for AI training
- Visualization of the AI's decision-making process
- Generation counter and score tracking
- Customizable game parameters

## Screenshot
<img src="https://imgur.com/AcK2EYx.png" alt="Flappy Screenshot 2">

## Requirements

- Python 3.x
- Pygame
- NEAT-Python

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/flappy-bird-ai.git
   ```

2. Install the required packages:
   ```
   pip install pygame neat-python
   ```

3. Run the game:
   ```
   python flappy_bird_ai.py
   ```

## How it Works

The AI uses a neural network to decide when to make the bird jump. Each generation of birds attempts to navigate through the pipes, with the most successful birds being used to create the next generation. Over time, the AI learns to play the game effectively.

## Configuration

You can modify the `config-feedforward.txt` file to adjust the NEAT algorithm parameters, such as population size, mutation rates, and network structure.

## Customization

Feel free to experiment with the game parameters in the code:

- `WINDOW_WIDTH` and `WINDOW_HEIGHT`: Change the game window size
- `OBSTACLE.GAP`: Adjust the gap between pipes
- `OBSTACLE.VELOCITY`: Change the speed of the pipes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
