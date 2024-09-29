import pygame
import numpy as np
import random

# Screen parameters
width = 800
height = 800
center = np.array([width / 2, height / 2])
screen = pygame.display.set_mode((width, height))

# Colors
colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "gray": (150, 150, 150),
}

# Set the frame rate
fpsClock = pygame.time.Clock()
fps = 60


def cartesian_to_screen(car_pos):
    factor = 0.02
    screen_pos = np.array([center[0] * factor + car_pos[0], center[1] * factor - car_pos[1]]) / factor
    return screen_pos.astype(int)


def screen_to_cartesian(screen_pos):
    factor = 0.02
    car_pos = np.array([screen_pos[0] - center[0], center[1] - screen_pos[1]]) * factor
    return car_pos.astype(float)


class Graph:
    def __init__(self, n, n_ants):
        self.t = 0
        self.n = n
        self.grid = [[None for _ in range(n)] for _ in range(n)]
        self.nodes = []
        self.edges = []
        self.ants = []
        xs = np.linspace(-7, 7, n)
        ys = np.linspace(-7, 7, n)
        for i in range(n):
            for j in range(n):
                node = self.Node(np.array([xs[i], ys[j]]))
                self.grid[i][j] = node
                self.nodes.append(node)

        # Create edges
        near_pos = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for i in range(n):
            for j in range(n):
                for pos in near_pos:
                    i_ = i + pos[0]
                    j_ = j + pos[1]
                    if self.index_is_valid(i_) and self.index_is_valid(j_):
                        edge = self.Edge(self.grid[i][j], self.grid[i_][j_])
                        self.edges.append(edge)
                        self.grid[i][j].connections.append(edge)

        # Create ants
        for _ in range(n_ants):
            self.ants.append(self.Ant(self.grid[0][0]))

        self.destination = None

    def search(self):
        if self.destination is None:
            return

        self.t += 1
        self.draw()
        for ant in self.ants:
            ant.navigate(self.destination, self)
        for edge in self.edges:
            edge.pheromone *= 0.95  # Evaporation
            edge.pheromone = max(edge.pheromone, 0)  # Prevent negative pheromone levels

    def index_is_valid(self, i):
        return 0 <= i < self.n

    class Node:
        def __init__(self, pos):
            self.pos = pos
            self.connections = []

    class Edge:
        def __init__(self, A, B):
            self.nodes = [A, B]
            self.A = A
            self.B = B
            self.pheromone = 1
            self.weight = np.linalg.norm(A.pos - B.pos)

    class Ant:
        def __init__(self, start):
            self.start = start
            self.current = start
            self.trace = []

        def navigate(self, d, g):
            if self.current == d:
                self.update_pheromones(g)
                self.current = self.start
                self.trace = []
                return

            p = [connection.pheromone for connection in self.current.connections]
            p = np.array(p) / np.sum(p)  # Normalize pheromone levels
            edge = np.random.choice(self.current.connections, p=p)
            self.current = edge.B
            self.trace.append(edge)

        def update_pheromones(self, g):
            if len(self.trace) == 0:
                return
            w = sum(edge.weight for edge in self.trace)
            for edge in self.trace:
                edge.pheromone += 10 / w

    def draw(self):
        pygame.event.get()
        screen.fill((0, 0, 0))

        # Draw nodes
        for node in self.nodes:
            pygame.draw.circle(screen, colors["red"], cartesian_to_screen(node.pos), 2)

        # Draw edges with pheromone levels
        for edge in self.edges:
            thickness = min(int(edge.pheromone * 5), 8)
            color = (int(255 * (1 - edge.pheromone / 10)), 0, 0)  # Gradient based on pheromone level
            pygame.draw.line(screen, color, cartesian_to_screen(edge.nodes[0].pos),
                             cartesian_to_screen(edge.nodes[1].pos), thickness)

        # Draw ants
        for ant in self.ants:
            pygame.draw.circle(screen, colors["green"], cartesian_to_screen(ant.current.pos), 5)

        # Draw destination
        if self.destination:
            pygame.draw.circle(screen, colors["yellow"], cartesian_to_screen(self.destination.pos), 9)
            # Draw feedback text
            font = pygame.font.SysFont(None, 36)
            feedback_text = "Destination Set!"
            feedback_surface = font.render(feedback_text, True, colors["white"])
            screen.blit(feedback_surface, (10, height - 40))

        # Draw statistics
        font = pygame.font.SysFont(None, 36)
        stats_text = f"Iteration: {self.t} | Ants: {len(self.ants)}"
        stats_surface = font.render(stats_text, True, colors["white"])
        screen.blit(stats_surface, (10, 10))

        pygame.display.flip()


def main():
    pygame.init()
    graph = Graph(20, 100)

    running = True
    while running:
        graph.search()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                cartesian_pos = screen_to_cartesian(mouse_pos)
                # Find the closest node to set as destination
                closest_node = min(graph.nodes, key=lambda node: np.linalg.norm(node.pos - cartesian_pos))
                graph.destination = closest_node

        fpsClock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
