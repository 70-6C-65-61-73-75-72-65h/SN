import os
import shutil
import _drop_tables
_drop_tables.do()

# drop cache
try:
    path = os.getcwd()
    files = []
    path_migrations = []
    # r=root, d=directories, f = files
    p_perms = ["__init__.py", "settings.py", "migrations"]
    packs = list(map(lambda x: x[0].split('\\')[-1] if p_perms[0] 
        in x[2] and p_perms[1] not in x[2] else None, os.walk(path)))
    packs = list(filter(lambda x: x is not None and x != p_perms[2] , packs))
    # print(packs)
    for r, d, f in os.walk(path):
        for file in f:
            if '.pyc' in file:
                files.append(os.path.join(r, file))
        for dirictory in d:
            print(f'\n\nto delete {d}\n\n')
            if dirictory == 'migrations':
                path_migrations.append(os.path.join(r, dirictory))
    for f in files:
        print(f)
        os.remove(f)
        
    print(f'\n\n\n\nmigrations: {path_migrations}\n\n')
    list(map(shutil.rmtree, path_migrations)) # , ignore_errors=True - delete read-only files
except Exception as ex:
    print('cache already deleted')
    print(ex)

# create db
try: 

    accounts_index = packs.index('accounts') # 'posts' - name of posts app
    accounts = packs[accounts_index]

    os.system(f'mkdir {accounts}\migrations')
    os.system(f'type nul > {accounts}\migrations\__init__.py')
    os.system('manage.py migrate')
    os.system('manage.py makemigrations')
    os.system('manage.py migrate')

    del packs[accounts_index]


    snu_index = packs.index('snusers') # 'posts' - name of posts app
    snu = packs[snu_index]

    os.system(f'mkdir {snu}\migrations')
    os.system(f'type nul > {snu}\migrations\__init__.py')
    os.system('manage.py migrate')
    os.system('manage.py makemigrations')
    os.system('manage.py migrate')

    del packs[snu_index] 

    # # then all others
    for pack in packs:
        os.system(f'mkdir {pack}\migrations')
        os.system(f'type nul > {pack}\migrations\__init__.py')
        os.system('manage.py migrate')
        os.system('manage.py makemigrations')
        os.system('manage.py migrate')

except Exception as ex:
    print('nu tu i durak')
    print(ex)

# create su
try:
    print('\n\nSU CREATING\n\n')
    os.system('manage.py shell <_auto/_csu.py')
    os.system('manage.py shell <_auto/_up.py') 
    os.system('manage.py runserver 0.0.0.0:8000')
except Exception as ex:
    print('nu tu i durak')
    print(ex)