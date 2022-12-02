from lib.lib_mycelium import Mycelium
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    parser.add_argument("--CSV", help="format output to CSV",action="store_true")
    args = parser.parse_args()

    mushroom = Mycelium(args.domain)
    mushroom.grow()

    if args.CSV:
        mushroom.CSV_output()
    else:
        mushroom.std_output()
