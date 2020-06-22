import os
from collections import defaultdict

LEVEL = 9
BASEDIR = os.path.abspath(os.path.dirname(__file__))
PYRAMID_STEP = os.path.join(BASEDIR, "pyramid_step.py")
OVERLAY_TILES = os.path.join(BASEDIR, "overlay_tiles.py")

def find_tiles(tiledir):
    for xdir in os.listdir(tiledir):
        try:
            x = int(xdir)
        except ValueError:
            continue
        for filename in os.listdir(os.path.join(tiledir, xdir)):
            base, ext = os.path.splitext(filename)
            y = int(base)
            yield (x,y)

def make_pyramides(basedir, level, tiles):
    if level == 0:
        return
    tiles = set(tiles)
    next_tiles = set((int(x/2), int(y/2)) for x, y in tiles)
    def intile_name(x, y):
        if (x, y) in tiles:
            return os.path.join(basedir, str(level), str(x), "%d.png"%y)
        else:
            return "-"
    def outtile_name(x, y):
        return os.path.join(basedir, str(level-1), str(x), "%d.png"%y)
    for x, y in next_tiles:
        innames = [intile_name(2*x+sx, 2*y+sy) for sx, sy in [(0,0), (0, 1), (1, 0), (1, 1)]]
        indeps = [inname for inname in innames if inname != "-"]
        print(outtile_name(x, y) + ": " + (" ".join(indeps)))
        print("\t${PYRAMID_STEP} $@ " + (" ".join(innames)))
        print()
    make_pyramides(basedir, level-1, next_tiles)

def _main():
    import sys
    if len(sys.argv) < 3:
        print("usage: generate_tile_makefile.py <BASEDIR> <OUTDIR>")
        exit(-1)
    basedir = sys.argv[1]
    outdir = sys.argv[2]
    layers = sorted(os.listdir(basedir))
    layers_by_tile = defaultdict(list)
    for layer in layers:
        for tile in find_tiles(os.path.join(basedir, layer, str(LEVEL))):
            layers_by_tile[tile].append(layer)
    def outname(x, y):
        return os.path.join(outdir, str(LEVEL), str(x), str(y)+".png")
    def inname(layer, x, y):
        return os.path.join(basedir, layer, str(LEVEL), str(x), str(y)+".png")
    yvals_by_x = defaultdict(list)
    for x, y in layers_by_tile.keys():
        yvals_by_x[x].append(y)

    print("PYRAMID_STEP=python3 \"{}\"".format(PYRAMID_STEP))
    print("OVERLAY_TILES=python3 \"{}\"".format(OVERLAY_TILES))
    print()
    print("all: " + os.path.join(outdir, "0", "0", "0.png"))
    print(".PHONY: all")
    print()
    make_pyramides(outdir, LEVEL, layers_by_tile.keys())
    for (x, y), layers in sorted(layers_by_tile.items()):
        print(outname(x, y) + ": " + (" ".join(inname(layer, x, y) for layer in sorted(layers))))
        print("\t${OVERLAY_TILES} $@ $^")
        print()


if __name__ == '__main__':
    _main()