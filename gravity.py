"""Gravity simulation.

Run this script to start the simulation.

Left click to create new planet, press to hold a planet, right click to delete planet,
scroll when your cursor is on a planet to feed or shrink a planet.
"""

from tkinter import Tk, Canvas
from time import time
import numpy
from pyautogui import position
import config

# from scipy.constants import gravitational_constant
# gravitational constant is ignored.

pressed_planet = None
bp3flag = False
before = now = time()
tk = Tk()
SCREENWIDTH = tk.winfo_screenwidth()
SCREENHEIGHT = tk.winfo_screenheight()

PLANET_COLOR = 255.0 * (128 * numpy.ones(3, dtype=int) > numpy.array(config.BG_COLOR))
COLLISION_COLOR = numpy.array((255.0, 0.0, 0.0))
cursor_coordinate = old_cursor_coordinate = numpy.array(position())
SIZE = numpy.array((SCREENWIDTH, SCREENHEIGHT))
CENTER = SIZE * config.SCALE / 2


class Planet:
    """Planet class."""

    def __init__(
        self,
        coordinate,
        velocity=numpy.zeros(2),
        acceleration=numpy.zeros(2),
        color=PLANET_COLOR.copy(),
        mass=1,
        radius=10,
        planet_id=None,
    ):
        self.coordinate = coordinate
        self.radius = radius
        self.mass = mass
        self.acceleration = acceleration
        self.velocity = velocity
        self.color = color
        self.planet_id = planet_id

    def redraw(self):
        canvas.itemconfig(
            self.planet_id,
            fill=rgb_color(self.color.astype(int)),
            outline=rgb_color(self.color.astype(int)),
        )
        canvas.coords(
            self.planet_id,
            tuple(
                numpy.hstack(
                    (self.coordinate - self.radius, self.coordinate + self.radius)
                )
                / config.SCALE
            ),
        )

    def move(self):
        self.coordinate += (
            (self.velocity + self.acceleration * config.DT * config.PLAY_SPEED / 2)
            * config.DT
            * config.PLAY_SPEED
        )
        self.velocity += self.acceleration * config.DT * config.PLAY_SPEED
        self.acceleration = numpy.zeros(2)
        edge(self)


def rgb_color(rgb) -> str:
    return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])


def find_planet(coordinate: numpy.ndarray):
    for index, planet in enumerate(planets):
        if numpy.linalg.norm(coordinate - planet.coordinate) < planet.radius:
            return {"index": index, "planet": planet}
    return {"index": None, "planet": None}


def main():
    for _ in range(int(1 / config.DT)):
        if pressed_planet:
            planets_iterate = planets[:pp_index] + planets[pp_index + 1 :]
            for i, planet1 in enumerate(planets_iterate):
                interact_p(planet1)
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
        planet.color += config.COLOR_CHANGE_RATE * (PLANET_COLOR - planet.color)
        planet.redraw()


def interact(planet1, planet2):
    vector21 = planet2.coordinate - planet1.coordinate
    distance_squared = sum(pow(vector21, 2))
    distance = numpy.sqrt(distance_squared)
    real_distance = distance - planet1.radius - planet2.radius
    # collide
    if real_distance < 0:
        # elastic collision
        vector_a = (
            2
            * numpy.matmul(planet1.velocity - planet2.velocity, vector21)
            * vector21
            / distance_squared
            / (planet1.mass + planet2.mass)
        )
        planet1.velocity -= planet2.mass * vector_a
        planet2.velocity += planet1.mass * vector_a
        planet1.color = planet2.color = COLLISION_COLOR.copy()

        # push away
        vector_a = vector21 * real_distance / distance / (planet1.mass + planet2.mass)
        planet1.coordinate += planet2.mass * vector_a
        planet2.coordinate -= planet1.mass * vector_a

    # gravitation
    # gravitational constant is ignored.
    vector_a = vector21 * planet1.mass * planet2.mass / pow(distance, 3)
    planet1.acceleration += vector_a / planet1.mass
    planet2.acceleration -= vector_a / planet2.mass


