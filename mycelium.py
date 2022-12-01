from lib.lib_mycelium import Mycelium
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    args = parser.parse_args()

    mushroom = Mycelium(args.domain)
    mushroom.grow()
 
    print("~~~~~~~~~ Initial List ~~~~~~~~~")    
    print(mushroom.fqdn_list)
    print("~~~~~~~~~ Additional List ~~~~~~~~~")  
    print(mushroom.additionnal_list)
    print("~~~~~~~~~ The end ~~~~~~~~~") 