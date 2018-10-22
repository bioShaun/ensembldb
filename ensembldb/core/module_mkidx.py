#!/usr/bin/env python

import luigi
from luigi.util import requires
from ensembldb.core.utils import SimpleTask, Prepare
from pathlib import PurePath
import os


script_dir, script_name = os.path.split(os.path.abspath(__file__))
MODULE, _ = os.path.splitext(script_name)


class Pubvar:
    _module = MODULE


class MkindexPrepare(Prepare, Pubvar):
    genome_fa = luigi.Parameter()
    genome_gtf = luigi.Parameter()


@requires(MkindexPrepare)
class MkindexExtr(SimpleTask, Pubvar):

    def treat_parameter(self):
        self.genome_fa = PurePath(self.genome_fa)
        self.genome_exon_fa = self.genome_fa.with_suffix('.exon.fa')
        self.genome_cds_fa = self.genome_fa.with_suffix('.cds.fa')
        self.genome_pep_fa = self.genome_fa.with_suffix('.pep.fa')


@requires(MkindexPrepare)
class MkindexKallisto(MkindexExtr):
    pass


@requires(MkindexPrepare)
class MkindexStar(SimpleTask, Pubvar):
    pass


if __name__ == '__main__':
    luigi.run()
