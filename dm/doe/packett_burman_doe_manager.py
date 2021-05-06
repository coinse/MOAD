import pyDOE
import logging
import numpy as np
from .doe_manager import DoEManager

root_logger = logging.getLogger()


class PackettBurmanDoEManager(DoEManager):

    def __init__(self, factor_manager, response_manager, max_expr,
                 plan_path=None, expr_idx_range=None):
        super().__init__(factor_manager, response_manager, max_expr,
                         plan_path, expr_idx_range)

    def _init_factor_queue(self, plan_path=None, expr_idx_range=None):
        if plan_path is not None and expr_idx_range is not None:
            super()._init_factor_queue(plan_path, expr_idx_range)
        else:
            # Cannot handle all cases
            factor_list = np.flip(pyDOE.pbdesign(self._factor_size), 0)
            for factor in factor_list:
                factor[factor == 1] = 0
                factor[factor == -1] = 1
                self.add_factor(factor.astype(int).tolist())
            self._expr_idx_range = range(self.qsize)
