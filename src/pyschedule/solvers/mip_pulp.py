#! /usr/bin/python
from __future__ import absolute_import as _absolute_import
from __future__ import print_function

'''
Copyright 2015 Tim Nonner

Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''


"""
a simple interface to pulp which is also an interface blueprint for potential other mip-interfaces
"""

import pulp as pl
import time

from pyschedule.solvers.pulp_scip import SCIP_CMD

class MIP(object):
    """
    Interface to pulp mip solver
    """

    def __init__(self,name,kind='Minimize'):
        kinds = {'Minimize':pl.LpMinimize, 'Maximize':pl.LpMaximize}
        self.mip = pl.LpProblem(name, kinds[kind])

    def var(self,name,low=0,up=0,cat='Binary'):
        return pl.LpVariable(name, low, up, cat=cat)

    def con(self,affine,sense=0,rhs=0):
        con = pl.LpConstraint(pl.LpAffineExpression(affine),sense=sense,rhs=rhs)
        self.mip += con
        return con

    def obj(self,affine):
        self.mip += pl.LpAffineExpression(affine)

    def solve(self,msg=0,**kwarg):
        kind = 'CBC'
        if 'kind' in kwarg:
            kind = kwarg['kind']
        time_limit = None
        if 'time_limit' in kwarg:
            time_limit = kwarg['time_limit']
        random_seed = None
        if 'random_seed' in kwarg:
            random_seed = kwarg['random_seed']
        ratio_gap = None
        if 'ratio_gap' in kwarg:
            ratio_gap = kwarg['ratio_gap']
        start_time = time.time()
        # select solver for pl
        if kind == 'CPLEX':
            if time_limit is not None:
                # pulp does currently not support a timelimit in 1.5.9
                self.mip.solve(pl.CPLEX_CMD(msg=msg, timelimit=time_limit))
            else:
                self.mip.solve(pl.CPLEX_CMD(msg=msg))
        elif kind == 'GLPK':
            self.mip.solve(pl.GLPK_CMD(msg=msg))
        elif kind == 'SCIP':
                self.mip.solve(SCIP_CMD(msg=msg))
        elif kind == 'CBC':
            options = []
            if time_limit is not None:
                options.extend(['sec', str(time_limit)])
            if random_seed is not None:
                options.extend(['randomSeed', str(random_seed)])
                options.extend(['randomCbcSeed', str(random_seed)])
            if ratio_gap is not None:
                options.extend(['ratio', str(ratio_gap)])
            self.mip.solve(pl.PULP_CBC_CMD(msg=msg, options=options))
        else:
            raise Exception('ERROR: solver ' + kind + ' not known')

        if msg:
            print('INFO: execution time for solving mip (sec) = ' + str(time.time() - start_time))
        if self.mip.status == 1 and msg:
            print('INFO: objective = ' + str(pl.value(self.mip.objective)))

    def status(self):
        return self.mip.status

    def value(self,var):
        return var.varValue
