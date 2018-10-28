import pandas as pd
import yaml
import os
import pkg_resources
from pathlib import PurePath


DATA_DIR = pkg_resources.resource_filename('ensembldb', 'data')


def load_cfg(cfg_file, cfg_dict):
    with open(cfg_file) as f:
        configs = yaml.load(f)
        for c, v in configs.items():
            cfg_dict[c] = v


# read slurm cfg
slurm_cfg_file = os.path.join(DATA_DIR, 'slurm.yml')
slurm_cfg_dict = dict()
load_cfg(slurm_cfg_file, slurm_cfg_dict)

# read paths and cmds
params_file = os.path.join(DATA_DIR, 'default_params.yml')
load_cfg(params_file, globals())

# read species db map
sp_db_file = os.path.join(DATA_DIR, 'plant_db.map')
sp_db_df = pd.read_table(sp_db_file, index_col=0)

# read ensembl db cfg
ens_db_cfg = os.path.join(DATA_DIR, 'db_cfg.yaml')
ens_db_dict = dict()
load_cfg(ens_db_cfg, ens_db_dict)


# ensembl db file path
class EnsemblFiles:

    def __init__(self, db_path, sp_latin, db_version):
        self.db_path = PurePath(db_path)
        self.sp = sp_latin
        self.db_version = db_version

    @property
    def gtf(self):
        gtf_file = '{t.sp}.{t.db_version}.genome.gtf'.format(
            t=self
        )
        return self.db_path / 'annotation' / self.db_version / gtf_file

    @property
    def genome_fa(self):
        genome_fa_file = '{t.sp}.{t.db_version}.genome.fa'.format(
            t=self
        )
        return self.db_path / 'annotation' / self.db_version / genome_fa_file
