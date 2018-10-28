#!/usr/bin/env python

import luigi
from luigi.util import requires, inherits
from ensembldb.core.utils import SimpleTask, Prepare
from ensembldb.core import config
import os
from pathlib import Path


script_dir, script_name = os.path.split(os.path.abspath(__file__))
MODULE, _ = os.path.splitext(script_name)


class Pubvar:
    _module = MODULE


class DlGenomePrepare(Prepare, Pubvar):
    sp_latin = luigi.Parameter()
    db_version = luigi.Parameter()


@requires(DlGenomePrepare)
class DlGenomeDownload(SimpleTask, Pubvar):
    slurm = False

    def treat_parameter(self):
        self.dl_dir = os.path.join(self.proj_dir,
                                   config.module_dir[self._module]['download'])


@inherits(DlGenomePrepare)
class DlGenomeFormatdb(SimpleTask, Pubvar):

    def requires(self):
        return DlGenomeDownload(proj_dir=self.proj_dir,
                                sp_latin=self.sp_latin,
                                db_version=self.db_version)

    def treat_parameter(self):
        self.proj_dir = Path(self.proj_dir).resolve()
        self.anno_dir = config.module_dir[self._module]['annotation']
        self.download_dir = config.module_dir[self._module]['download']
        self.genome_fa = '{sp}.{ve}.genome.fa'.format(
            sp=self.sp_latin, ve=self.db_version)
        self.genome_gtf = '{sp}.{ve}.genome.gtf'.format(
            sp=self.sp_latin, ve=self.db_version)


@requires(DlGenomeFormatdb)
class DlGenomeMetatable(SimpleTask, Pubvar):

    def treat_parameter(self):
        self.proj_dir = Path(self.proj_dir).resolve()
        self.db_obj = config.EnsemblFiles(self.proj_dir,
                                          self.sp_latin,
                                          self.db_version)


if __name__ == '__main__':
    luigi.run()
