from pathlib import Path
import shutil
import os
import sqlite3
import sys
from prompt_toolkit.validation import Validator
from prompt_toolkit import prompt

CFG_TEMPLATE = '''\
export ENSEMBL_DB_PATH={}
'''

SHELL_CFG = [
    '.zshrc',
    '.bash_profile',
]


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


def is_right_choice(text):
    choice = ['y', 'n', 'yes', 'no']
    return text in choice


PROMOT_VAL = Validator.from_callable(
    is_right_choice,
    error_message='not legal choice',
    move_cursor_to_end=True
)

PROMOT_MSG = 'Reset ENSEMBL_DB_PATH from ({old}) to ({new})? [y/n]:'


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
    for each in HOME_DIR.iterdir():
        if each.name in SHELL_CFG:
            return each
    return HOME_DIR / '.bashrc'


def setup_db_env(variable_path):
    variable_name = 'ENSEMBL_DB_PATH'
    write_flag = 1
    shell_cfg_file = shell_cfg_path()
    ens_path_cfg = CFG_TEMPLATE.format(variable_path)
    backup_file(shell_cfg_file)
    with open(shell_cfg_file) as cfg_inf:
        cfg_list = cfg_inf.readlines()
        cp_cfg_list = cfg_list[:]
        for n, eachline in enumerate(cp_cfg_list):
            if variable_name in eachline:
                write_flag = 0
                old_cfg = eachline.split('ENSEMBL_DB_PATH=')[1].strip()
                msg = PROMOT_MSG.format(
                    old=old_cfg, new=variable_path
                )
                choice = prompt(
                    msg, validator=PROMOT_VAL)
                if choice in ['y', 'yes']:
                    cfg_list[n] = ens_path_cfg
    if write_flag:
        cfg_list.append(ens_path_cfg)
    with open(shell_cfg_file, 'w') as cfg_inf:
        cfg_inf.write(''.join(cfg_list))
    if variable_name not in os.environ:
        print('#You need to refresh your environment variables')
        print('#Please run above command before next step:')
        print('source {}'.format(shell_cfg_file))
    else:
        print('#environment variable setted.')
