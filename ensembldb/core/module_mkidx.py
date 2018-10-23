#!/usr/bin/env python

import luigi
from luigi.util import requires, inherits
from ensembldb.core.utils import SimpleTask, Prepare
from ensembldb.core import config
from pathlib import PurePath
import os


script_dir, script_name = os.path.split(os.path.abspath(__file__))
MODULE, _ = os.path.splitext(script_name)


class Pubvar:
    _module = MODULE


class MkindexPrepare(Prepare, Pubvar):
    genome_fa = luigi.Parameter()
    genome_gtf = luigi.Parameter()
    genome_exon_fa = luigi.Parameter()


@requires(MkindexPrepare)
class MkindexKallisto(SimpleTask, Pubvar):

    def treat_parameter(self):
        index_dir = os.path.join(self.proj_dir,
                                 config.module_dir[self._module]['main'])
        tr_name = os.path.basename(self.genome_exon_fa)
        self.index_path = os.path.join(index_dir,
                                       '{}.kallisto_idx'.format(tr_name))


@requires(MkindexPrepare)
class MkindexStar(SimpleTask, Pubvar):

    def treat_parameter(self):
        self.index_path = os.path.join(self.proj_dir,
                                       config.module_dir[self._module]['star'])


@inherits(MkindexPrepare)
class Mkindex(SimpleTask, Pubvar):

    index = luigi.Parameter(default='kallisto,star')

    def requires(self):
        INDEX_MD_DICT = {
            'kallisto': MkindexKallisto,
            'star': MkindexStar
        }

        index_list = self.index.split(',')
        index_jobs = []
        for each_index in index_list:
            index_jobs.append(
                INDEX_MD_DICT[each_index](genome_fa=self.genome_fa,
                                          genome_gtf=self.genome_gtf,
                                          genome_exon_fa=self.genome_exon_fa,
                                          proj_dir=self.proj_dir,
                                          slurm=self.slurm))
        return index_jobs


if __name__ == '__main__':
    luigi.run()
