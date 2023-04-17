from solid import (
    OpenSCADObject,
    difference,
    linear_extrude,
    rotate,
    scad_render_to_file,
    translate,
    union,
)
from solid.objects import polygon, square


WIDTH_IN_BLOCKS = 9
HEIGHT_IN_BLOCKS = 9
BLOCK_SIZE = 1

PADDING = BLOCK_SIZE / 2
SPACING = BLOCK_SIZE + PADDING
CANVAS_WIDTH = (SPACING * WIDTH_IN_BLOCKS) + PADDING
CANVAS_HEIGHT = (SPACING * HEIGHT_IN_BLOCKS) + PADDING


def make_triangle() -> OpenSCADObject:
    """
      Everything is Triangles.   The ones we use look like this:

              1
      ---------------------
      |                  /
      |                /
      |              /
      |            /
    1 |          /
      |        /  √2
      |      /
      |    /
      |  /
      |/


    This is one half of the blocks we are using to draw everything.

    """
    vertices = [
        (0, BLOCK_SIZE),
        (BLOCK_SIZE, 0),
        (0, 0),
    ]
    midpoint = (
        (BLOCK_SIZE / 2) - BLOCK_SIZE,
        (BLOCK_SIZE / 2) - BLOCK_SIZE,
        0,
    )

    triangle = polygon(vertices)
    triangle = union()(translate(midpoint)(triangle))

    return triangle


def make_open_square(open_side: str = "", rotate_45=False) -> OpenSCADObject:
    """
     The blocks we make are either open or closed.   They can be opened on any side.


    This building block is half of the square.:
              1
      ---------------------
      |                  /
      |                /
      |              /
      |            /
    1 |          /
      |        /  √2
      |      /
      |    /
      |  /
      |/

      We overlay two of them to make this shape (but not all ascii messed up):
                    1
      ---------------------
      |                  /
      |                /
      |              /
      |            /
    1 |          /

      |          \
      |           \
      |            \
      |             \
      |              \
      ---------------------
                    1

    """

    triangle = make_triangle()
    if rotate_45:
        triangle = rotate((0, 0, 45))(triangle)
    square_chunks = []

    if open_side == "W":
        sections = (0, 0, 1, 1)
    elif open_side == "E":
        sections = (1, 1, 0, 0)
    elif open_side == "N":
        sections = (0, 1, 1, 0)
    elif open_side == "S":
        sections = (1, 0, 0, 1)
    else:
        sections = (1, 0, 1, 0)

    for i, each_section in enumerate(sections):
        if each_section:
            square_chunks.append(rotate((0, 0, 90 * i))(triangle))

    del triangle
    the_square = union()(*square_chunks)

    # Set the squares origin at the top corner fully inside the quadrant
    the_square = translate((BLOCK_SIZE / 2, BLOCK_SIZE / 2, 0))(the_square)

    return the_square


def create_decoration(block_coord: tuple[int, int], side: str = "") -> OpenSCADObject:
    """
    These are external triangles that poke out of the canvas.
    """
    decoration = make_triangle()
    x, y = block_coord

    rotation_angle = 0
    x_offset = 0
    y_offset = 0

    if side == "N":
        rotation_angle = 225
    elif side == "W":
        rotation_angle = 315
    elif side == "E":
        rotation_angle = 135
    elif side == "S":
        rotation_angle = 45

    if side == "N":
        y_offset = PADDING + PADDING / 2
    elif side == "W":
        x_offset = PADDING + PADDING / 2
    elif side == "E":
        x_offset = PADDING + PADDING / 2
    elif side == "S":
        y_offset = PADDING + PADDING / 2

    decoration = rotate((0, 0, rotation_angle))(decoration)
    decoration = translate(
        (
            ((x * SPACING) - BLOCK_SIZE / 2) + x_offset,
            -((y * SPACING) - BLOCK_SIZE / 2) - y_offset,
            0,
        ),
    )(decoration)

    return decoration


if __name__ == "__main__":
    from yvaral import l_instabilità_come_condizione_umana_1981

    the_base = square((CANVAS_HEIGHT, CANVAS_WIDTH))
    the_base = rotate((0, 0, 270))(the_base)
    the_base = linear_extrude(1)(the_base)

    the_holes = []
    for r_i, each_row in enumerate(l_instabilità_come_condizione_umana_1981):
        new_row = []
        for s_i, each_square in enumerate(each_row):
            square = make_open_square(*each_square)
            square = translate((SPACING * r_i, SPACING * s_i, 0))(square)
            new_row.append(square)
        full_row = union()(*new_row)
        full_row = rotate((0, 0, -90))(full_row)
        the_holes.append(full_row)

    holes = union()(*the_holes)
    holes = linear_extrude(3)(holes)
    holes = translate((PADDING, -PADDING, -1))(holes)

    top = create_decoration((4, 0), side="N")
    left = create_decoration((0, 3), side="W")
    right = create_decoration((9, 7), side="E")
    bottom1 = create_decoration((3, 9), side="S")
    bottom2 = create_decoration((7, 9), side="S")
    decorations = union()(top, left, right, bottom1, bottom2)
    decorations = linear_extrude(1)(decorations)

    final_art = difference()(the_base, holes)
    final_art = union()(final_art, decorations)
    scad_render_to_file(
        final_art, "L'instabilità come condizione umana by Yvaral (1981).scad"
    )