def interact_p(planet):
    vector21 = planet.coordinate - pressed_planet.coordinate
    distance_squared = sum(pow(vector21, 2))
    distance = numpy.sqrt(distance_squared)
    real_distance = distance - pressed_planet.radius - planet.radius
    # collide
    if distance:
        if real_distance < 0:
            # elastic collision
            vector_a = (
                2
                * numpy.matmul(pressed_planet.velocity - planet.velocity, vector21)
                * vector21
                / distance_squared
                / (pressed_planet.mass + planet.mass)
            )
            pressed_planet.velocity -= planet.mass * vector_a
            planet.velocity += pressed_planet.mass * vector_a
            pressed_planet.color = planet.color = COLLISION_COLOR.copy()

            # push away
            planet.coordinate -= vector21 * real_distance / distance

        # gravitation
        # gravitational constant is ignored.
        vector_a = vector21 * pressed_planet.mass * planet.mass / pow(distance, 3)
        pressed_planet.acceleration += vector_a / pressed_planet.mass
        planet.acceleration -= vector_a / planet.mass


def callback():
    global cursor_coordinate, before, now, old_cursor_coordinate, coordinate_difference, pressed_planet
    old_cursor_coordinate = cursor_coordinate
    cursor_coordinate = numpy.array(position())
    before = now
    now = time() * 1000
    main()
    if pressed_planet is not None:
        pressed_planet.velocity = numpy.zeros(2)
        pressed_planet.coordinate = (
            config.SCALE * cursor_coordinate + coordinate_difference
        )
        pressed_planet.redraw()

    if bp3flag:
        index, planet = find_planet(config.SCALE * cursor_coordinate).values()
        if planet is not None:
            if pressed_planet == planet:
                pressed_planet = None
            canvas.delete(planet.planet_id)
            del planets[index]
    canvas.after(config.DELAY, callback)


def ButtonPress1(event):
    global pressed_planet, coordinate_difference, pp_index
    coordinate = config.SCALE * numpy.array((event.x, event.y), dtype=float)
    pp_index, pressed_planet = find_planet(coordinate).values()
    if pressed_planet is None:
        coordinate_difference = numpy.zeros(2)
        radius = (
            numpy.random.uniform(config.RADIUS_RANGE[0], config.RADIUS_RANGE[1])
            * config.SCALE
        )
        pressed_planet = Planet(
            coordinate,
            radius=radius,
            mass=4 / 3 * numpy.pi * config.DENSITY * radius**3,
            planet_id=canvas.create_oval(
                tuple(
                    numpy.hstack((coordinate - radius, coordinate + radius))
                    / config.SCALE
                ),
                fill=rgb_color(PLANET_COLOR.astype(int)),
            ),
        )
        pp_index = len(planets)
        planets.append(pressed_planet)
    else:
        coordinate_difference = pressed_planet.coordinate - coordinate


def ButtonRelease1(event):
    global pressed_planet
    if pressed_planet is not None:
        pressed_planet.velocity = (
            config.SCALE
            / config.PLAY_SPEED
            * (numpy.array((event.x, event.y)) - old_cursor_coordinate)
            / (time() * 1000 - before)
        )
        pressed_planet = None


def MouseWheel(event):
    global pressed_planet
    index, planet = find_planet(config.SCALE * numpy.array((event.x, event.y))).values()
    if planet is not None:
        planet.radius += config.SCALE * event.delta * config.FEED_SPEED
        if planet.radius <= config.SCALE * config.RADIUS_MIN:
            canvas.delete(planet.planet_id)
            del planets[index]
            pressed_planet = None
        else:
            planet.mass = 4 / 3 * numpy.pi * config.DENSITY * planet.radius**3
            planet.redraw()


def button_press3(_):
    global bp3flag
    bp3flag = True


def button_release3(_):
    global bp3flag
    bp3flag = False


def button_press2(_):
    global coordinate_difference
    if pressed_planet:
        coordinate_difference = numpy.zeros(2)


