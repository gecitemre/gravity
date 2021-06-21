from tkinter import Tk,Canvas
from math import pi
from time import time
from constants import *
from functions import *
from copy import deepcopy
def universe():
    global planets,time_,dt,mode
    time_=0
    while time_<1:
        for i in range(len(planets)):
            planets[i].ax=planets[i].ay=0
        for i in range(len(planets)):
            planet1=planets[i]
            for j in range(i+1,len(planets)):
                planet2=planets[j]
                d=find_distance(planet1,planet2)
                if d<=planet1.radius+planet2.radius:
                    if color_mode=="normal":
                        planet1.color=planet2.color=[255,0,0]
                    collision(planet1,planet2,d)
                    gravity_inside(planet1,planet2)
                else:
                    acceleration(planet1,planet2)
            planets[i].move()
        planets=edge(planets)
        change_color(planets)
        time_+=dt
    return planets
def callback():
    global canvas,DELAY,now_b,now_c,double_click,pressed_r,pressed
    if flag: move_shapes(universe(),canvas,my_shapes)
    now_b=time()
    if now_c :
        if type(pressed)==int:
            if flag:
                planets[pressed].vx=planets[pressed].vy=0
                planets[pressed].x=cursor_x*scale
                planets[pressed].y=cursor_y*scale
                redraw_shape(canvas,my_shapes[pressed],cursor_x,cursor_y,planets[pressed].radius,planets[pressed].color)
        if pressed3:
            f=find(cursor_x,cursor_y,planets)
            if type(f)==int:
                delete(canvas,my_shapes,planets,f)
                pressed=False
    now_c=time()
    canvas.after(DELAY,callback)
def lcp(event):
    global pressed
    f=find(event.x,event.y,planets)
    if type(f)==int:
            pressed=f
    else:
        pressed=-1
        if color_mode=="random":
                color=[randrange(0,256),randrange(0,256),randrange(0,256)]
        elif color_mode=="normal":
                color=deepcopy(bgcolor)
        planets.append(planet(scale*event.x,scale*event.y,radius,4/3*pi*density*radius**3,color))
        my_shapes.append(draw_shape(canvas,scale*event.x,scale*event.y,radius,rgb_color(color)))
def lcr(event):
    global pressed,last_now,last_cursor_x,last_cursor_y
    if type(pressed)==int:
        time__=time()*1000
        planets[pressed].vx=scale*(event.x-last_cursor_x)/(time__-last_now)/play_speed
        planets[pressed].vy=scale*(event.y-last_cursor_y)/(time__-last_now)/play_speed
        pressed=False
def motion(event):
    global cursor_x,cursor_y,now,last_cursor_x,last_cursor_y,last_now
    time_=time()*1000
    if time_>now:
        last_cursor_x=cursor_x
        last_cursor_y=cursor_y
        cursor_x=event.x
        cursor_y=event.y
        last_now=now
        now=time_
def wheel(event):
    j=find(event.x,event.y,planets)
    if type(j)==int:
            planets[j].radius+=scale*event.delta/30
            if planets[j].radius<=0:
                delete(canvas,my_shapes,planets,j)
            else:
                planets[j].mass=4/3*pi*density*planets[j].radius**3
                redraw_shape(canvas,my_shapes[j],planets[j].x,planets[j].y,planets[j].radius,planets[j].color)
def bp3(event):
    global pressed3
    pressed3=True

def br3(event):
    global pressed3
    pressed3=False

def bp2(event):
    global flag
    flag=True

planets=create_universe(0)
tk = Tk()
tk.title('Gravity Simulator')
canvas = Canvas(tk,width=x2*2,height=y2*2)
canvas.configure(bg=rgb_color(bgcolor))
canvas.bind('<ButtonPress-1>',lcp)
canvas.bind('<ButtonRelease-1>',lcr)
canvas.bind('<Motion>', motion)
canvas.bind('<MouseWheel>',wheel)
canvas.bind('<ButtonPress-2>',bp2)
canvas.bind('<ButtonPress-3>',bp3)
canvas.bind('<ButtonRelease-3>',br3)
canvas.pack()
my_shapes=draw_shapes(canvas,universe())
canvas.after(DELAY,callback)
tk.mainloop()