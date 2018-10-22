import yaml
import os

config_path = os.path.dirname(os.path.realpath(__file__))

# read slurm cfg
slurm_cfg_file = os.path.join(config_path, 'slurm.yml')
slurm_cfg_dict = dict()
with open(slurm_cfg_file) as f:
    slurm_configs = yaml.load(f)
    for c, v in slurm_configs.items():
        slurm_cfg_dict[c] = v

# read paths and cmds
params_file = os.path.join(config_path, 'default_params.yml')
with open(params_file) as f:
    param_configs = yaml.load(f)
    for c, v in param_configs.items():
        globals()[c] = v
