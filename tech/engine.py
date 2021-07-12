from math import hypot, asin, cos, sin, pi


def step(space_objects=None, DT=1.0, G=1.0):
    for i in range(len(space_objects)):  # current
        i_obj = space_objects[i]
        for j in range(len(space_objects)):  # another
            if i == j or i_obj.coll or space_objects[j].coll:
                continue
            j_obj = space_objects[j]
            dx = j_obj.x - i_obj.x
            dy = j_obj.y - i_obj.y
            r = hypot(dx, dy)  # R
            if r > j_obj.r + i_obj.r:
                if r < 0.001: r = 0.001
                a = (G * j_obj.m) / (r * r)
                ax = a * dx / r  # a * cos
                ay = a * dy / r  # a * sin
                space_objects[i].vx += ax * DT
                space_objects[i].vy += ay * DT
            else:
                if r < j_obj.r + i_obj.r:  # moving an inbound object out of another
                    if i_obj.m <= j_obj.m:
                        space_objects[i].x += (j_obj.vx * DT +
                                               (j_obj.r + i_obj.r) - r) * (- dx / r)
                        space_objects[i].y += (j_obj.vy * DT +
                                               (j_obj.r + i_obj.r) - r) * (- dy / r)
                    else:
                        break
                    dx = j_obj.x - i_obj.x
                    dy = j_obj.y - i_obj.y
                    r = hypot(dx, dy)
                if r < 0.001: r = 0.001
                v1 = hypot(i_obj.vx, i_obj.vy)
                m1 = i_obj.m
                v2 = hypot(j_obj.vx, j_obj.vy)
                m2 = j_obj.m
                if v1:
                    F1 = asin(i_obj.vy / v1)
                else:
                    F1 = asin(0)
                if v2:
                    F2 = asin(j_obj.vy / v2)
                else:
                    F2 = asin(0)
                f = asin(dy / r)
                space_objects[i].vx = ((v1 * cos(F1 - f) * (m1 - m2) + 2 * m2 * v2 * cos(
                    F2 - f)) * cos(f)) / (m1 + m2) + v1 * sin(F1 - f) * cos(f + pi / 2)
                space_objects[i].vy = ((v1 * cos(F1 - f) * (m1 - m2) + 2 * m2 * v2 * cos(
                    F2 - f)) * sin(f)) / (m1 + m2) + v1 * sin(F1 - f) * sin(f + pi / 2)
                space_objects[j].vx = ((v2 * cos(F2 - f) * (m2 - m1) + 2 * m1 * v1 * cos(
                    F1 - f)) * cos(f)) / (m1 + m2) + v2 * sin(F2 - f) * cos(f + pi / 2)
                space_objects[j].vy = ((v2 * cos(F2 - f) * (m2 - m1) + 2 * m1 * v1 * cos(
                    F1 - f)) * sin(f)) / (m1 + m2) + v2 * sin(F2 - f) * sin(f + pi / 2)
                space_objects[i].coll = True
                break
                #if r < j_obj.r + i_obj.r and i_obj.m <= j_obj.m:  # moving an inbound object out of another
                #  a = (5 * 10 ** -9 * i_obj.m) / (r * r)
                #  ax = - a * dx / r  # a * cos
                #   ay = - a * dy / r  # a * sin
                #   space_objects[i].vx += ax * DT
                #   space_objects[i].vy += ay * DT
                #else:
                #  break
        else:
            space_objects[i].coll = False
    for i in range(len(space_objects) - 1, -1, -1):
        space_objects[i].x += space_objects[i].vx * DT
        space_objects[i].y += space_objects[i].vy * DT
        if abs(space_objects[i].x) > 10 ** 12 or abs(space_objects[i].y) > 10 ** 12:
            space_objects.pop(i)
