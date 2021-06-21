from random import random,choice,randrange
from math import pi,sin,cos,sqrt
from constants import *
from variables import *
class planet:
    def __init__(self,x,y,radius=10,mass=1,color=[255,255,255],vx=0,vy=0,ax=0,ay=0):
        self.x=x
        self.y=y
        self.radius = radius
        self.mass = mass
        self.ax = ax
        self.ay = ay
        self.color = color
        self.vx = vx
        self.vy = vy
    def move(self):
        self.vx+=self.ax*t
        self.vy+=self.ay*t
        self.x+=self.vx*t+(self.ax*t**2)/2
        self.y+=self.vy*t+(self.ay*t**2)/2
def draw_shapes(canvas,universe):
    my_shapes=[]
    for item in universe:
        x=item.x
        y=item.y
        radius=item.radius
        color=rgb_color(item.color)
        my_shapes.append(draw_shape(canvas,x,y,radius,color))
    return my_shapes
def move_shapes(universe,canvas,my_shapes):
    i=0
    for item in universe:
        x=item.x
        y=item.y
        radius=item.radius
        color=item.color
        redraw_shape(canvas, my_shapes[i], x, y, radius,color)
        i+=1
def edge(planets):
    if mode=="reflect":
        for planet in planets:
            if planet.radius+planet.x>=(x2*2) and planet.vx>0:
                if color_mode=="normal":
                    planet.color=[255,0,0]
                planet.vx*=-1
            elif planet.x-planet.radius<=0 and planet.vx<0:
                if color_mode=="normal":
                    planet.color=[255,0,0]
                planet.vx*=-1
            if planet.radius+planet.y>=(y2*2) and planet.vy>0:
                if color_mode=="normal":
                    planet.color=[255,0,0]
                planet.vy*=-1
            elif planet.y-planet.radius<=0 and planet.vy<0:
                if color_mode=="normal":
                    planet.color=[255,0,0]
                planet.vy*=-1
        return planets
    elif mode=="respawn":
        screen_radius=(x2**2+y2**2)**(1/2)
        for planet in planets:
            if pow(planet.x-x2,2)+pow(planet.y-y2,2)>screen_radius**2:
                planet.x+=2*(x2-planet.x)
                planet.y+=2*(y2-planet.y)
        return planets

def respawn(planets):
    screen_radius=(x2**2+y2**2)**(1/2)
    for planet in planets:
        if pow(planet.x-x2,2)+pow(planet.y-y2,2)>screen_radius**2:
            planet.x+=2*(x2-planet.x)
            planet.y+=2*(y2-planet.y)
    return planets
def change_color(planets):
    if color_mode=="normal":
        for planet in planets:
            for i in range(3):
                if planet.color[i]<255:
                    planet.color[i]+=color_change_rate
            
def push_away(planet1,planet2,distance):
    m1=planet1.mass
    m2=planet2.mass
    q=(planet1.radius+planet2.radius-distance)/(m1+m2)
    d1x=planet2.x-planet1.x
    d1y=planet2.y-planet1.y
    d2x=planet1.x-planet2.x
    d2y=planet1.y-planet2.y
    vector1x=d1x/distance
    vector1y=d1y/distance
    vector2x=d2x/distance
    vector2y=d2y/distance
    a1=(planet1.ax**2+planet1.ay**2)**(1/2)
    a2=(planet2.ax**2+planet2.ay**2)**(1/2)
    a1_=(q*m2-a1*t**2)/t**2
    a2_=(q*m1-a2*t**2)/t**2
    planet1.ax-=a1_*vector1x
    planet1.ay-=a1_*vector1y
    planet2.ax-=a2_*vector2x
    planet2.ay-=a2_*vector2y
def create_universe(b4):
    planets=[]
    scXscale=scale*speed_constant
    i=0
    if mode=="respawn":
        screen_radius=(x2**2+y2**2)**(1/2)
        while i<b4:
            alpha=random()*2*pi
            y=sin(alpha)*screen_radius*random()+y2
            x=cos(alpha)*screen_radius*random()+x2
            radius=randrange(radius_range[0],radius_range[-1]+1)*scale
            vx=scXscale*random()
            vy=scXscale*random()
            m=4/3*pi*density*radius**3
            if color_mode=="random":
                color=[randrange(0,256),randrange(0,256),randrange(0,256)]
            elif color_mode=="normal":
                color=[255,255,255]
            new_planet=planet(x,y,radius,m,color,choice([vx,-vx]),choice([vy,-vy]))
            for j in planets:
                if j.radius+new_planet.radius>=distance(j,new_planet):
                    break
            else:
                planets.append(new_planet)
                i+=1
        return planets
    elif mode=="reflect":
        while i<b4:
            radius=randrange(radius_range[0],radius_range[-1]+1)*scale
            y=scale*2*(random()*(y2-radius)+radius)
            x=scale*2*(random()*(x2-radius)+radius)
            vx=scXscale*random()
            vy=scXscale*random()
            m=4/3*pi*density*radius**3
            if color_mode=="random":
                color=[randrange(0,256),randrange(0,256),randrange(0,256)]
            elif color_mode=="normal":
                color=[255,255,255]
            new_planet=planet(x,y,radius,m,color,choice([vx,-vx]),choice([vy,-vy]))
            for j in planets:
                if j.radius+new_planet.radius>=find_distance(j,new_planet):
                    break
            else:
                planets.append(new_planet)
                i+=1
        return planets
