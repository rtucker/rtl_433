#!/usr/bin/python

# Power monitor decoder
# Takes output from rtl_433 -a and translates it into kW.

import numpy

# Mappings of readouts from power meter via RF (x) to displayed
# values on front panel (y).  Used to generate polynomial coefficients.
points = [
    (-99, 0.5),
    (-31, 0.8),
    (-30, 0.9),
    (-29, 0.9),
    (-27, 0.9),
    (-26, 0.9),
    (-25, 0.9),
    (-24, 0.9),
    (-22, 0.9),
    (-20, 0.9),
    (-19, 0.9),
    (-18, 1.0),
    (-17, 1.0),
    (-16, 1.0),
    (-14, 1.0),
    (-13, 1.0),
    (-11, 1.0),
    (-10, 1.1),
    (-9, 1.1),
    (-8, 1.1),
    (-7, 1.1),
    (-6, 1.1),
    (-5, 1.1),
    (-4, 1.1),
    (-3, 1.1),
    (-2, 1.2),
    (-1, 1.2),
    (0, 1.2),
    (1, 1.2),
    (2, 1.2),
    (3, 1.2),
    (4, 1.2),
    (5, 1.3),
    (6, 1.3),
    (7, 1.3),
    (8, 1.3),
    (9, 1.3),
    (10, 1.3),
    (11, 1.4),
    (12, 1.4),
    (14, 1.4),
    (16, 1.5),
    (17, 1.5),
    (18, 1.5),
    (20, 1.6),
    (21, 1.6),
    (22, 1.6),
    (24, 1.7),
    (27, 1.8),
    (32, 1.9),
    (33, 2.0),
    (42, 2.5),
    (43, 2.5),
    (44, 2.6),
    (45, 2.6),
    (46, 2.8),
    (49, 3.0),
    (52, 3.3),
]

# Unzip into x and y for use by interpolation.
x = [f[0] for f in points]
y = [f[1] for f in points]

# Offset x for more effective polynomial fit
offset = abs(min(x)) if min(x) < 0 else 0
xp = [xv+offset for xv in x]
coef = numpy.polyfit(xp, y, 5)


def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])


def compute(xv):
    #return numpy.interp(xv, x, y)
    return numpy.polyval(coef, xv+offset)


def get_values(linelist):
    for line in open('log.dat', 'r').readlines():
        if not line.startswith('['):
            continue

        line = line.strip()

        fields = line.split()

        if fields[1] != '{32}':
            continue

        index = fields[0]

        bytes = [b-2**8 if b > 2**7 else b
                 for b in [int(b, 16) for b in fields[2:7]]]

        if index == '[02]':
            guess = round(compute(bytes[2]), 3)
            yield bytes[2], guess


def main():
    for raw, kw in get_values(open('log.dat', 'r').readlines()):
        print '%3d = %3.3f kW%s' % (raw, kw, '' if raw in x else ' *')

if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt
    if len(sys.argv) > 1 and sys.argv[1] == 'plot':
        plt.plot(x, y)
        plt.show()
    elif len(sys.argv) > 1 and sys.argv[1] == 'fit':
        print coef
        py = [numpy.polyval(coef, xv) for xv in xp]
        plt.plot(xp, y)
        plt.plot(xp, py)
        plt.show()
    else:
        main()
