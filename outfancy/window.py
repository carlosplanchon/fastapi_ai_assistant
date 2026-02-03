#!/usr/bin/env python3

from . import widgets


class Window:
    """It creates a Window Object."""
    def __init__(self, width: int, height: int, fill: str = ' ') -> None:
        self.content = widgets.create_matrix(
            x=width,
            y=height,
            fill=fill
            )

    def insert(self, matrix: list[list[str]] | list[str], x_vertex: int, y_vertex: int) -> None:
        """Each element of the matrix is inserted on the window."""
        # Variable to walk through the matrix (y value).
        y_index = 0
        while y_index < len(matrix) and y_vertex < len(self.content):
            # Variable to walk through the matrix (x value).
            x_index = 0
            x_vert = x_vertex
            while x_index < len(matrix[0]) and x_vert < len(self.content[0]):
                self.content[y_vertex][x_vert] = matrix[y_index][x_index]
                x_index += 1
                x_vert += 1
            y_index += 1
            y_vertex += 1

    def insert_point(self, point_character: str, x_coord: int, y_coord: int) -> None:
        """Each element of the matrix is inserted in the window."""
        if 0 <= y_coord < len(self.content) and 0 <= x_coord < len(self.content[0]):
            self.content[y_coord][x_coord] = point_character

    def render(self) -> str:
        return '\n'.join([''.join(x) for x in self.content])
