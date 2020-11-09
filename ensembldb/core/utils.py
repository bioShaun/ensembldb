import subprocess
import luigi
from .slurmpy import Slurm
from . import config
import envoy
import os
import time
import asyncio
import aioftp


def check_slurm_job(job_ids):
    while True:
        running_jobs = set()
        # python2 don not need decode
        job_inf = subprocess.check_output('squeue').decode().split('\n')
        for each_job in job_inf[1:]:
            if each_job.strip() != '':
                each_job_id = int(each_job.split()[0])
                running_jobs.add(each_job_id)
        if not running_jobs.intersection(set(job_ids)):
            break
        time.sleep(10)


class Prepare(luigi.Task):

    proj_dir = luigi.Parameter()
    slurm = luigi.BoolParameter()

    def run(self):
        prepare_dir_log_list = []
        for each_module in config.module_dir[self._module]:
            each_module_dir = os.path.join(
                self.proj_dir, config.module_dir[self._module][each_module])
            if not self.slurm:
                if 'slurm' in os.path.basename(each_module_dir):
                    continue
            try:
                os.makedirs(each_module_dir)
            except OSError:
                prepare_dir_log_list.append(
                    '{_dir} has been built before.\n'.format(
                        _dir=each_module_dir
                    ))
        with self.output().open('w') as prepare_dir_log:
            for eachline in prepare_dir_log_list:
                prepare_dir_log.write(eachline)

    def output(self):
        return luigi.LocalTarget('{t.proj_dir}/{_dir}/prepare_dir.log'.format(
            t=self, _dir=config.module_dir[self._module]['logs']))


class SimpleTask(luigi.Task):

    _tag = 'analysis'
    proj_dir = luigi.Parameter()
    venv = ''
    _py = False

    def get_tag(self):
        return self._tag

    def treat_parameter(self):
        pass

    def run(self):
        self.treat_parameter()
        class_name = self.__class__.__name__
        _run_cmd = config.module_cmd[self._module][class_name].format(
            t=self)
        if not self.slurm:
            _process = envoy.run(_run_cmd)
            log_out = "cmd:\n{cmd}\n\nstd_err:\n{se}".format(
                cmd=_run_cmd, se=_process.std_err)
        else:
            check_bash_var = True
            _run_cmd_list = [each.strip() for each in _run_cmd.split('|')]
            _run_cmd = '\n'.join(_run_cmd_list)
            if self.venv:
                check_bash_var = False
                _run_cmd = '''\
source `which virtualenvwrapper.sh`
workon {t.venv}
{cmd}
'''''.format(t=self, cmd=_run_cmd)
            slurm_scripts_dir = os.path.join(self.proj_dir,
                                             config.module_dir[self._module]['slurm_scripts'])
            slurm_log_dir = os.path.join(self.proj_dir,
                                         config.module_dir[self._module]['slurm_logs'])
            s = Slurm(class_name, config.slurm_cfg_dict[self._module][class_name],
                      check_bash_var=check_bash_var,
                      scripts_dir=slurm_scripts_dir,
                      log_dir=slurm_log_dir)
            s_id = s.run(_run_cmd)
            check_slurm_job([s_id])
            log_out = '{} finished!'.format(s_id)
        with self.output().open('w') as slurm_task_log:
            slurm_task_log.write(log_out)

    def output(self):
        tag = self.get_tag()
        class_name = self.__class__.__name__
        return luigi.LocalTarget('{t.proj_dir}/{_dir}/{name}.{tag}.log'.format(
            t=self, _dir=config.module_dir[self._module]['logs'],
            name=class_name, tag=tag
        ))


def get_sp_db_inf(sp_latin):
    if sp_latin in config.sp_db_df.index:
        ens_db_name = config.sp_db_df.loc[sp_latin, 'division']
    else:
        ens_db_name = 'Ensembl'
    return ens_db_name, config.ens_db_dict[ens_db_name]


async def get_db_version(host, species, version, start_path='/pub/',
                         db_name='Ensembl'):
    print(host)
    if version != 'current':
        return version
    else:
        if db_name == 'Ensembl':
            path = '{start}/current_fasta/{sp}/cds/'.format(
                sp=species, start=start_path
            )
        else:
            path = '{start}/{ver}/fasta/{sp}/cds/'.format(
                ver=version, sp=species, start=start_path
            )
        async with aioftp.ClientSession(host) as client:
            await client.change_directory(path)
            path_name = await client.get_current_directory()
            return str(path_name).split('/')[2].split('-')[-1]
