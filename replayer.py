from __future__ import print_function
import pickle
import sys
import glob
import os
import domination

# Run a replay from the command line
# Usage: python replayer.py PATH [-g for endered view]
# If PATH is directory, all replay files in the directory are played

def main():
    graphic = "-g" in sys.argv
    if os.path.isdir(sys.argv[1]):
    	files = glob.glob(os.path.join(sys.argv[1], "*.replay"))
        for f in files:
            fname = f.split("/")[-1]
            for i in range(15 + len(fname)):
                print("-", end="")
            print("\nReplaying now: " + fname)
            for i in range(15 + len(fname)):
                print("-", end="")
            print()
            run_replay(f, graphic=graphic)
    else:
        run_replay(sys.argv[1], graphic=graphic)


def run_replay(path, graphic=False):
    rendered = graphic
    verbose = not graphic
    openfile = open(path, "rb")
    g = domination.core.Game(replay=pickle.load(openfile), rendered=rendered, verbose=verbose).run()
    print(g.stats)


if __name__ == "__main__":
    main()
