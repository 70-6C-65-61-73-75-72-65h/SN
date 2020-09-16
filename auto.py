import os
import sys
# -u - update # nothing or l - load
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BASE_DIR)
def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-u':
            try:
                os.system(BASE_DIR+'\_auto\_ddb.py') # send in **kwargs all packages but not main ( with settings.py )
            except Exception as ex:
                print(ex)
    elif len(sys.argv) == 1:
            try:
                os.system('manage.py runserver 0.0.0.0:8000')
            except Exception as ex:
                print(ex)

if __name__=='__main__':
    main()