if config.EDGE_MODE == "reflect":

    def create_universe() -> list:
        planets_ = []
        for _ in range(config.INITIAL_PLANETS):
            flag = True
            while flag:
                radius = (
                    numpy.random.uniform(config.RADIUS_RANGE[0], config.RADIUS_RANGE[1])
                    * config.SCALE
                )
                coordinate = numpy.random.uniform(high=2, size=2) * (CENTER - radius)
                for planet in planets_:
                    if planet.radius + radius >= numpy.linalg.norm(
                        planet.coordinate - coordinate
                    ):
                        break
                flag = False
            planets_.append(
                Planet(
                    coordinate,
                    numpy.random.uniform(
                        high=config.INITIAL_SPEED_CONSTANT * config.SCALE, size=2
                    ),
                    mass=4 / 3 * numpy.pi * config.DENSITY * radius**3,
                    radius=radius,
                    planet_id=canvas.create_oval(
                        tuple(
                            numpy.hstack((coordinate - radius, coordinate + radius))
                            / config.SCALE
                        ),
                        fill=rgb_color(PLANET_COLOR.astype(int)),
                    ),
                )
            )
        return planets_

    def edge(planet):
        global coordinate_difference
        edge_matrix = numpy.vstack(
            (
                planet.coordinate <= planet.radius,
                planet.coordinate >= SIZE - planet.radius,
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
                            SIZE - planet.radius,
                        )
                    )
                    - planet.coordinate
                )
            ).sum(axis=0)
            planet.velocity *= -2 * edge_matrix.sum(axis=0) + 1
            if pressed_planet == planet:
                coordinate_difference += change
            planet.coordinate += change

elif config.EDGE_MODE == "respawn":

    def create_universe() -> list[Planet]:
        planets_ = []
        for _ in range(config.INITIAL_PLANETS):
            flag = True
            while flag:
                array = numpy.random.uniform(high=numpy.linalg.norm(CENTER))
                theta = numpy.random.uniform(high=2 * numpy.pi)
                coordinate = array * (
                    numpy.array(numpy.cos(theta), numpy.sin(theta)) + CENTER
                )
                radius = (
                    numpy.random.uniform(config.RADIUS_RANGE[0], config.RADIUS_RANGE[1])
                    * config.SCALE
                )
                for planet in planets_:
                    if planet.radius + radius < numpy.linalg.norm(
                        planet.coordinate - coordinate
                    ):
                        break
                flag = False

            planets_.append(
                Planet(
                    coordinate,
                    numpy.random.uniform(
                        high=config.INITIAL_SPEED_CONSTANT * config.SCALE, size=2
                    ),
                    mass=4 / 3 * numpy.pi * config.DENSITY * radius**3,
                    radius=radius,
                    planet_id=canvas.create_oval(
                        tuple(
                            numpy.hstack((coordinate - radius, coordinate + radius))
                            / config.SCALE
                        ),
                        fill=rgb_color(PLANET_COLOR.astype(int)),
                    ),
                )
            )
        return planets_

    def edge(planet):
        if numpy.linalg.norm(planet.coordinate - CENTER) > numpy.linalg.norm(CENTER):
            planet.coordinate = SIZE - planet.coordinate


tk.title("Gravity Simulator - Emre Geçit")
tk.attributes("-fullscreen", True)
canvas = Canvas(tk, width=SCREENWIDTH, height=SCREENHEIGHT)
planets = create_universe()
canvas.configure(bg=rgb_color(config.BG_COLOR))
canvas.bind("<ButtonPress-1>", ButtonPress1)
canvas.bind("<ButtonRelease-1>", ButtonRelease1)
canvas.bind("<MouseWheel>", MouseWheel)
canvas.bind("<ButtonPress-3>", button_press3)
canvas.bind("<ButtonRelease-3>", button_release3)
canvas.bind("<ButtonPress-2>", button_press2)
canvas.pack()
canvas.after(config.DELAY, callback)
tk.mainloop()
