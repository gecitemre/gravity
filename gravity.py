from time import time
from tkinter import Tk, Canvas
import numpy
from ctypes import windll, byref, Structure

# from scipy.constants import gravitational_constant
# gravitational constant is ignored.


class POINT(Structure):
    from ctypes import c_long

    _fields_ = [("x", c_long), ("y", c_long)]


def get_cursor_coordinate() -> numpy.ndarray:
    point = POINT()
    windll.user32.GetCursorPos(byref(point))
    return numpy.array((point.x, point.y), dtype=float)


pressed_planet = None
bp3flag = False
before = now = time()
tk = Tk()
SCREENWIDTH = tk.winfo_screenwidth()
SCREENHEIGHT = tk.winfo_screenheight()

with open("variables.txt", "r") as file:
    dictionary = eval(file.read())
    SCALE = dictionary["SCALE"]  # int|float
    DENSITY = dictionary["DENSITY"]  # int|float
    DT = dictionary["DT"]  # 0<float<=1
    DELAY = dictionary["DELAY"]  # int
    PLAY_SPEED = dictionary["PLAY_SPEED"]  # int|float
    INITIAL_SPEED_CONSTANT = dictionary["INITIAL_SPEED_CONSTANT"]  # int|float
    COLOR_CHANGE_RATE = dictionary["COLOR_CHANGE_RATE"]  # int
    RADIUS_RANGE = dictionary["RADIUS_RANGE"]  # tuple[int|float,int|float]
    FEED_SPEED = dictionary["FEED_SPEED"]  # int|float
    EDGE_MODE = dictionary["EDGE_MODE"]  # "respawn"|"reflect"
    BG_COLOR = dictionary["BG_COLOR"]  # tuple[int,int,int]
    INITIAL_PLANETS = dictionary["INITIAL_PLANETS"]  # int
    RADIUS_MIN = dictionary["RADIUS_MIN"]  # float

PLANET_COLOR = 255.0 * (128 * numpy.ones(3, dtype=int) > numpy.array(BG_COLOR))
COLLISION_COLOR = numpy.array((255.0, 0.0, 0.0))
cursor_coordinate = old_cursor_coordinate = get_cursor_coordinate()
CENTER = numpy.array((SCREENWIDTH, SCREENHEIGHT)) * SCALE / 2

"""@numba.experimental.jitclass(
spec=[("coordinate",numba.float64[:]),
      ("radius",numba.int64),
      ("mass",numba.float64),
      ("acceleration",numba.float64[:]),
      ("velocity",numba.float64[:]),
      ("color",numba.float64[:]),
      ("ID",numba.int64)
])"""


class Planet:
    def __init__(
        self,
        coordinate,
        velocity=numpy.zeros(2),
        acceleration=numpy.zeros(2),
        color=PLANET_COLOR.copy(),
        mass=1,
        radius=10,
        ID=None,
    ):
        self.coordinate = coordinate
        self.radius = radius
        self.mass = mass
        self.acceleration = acceleration
        self.velocity = velocity
        self.color = color
        self.ID = ID

    def redraw(self):
        canvas.itemconfig(
            self.ID,
            fill=rgb_color(self.color.astype(int)),
            outline=rgb_color(self.color.astype(int)),
        )
        canvas.coords(
            self.ID,
            tuple(
                numpy.hstack(
                    (self.coordinate - self.radius, self.coordinate + self.radius)
                )
                / SCALE
            ),
        )

    def move(self):
        self.coordinate += (
            (self.velocity + self.acceleration * DT * PLAY_SPEED / 2) * DT * PLAY_SPEED
        )
        self.velocity += self.acceleration * DT * PLAY_SPEED
        self.acceleration = numpy.zeros(2)
        edge(self)


def rgb_color(rgb) -> str:
    return f"#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])


def find_planet(coordinate: numpy.ndarray):
    for index, planet in enumerate(planets):
        if numpy.linalg.norm(coordinate - planet.coordinate) < planet.radius:
            return {"index": index, "planet": planet}
    else:
        return {"index": None, "planet": None}


def main():
    for _ in range(int(1 / DT)):
        if pressed_planet:
            planets_iterate = planets[:pp_index] + planets[pp_index + 1 :]
            for i, planet1 in enumerate(planets_iterate):
                interact_p(pressed_planet, planet1)
                for planet2 in planets_iterate[i + 1 :]:
                    interact(planet1, planet2)
                planet1.move()
            pressed_planet.move()

        else:
            for i, planet1 in enumerate(planets):
                for planet2 in planets[i + 1 :]:
                    interact(planet1, planet2)
                planet1.move()

    for planet in planets:
        planet.color += COLOR_CHANGE_RATE * (PLANET_COLOR - planet.color)
        planet.redraw()


