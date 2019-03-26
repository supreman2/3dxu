import re

from PIL import Image

import math


class point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, item):
        if item == 'x':
            return self.x
        elif item == 'y':
            return self.y
        elif item == 'z':
            return self.z
        else:
            return None

class tri:

    def __init__(self, point1, point2, point3, max_z, min_z, field):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.max_z = max_z
        self.min_z = min_z
        self.field = field

    def draw(self):

        # определяем левую, правую и среднюю точки (по оси Х)
        p1 = min([self.point1, self.point2, self.point3], key=lambda p: p.x)
        p3 = max([self.point1, self.point2, self.point3], key=lambda p: p.x)
        p2 = [p for p in [self.point1, self.point2, self.point3] if (p != p1 and p != p3)][0]

        # определяем приращение координат Y и Z для линий p1->p3, p1->p2, p2->p3
        dy12 = (p2.y - p1.y) / (p2.x - p1.x) if (p2.x - p1.x) != 0 else 0
        dz12 = (p2.z - p1.z) / (p2.x - p1.x) if (p2.x - p1.x) != 0 else 0

        dy13 = (p3.y - p1.y) / (p3.x - p1.x) if (p3.x - p1.x) != 0 else 0
        dz13 = (p3.z - p1.z) / (p3.x - p1.x) if (p3.x - p1.x) != 0 else 0

        dy23 = (p3.y - p2.y) / (p3.x - p2.x) if (p3.x - p2.x) != 0 else 0
        dz23 = (p3.z - p2.z) / (p3.x - p2.x) if (p3.x - p2.x) != 0 else 0

        # двигаемся по X от p1 до p2 и рисуем вертикальные линии от одной линии треугольника до другой
        y2 = p1.y
        y3 = p1.y

        z2 = p1.z
        z3 = p1.z

        for x in range(p1.x, p2.x + 1):

            if x >= 0 and x < scr_x:
                z = z2 if y2 < y3 else z3
                dz = (z3 - z2) / (int(y3) - int(y2)) if (int(y3) - int(y2)) != 0 else 0
                for y in range(int(min(y2, y3)), int(max(y2, y3)) + 1):
                    col = 50 + int(205 * (z - self.min_z) / (self.max_z - self.min_z))
                    if y >= 0 and y < scr_y:
                        infield = field.get((x,y))
                        if infield == None or infield < int(z):
                            canvas_pixels[x, y] = (col, col, col)
                            field[(x,y)] = int(z)
                    z = z + dz

            y2 = y2 + dy12
            y3 = y3 + dy13

            z2 = z2 + dz12
            z3 = z3 + dz13

        # двигаемся по X от p2 до p3 и рисуем вертикальные линии от одной линии треугольника до другой
        y2 = y2 - dy12 + dy23
        z2 = z2 - dz12 + dy23

        for x in range(p2.x + 1, p3.x + 1):

            if x >= 0 and x < scr_x:
                z = z2 if y2 < y3 else z3
                dz = (z3 - z2) / (int(y3) - int(y2)) if (int(y3) - int(y2)) != 0 else 0
                for y in range(int(min(y2, y3)), int(max(y2, y3)) + 1):
                    col = 50 + int(205 * (z - self.min_z) / (self.max_z - self.min_z))
                    if y >= 0 and y < scr_y:
                        infield = field.get((x, y))
                        if infield == None or infield < int(z):
                            canvas_pixels[x, y] = (col, col, col)
                            field[(x, y)] = int(z)
                    z = z + dz

            y2 = y2 + dy23
            y3 = y3 + dy13

            z2 = z2 + dz23
            z3 = z3 + dz13

def redef(p1, p2, p3, p4):

    if p1.x == p2.x and p1.x == p3.x and p1.x == p4.x or p1.y == p2.y and p1.y == p3.y and p1.y == p4.y:
        return None

    # если две точки совпадают, то одну повторяющуюся выкидываем
    for i in [p1, p2, p3, p4]:
        for j in [p1, p2, p3, p4]:
            if i != j and i.x == j.x and i.y == j.y:
                q = [p for p in [p1, p2, p3, p4] if p != i and p != j]
                return (i, q[0], q[1], None)

    # возвращаем такую последовательность точек, чтобы третья и четвертая были по разные стороны от линии первая-вторая
    for i in [(p1,p2,p3,p4), (p1,p3,p2,p4), (p1,p4,p2,p3), (p2,p3,p1,p4), (p2,p4,p1,p3), (p3,p4,p1,p2)]:
        if i[0].x == i[1].x:
            side1 = i[2].x > i[0].x
            side2 = i[3].x > i[0].x
        else:
            side1 = (i[1].y - i[0].y) / (i[1].x - i[0].x) * (i[2].x - i[0].x) + i[0].y > i[2].y
            side2 = (i[1].y - i[0].y) / (i[1].x - i[0].x) * (i[3].x - i[0].x) + i[0].y > i[3].y
        if side1 != side2:
            return i

    # значит ве четыре точки на одной линии, такое рисовать не надо
    return None

scr_x = 1000
scr_y = 1000
a = 5  # угол поворота - множитель для 45 градусов
k = 30 # коэффициент масштабирования
ver = 2 # версия вывода: 1 точки, 2 линии, 3 поверхности

img = Image.new('RGB', (scr_x, scr_y), 'black')
canvas_pixels = img.load()

#f = open('C:/3d mod/pjanic.obj')
f = open('C:/3d mod/skull/12140_Skull_v3_L2.obj')
lines = f.read()