def find_distance(planet1,planet2):
    return sqrt(pow(planet1.x-planet2.x,2)+pow(planet1.y-planet2.y,2))
def acceleration(planet1,planet2):
    m1=planet1.mass
    m2=planet2.mass
    d1x=planet2.x-planet1.x
    d1y=planet2.y-planet1.y
    distance_square=d1x**2+d1y**2
    force=m1*m2/distance_square#*G# is ignored. to use G in calculations, delete the first hashtag. G is the gravitational constant.
    vector1x=d1x/sqrt(distance_square)
    vector1y=d1y/sqrt(distance_square)
    planet1.ax+=force/m1*vector1x
    planet1.ay+=force/m1*vector1y
    planet2.ax-=force/m2*vector1x
    planet2.ay-=force/m2*vector1y
def draw_shape(canv,x,y,radius,color):
    return canv.create_oval((x-radius)/scale,(y-radius)/scale,(x+radius)/scale,(y+radius)/scale,width=1,fill=color,outline=color)
def redraw_shape(canv,item,x,y,radius,color):
    canv.itemconfig(item,fill=rgb_color(color),outline=outline_rgb(color))
    canv.coords(item,(x-radius)/scale,(y-radius)/scale,(x+radius)/scale,(y+radius)/scale)
def rgb_color(rgb):
    return f'#%02x%02x%02x' %(int(rgb[0]),int(rgb[1]),int(rgb[2]))
def outline_rgb(rgb):
    return f'#%02x%02x%02x' %(int((rgb[0]+bgcolor[0])/2),int((rgb[1]+bgcolor[1])/2),int((rgb[2]+bgcolor[2])/2))
def delete(canvas,my_shapes,planets,j):
    canvas.delete(my_shapes[j])
    del my_shapes[j]
    del planets[j]
def find(x,y,planets):
    for j in range(len(planets)):
        if pow(scale*x-planets[j].x,2)+pow(scale*y-planets[j].y,2)<planets[j].radius**2:
            return j
    else:
        return False
def collision(planet1,planet2,d):
    if collision_mode==1:
        push_away(planet1,planet2,d)
    elif collision_mode==2:
        dot=(planet1.vx-planet2.vx)*(planet1.x-planet2.x)+(planet1.vy-planet2.vy)*(planet1.x-planet2.x)
        a=pow(planet1.x-planet2.x,2)+pow(planet1.y-planet2.y,2)
        dot_over_a=0 if a==0 else dot/a
        sumofmasses=planet2.mass+planet1.mass
        c1=planet1.vx**2+planet1.vy**2-2*planet2.mass/sumofmasses*dot_over_a
        c2=planet2.vx**2+planet2.vy**2-2*planet1.mass/sumofmasses*dot_over_a
        planet1.vx=c1*(planet1.x-planet2.x)
        planet1.vy=c1*(planet1.y-planet2.y)
        planet2.vx=c2*(planet2.x-planet1.x)
        planet2.vy=c2*(planet2.y-planet1.y)

def gravity_inside(planet1,planet2):
    m1=planet1.mass
    m2=planet2.mass
    d1x=planet2.x-planet1.x
    d1y=planet2.y-planet1.y
    distance_square=d1x**2+d1y**2
    if distance_square:
        sum_or_radii=planet1.radius+planet2.radius
        force=sqrt(distance_square)*m1*m2/sum_or_radii**3#*G# is ignored. to use G in calculations, delete the first hashtag. G is the gravitational constant.
        vector1x=d1x/sqrt(distance_square)
        vector1y=d1y/sqrt(distance_square)
        planet1.ax+=force/m1*vector1x
        planet1.ay+=force/m1*vector1y
        planet2.ax-=force/m2*vector1x
        planet2.ay-=force/m2*vector1y