def interact(planet1, planet2):
    vector12 = planet2.coordinate - planet1.coordinate
    distance_squared = sum(pow(vector12, 2))
    distance = numpy.sqrt(distance_squared)
    real_distance = distance - planet1.radius - planet2.radius
    # collide
    if real_distance < 0:
        # elastic collision
        vector_a = (
            2
            * numpy.matmul(planet1.velocity - planet2.velocity, vector12)
            * vector12
            / (distance_squared * (planet1.mass + planet2.mass))
        )
        planet1.velocity -= planet2.mass * vector_a
        planet2.velocity += planet1.mass * vector_a
        planet1.color = planet2.color = COLLISION_COLOR.copy()

        # push away
        vector_a = vector12 * real_distance / distance
        planet1.coordinate += planet2.mass * vector_a / (planet1.mass + planet2.mass)
        planet2.coordinate -= planet1.mass * vector_a / (planet1.mass + planet2.mass)

    # gravitation
    # gravitational constant is ignored.
    vector_a = vector12 * planet1.mass * planet2.mass / pow(distance, 3)
    planet1.acceleration += vector_a / planet1.mass
    planet2.acceleration -= vector_a / planet2.mass


def interact_p(pressed_planet, planet):
    vector12 = planet.coordinate - pressed_planet.coordinate
    distance_squared = sum(pow(vector12, 2))
    distance = numpy.sqrt(distance_squared)
    real_distance = distance - pressed_planet.radius - planet.radius
    # collide
    if distance:
        if real_distance < 0:
            # elastic collision
            vector_a = (
                2
                * numpy.matmul(pressed_planet.velocity - planet.velocity, vector12)
                * vector12
                / (distance_squared * (pressed_planet.mass + planet.mass))
            )
            pressed_planet.velocity -= planet.mass * vector_a
            planet.velocity += pressed_planet.mass * vector_a
            pressed_planet.color = planet.color = COLLISION_COLOR.copy()

            # push away
            planet.coordinate -= vector12 * real_distance / distance

        # gravitation
        # gravitational constant is ignored.
        vector_a = vector12 * pressed_planet.mass * planet.mass / pow(distance, 3)
        pressed_planet.acceleration += vector_a / pressed_planet.mass
        planet.acceleration -= vector_a / planet.mass


def callback():
    global pressed_planet, cursor_coordinate, before, now, old_cursor_coordinate, coordinate_difference
    old_cursor_coordinate = cursor_coordinate
    cursor_coordinate = get_cursor_coordinate()
    before = now
    now = time() * 1000
    main()
    if pressed_planet != None:
        pressed_planet.velocity = numpy.zeros(2)
        pressed_planet.coordinate = SCALE * cursor_coordinate + coordinate_difference
        pressed_planet.redraw()

    if bp3flag:
        index, planet = find_planet(SCALE * cursor_coordinate).values()
        if planet != None:
            if pressed_planet == planet:
                pressed_planet = None
            canvas.delete(planet.ID)
            del planets[index]
    canvas.after(DELAY, callback)


def ButtonPress1(event):
    global pressed_planet, coordinate_difference, pp_index
    coordinate = SCALE * numpy.array((event.x, event.y), dtype=float)
    pp_index, pressed_planet = find_planet(coordinate).values()
    if pressed_planet == None:
        coordinate_difference = numpy.zeros(2)
        radius = numpy.random.uniform(RADIUS_RANGE[0], RADIUS_RANGE[1]) * SCALE
        pressed_planet = Planet(
            coordinate,
            radius=radius,
            mass=4 / 3 * numpy.pi * DENSITY * radius ** 3,
            ID=canvas.create_oval(
                tuple(numpy.hstack((coordinate - radius, coordinate + radius)) / SCALE),
                fill=rgb_color(PLANET_COLOR.astype(int)),
            ),
        )
        pp_index = len(planets)
        planets.append(pressed_planet)
    else:
        coordinate_difference = pressed_planet.coordinate - coordinate


def ButtonRelease1(event):
    global pressed_planet, old_cursor_coordinate
    if pressed_planet:
        pressed_planet.velocity = (
            SCALE
            / PLAY_SPEED
            * (numpy.array((event.x, event.y)) - old_cursor_coordinate)
            / (time() * 1000 - before)
        )
        pressed_planet = None


