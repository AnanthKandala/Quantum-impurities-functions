from run_functions import run_check_func
import os

if __name__ == "__main__":
    pwd = os.getcwd()
    print(pwd)
    run_check_func(pwd)
    os.system('cat STATUS.txt')
