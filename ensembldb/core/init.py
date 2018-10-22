from pathlib import Path
import shutil
import os
import sqlite3
import sys


CFG_TEMPLATE = '''
# ENSEMBL DB ENV
export ENSEMBL_DB_PATH={variable_path}
'''

SHELL_CFG = {
    'zsh': '.zshrc',
    'bash': '.bash_profile'
}


SQLIT_TABLE_COL = [
    'species',
    'version',
    'kingdom',
    'user',
    'update_time'
]

if sys.version_info >= (3, 5):
    HOME_DIR = Path().home()
else:
    HOME_DIR = Path(os.path.expanduser('~'))


class EnsSQL:

    def __init__(self, db_path):
        self.db_path = str(db_path)

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is AssertionError:
            print('Wrong database to use.')
        self.cur.close()
        self.conn.close()

    def check(self):
        self.cur.execute("SELECT * FROM {}".format('ensembldb'))
        col_name_list = [tuple[0] for tuple in self.cur.description]
        assert col_name_list == ['species', 'version',
                                 'kingdom', 'user', 'update_time']

    def create(self):
        creat_cmd = '''CREATE TABLE IF NOT EXISTS ensembldb(species text,
version text, kingdom text, user text, update_time timestamp)'''
        self.cur.execute(creat_cmd)


def backup_file(file_path):
    file_path = Path(file_path)
    back_file = file_path.with_suffix('{}.backup'.format(file_path.suffix))
    shutil.copyfile(file_path, back_file)


def setup_db_sqlit(db_path):
    db_path = Path(db_path)
    if not db_path.exists():
        db_path.mkdir(parents=True)
    sql_file = db_path / 'ensembldb.sql'
    ensdb = EnsSQL(sql_file)
    with ensdb:
        ensdb.create()
        ensdb.check()
    print('#ensembldb database settled.')


def shell_cfg_path():
    sys_shell = Path(os.environ['SHELL']).name
    return HOME_DIR / SHELL_CFG[sys_shell]


def setup_db_env(variable_path):
    variable_name = 'ENSEMBL_DB_PATH'
    write_flag = 1
    shell_cfg_file = shell_cfg_path()
    backup_file(shell_cfg_file)
    with open(shell_cfg_file) as cfg_inf:
        for eachline in cfg_inf:
            if variable_name in eachline:
                write_flag = 0
    if write_flag:
        with open(shell_cfg_file, 'a') as cfg_inf:
            cfg_inf.write(CFG_TEMPLATE.format(**locals()))
    if variable_name not in os.environ:
        print('#You need to refresh your environment variables')
        print('#Please run above command before next step:')
        print('source {}'.format(shell_cfg_file))
    else:
        print('#environment variable setted.')