def MouseWheel(event):
    global pressed_planet
    index, planet = find_planet(SCALE * numpy.array((event.x, event.y))).values()
    if planet != None:
        planet.radius += SCALE * event.delta * FEED_SPEED
        if planet.radius <= SCALE * RADIUS_MIN:
            canvas.delete(planet.ID)
            del planets[index]
            pressed_planet = None
        else:
            planet.mass = 4 / 3 * numpy.pi * DENSITY * planet.radius ** 3
            planet.redraw()


def ButtonPress3(event):
    global bp3flag
    bp3flag = True


def ButtonRelease3(event):
    global bp3flag
    bp3flag = False


def ButtonPress2(event):
    global coordinate_difference
    if pressed_planet:
        coordinate_difference = numpy.zeros(2)


if EDGE_MODE == "reflect":

    def create_universe() -> list[Planet]:
        planets = []
        for _ in range(INITIAL_PLANETS):
            flag = True
            while flag:
                radius = numpy.random.uniform(RADIUS_RANGE[0], RADIUS_RANGE[1]) * SCALE
                coordinate = numpy.random.uniform(high=2, size=2) * (CENTER - radius)
                for planet in planets:
                    if planet.radius + radius >= numpy.linalg.norm(
                        planet.coordinate - coordinate
                    ):
                        break
                flag = False
            planets.append(
                Planet(
                    coordinate,
                    numpy.random.uniform(high=INITIAL_SPEED_CONSTANT * SCALE, size=2),
                    mass=4 / 3 * numpy.pi * DENSITY * radius ** 3,
                    radius=radius,
                    ID=canvas.create_oval(
                        tuple(
                            numpy.hstack((coordinate - radius, coordinate + radius))
                            / SCALE
                        ),
                        fill=rgb_color(PLANET_COLOR.astype(int)),
                    ),
                )
            )
        return planets

    def edge(planet):
        global coordinate_difference
        edge_matrix = numpy.vstack(
            (
                planet.coordinate <= planet.radius,
                planet.coordinate >= 2 * CENTER - planet.radius,
            )
        )
        if edge_matrix.any():
            planet.color = COLLISION_COLOR.copy()
            change = (
                edge_matrix
                * (
                    numpy.vstack(
                        (
                            numpy.array((planet.radius, planet.radius)),
                            2 * CENTER - planet.radius,
                        )
                    )
                    - planet.coordinate
                )
            ).sum(axis=0)
            planet.velocity *= -2 * edge_matrix.sum(axis=0) + 1
            if pressed_planet == planet:
                coordinate_difference += change
            planet.coordinate += change


elif EDGE_MODE == "respawn":

    def create_universe() -> list[Planet]:
        planets = []
        for _ in range(INITIAL_PLANETS):
            flag = True
            while flag:
                r = numpy.random.uniform(high=numpy.linalg.norm(CENTER))
                theta = numpy.random.uniform(high=2 * numpy.pi)
                coordinate = r * (
                    numpy.array(numpy.cos(theta), numpy.sin(theta)) + CENTER
                )
                radius = numpy.random.uniform(RADIUS_RANGE[0], RADIUS_RANGE[1]) * SCALE
                for planet in planets:
                    if planet.radius + radius < numpy.linalg.norm(
                        planet.coordinate - coordinate
                    ):
                        break
                flag = False

            planets.append(
                Planet(
                    coordinate,
                    numpy.random.uniform(high=INITIAL_SPEED_CONSTANT * SCALE, size=2),
                    mass=4 / 3 * numpy.pi * DENSITY * radius ** 3,
                    radius=radius,
                    ID=canvas.create_oval(
                        tuple(
                            numpy.hstack((coordinate - radius, coordinate + radius))
                            / SCALE
                        ),
                        fill=rgb_color(PLANET_COLOR.astype(int)),
                    ),
                )
            )
        return planets

    def edge(planet):
        if numpy.linalg.norm(planet.coordinate - CENTER) > numpy.linalg.norm(CENTER):
            planet.coordinate = 2 * CENTER - planet.coordinate


tk.title("Gravity Simulator - Emre Geçit")
tk.attributes("-fullscreen", True)
canvas = Canvas(tk, width=SCREENWIDTH, height=SCREENHEIGHT)
planets = create_universe()
canvas.configure(bg=rgb_color(BG_COLOR))
canvas.bind("<ButtonPress-1>", ButtonPress1)
canvas.bind("<ButtonRelease-1>", ButtonRelease1)
canvas.bind("<MouseWheel>", MouseWheel)
canvas.bind("<ButtonPress-3>", ButtonPress3)
canvas.bind("<ButtonRelease-3>", ButtonRelease3)
canvas.bind("<ButtonPress-2>", ButtonPress2)
canvas.pack()
canvas.after(DELAY, callback)
tk.mainloop()
