from pathlib import Path
import shutil
import os

DB_CFG = '''
# ENSEMBL DATABASE PATH
export ENSEMBL_DB_PATH={}
'''

SHELL_CFG = {
    'zsh': '.zshrc',
    'bash': '.bash_profile'
}


HOME_DIR = Path().home()


def backup_file(file_path):
    file_path = Path(file_path)
    back_file = file_path.with_suffix('{file_path.suffix}.backup')
    shutil.copyfile(file_path, back_file)


def setup_db_env(db_path):
    sys_shell = Path(os.environ['SHELL']).name
    shell_cfg_file = HOME_DIR / SHELL_CFG[sys_shell]
    backup_file(shell_cfg_file)
    with open(shell_cfg_file, 'a') as cfg_inf:
        cfg_inf.write(DB_CFG.format(db_path))