# считаем точки из файла "как есть"
points = []
ab_points = []
ab_names = set()
polyg = []
for line in lines.split('\n'):
    words = re.split('\s+', line.strip())
    _len = len(words)
    if words[0] == 'v' and _len == 4:
        x = float(words[1])
        z = float(words[2])
        y = float(words[3])
        points.append(point(x, y, z))
    elif ver != 1 and words[0] == 'f' and (_len == 4 or _len == 5):
        # tops = []
        # for word in words:
        #     if word == 'f':
        #         continue
        #     elems = re.split('/', word)
        #     p = [int(elems[0]), int(elems[1])]
        #     tops.append(p)
        # polyg.append(tops)
        words.pop(0)
        a_name = re.split('/', words[-1])[0]
        for i in range(_len-1):
            b_name = re.split('/', words[i])[0]
            if a_name < b_name:
                ab_name = a_name + '/' + b_name
            else:
                ab_name = b_name + '/' + a_name
            if ab_name in ab_names:
                continue
            ab_names.add(ab_name)
            a_point = points[int(a_name) - 1]
            b_point = points[int(b_name) - 1]
            ab_points.append([a_point, b_point])
            a_name = b_name

# обработаем поворот
min_x = min(points, key=lambda p: p.x).x
max_x = max(points, key=lambda p: p.x).x
os_x = (max_x + min_x) / 2

min_y = min(points, key=lambda p: p.y).y
max_y = max(points, key=lambda p: p.y).y
os_y = (max_y + min_y) / 2

min_z = min(points, key=lambda p: p.z).z
max_z = max(points, key=lambda p: p.z).z
os_z = (max_z + min_z) / 2

sin = math.sin(math.pi / 4 * a)
cos = math.cos(math.pi / 4 * a)

for p in points:
    dx = p.x - os_x  # смещение относительно оси
    dy = p.y - os_y  # смещение относительно оси
    dz = p.z - os_z  # смещение относительно оси

    dx2 = int((dx * cos - dz * sin) * k + scr_x / 2)
    dy2 = scr_y - int(dy * k + scr_y / 2)
    dz2 = int((dz * cos + dx * sin) * k)
    p.x = dx2
    p.y = dy2
    p.z = dz2

# вывод
min_z = min(points, key=lambda p: p.z).z
max_z = max(points, key=lambda p: p.z).z
field = {}
if ver == 1:

    for p in points:

        if p.x < 0 or p.y < 0 or p.x >= scr_x or p.y >= scr_y:
            continue
        infield = field.get((p.x, p.y))
        if infield == None or infield < p.z:
            col = 50 + int(205 * (p.z - min_z) / (max_z - min_z))
            canvas_pixels[p.x, p.y] = (col, col, col)
            field[(p.x, p.y)] = p.z

elif ver == 2:

    for l in ab_points:

        if l[0].x < 0 and l[1].x < 0 or l[0].y < 0 and l[1].y < 0 or l[0].x >= scr_x and l[1].x >= scr_x or l[0].y >= scr_y and l[1].y >= scr_y:
            continue

        if abs(l[0].x - l[1].x) > abs(l[0].y - l[1].y):
            c1 = 'x'
            c2 = 'y'
        else:
            c1 = 'y'
            c2 = 'x'

        if l[0][c1] < l[1][c1]:
            p1 = l[0]
            p2 = l[1]
        else:
            p1 = l[1]
            p2 = l[0]

        # определяем приращение координат c2 и Z для линий p1->p2
        dc12 = (p2[c2] - p1[c2]) / (p2[c1] - p1[c1]) if (p2[c1] - p1[c1]) != 0 else 0
        dz12 = (p2.z - p1.z) / (p2[c1] - p1[c1]) if (p2[c1] - p1[c1]) != 0 else 0

        # двигаемся по c1 от p1 до p2 и рисуем точки
        _c2 = p1[c2]
        _z = p1.z

        for _c1 in range(p1[c1], p2[c1] + 1):

            if c1 == 'x':
                x = int(_c1)
                y = int(_c2)
            else:
                x = int(_c2)
                y = int(_c1)
            z = int(_z)

            if x < 0 or y < 0 or x >= scr_x or y >= scr_y:
                continue
            infield = field.get((x, y))
            if infield == None or infield < z:
                col = 50 + int(205 * (z - min_z) / (max_z - min_z))
                canvas_pixels[x, y] = (col, col, col)
                field[(x, y)] = z

            _c2 = _c2 + dc12
            _z = _z + dz12


# field = {}
# for t in polyg:
#     p1 = points[t[0][0] - 1]
#     p2 = points[t[1][0] - 1]
#     p3 = points[t[2][0] - 1]
#
#     if len(t) == 3:
#         tr = tri(p1, p2, p3, max_z, min_z, field)
#         tr.draw()
#     else: # len(t) == 4
#         p4 = points[t[3][0] - 1]
#         tr1 = tri(p1, p2, p3, max_z, min_z, field)
#         tr2 = tri(p2, p3, p4, max_z, min_z, field)
#         tr3 = tri(p3, p4, p1, max_z, min_z, field)
#         tr4 = tri(p4, p1, p2, max_z, min_z, field)
#         tr1.draw()
#         tr2.draw()
#         tr3.draw()
#         tr4.draw()

        #p4 = points[t[3][0] - 1]
        #p = redef(p1, p2, p3, p4)
        #if p != None:
#            p1, p2, p3, p4 = p
 #           if p4 == None:
#              tr = tri(p1, p2, p3, max_z, min_z, field)
 #               tr.draw()
  #          else:
   #             tr1 = tri(p1, p2, p3, max_z, min_z, field)
    #            tr2 = tri(p1, p2, p4, max_z, min_z, field)
     #           tr1.draw()
      #          tr2.draw()

img.show()
