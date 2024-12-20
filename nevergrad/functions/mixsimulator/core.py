# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Based on https://github.com/Foloso/MixSimulator

from .. import base


class OptimizeMix(base.ExperimentFunction):
    """
    MixSimulator is an application with an optimization model for calculating
    and simulating the least cost of an energy mix under certain constraints.

    For now, it uses a default dataset (more will be added soon).

    For more information, visit : https://github.com/Foloso/MixSimulator

    Parameters
    ----------
    time: int
        total time over which it evaluates the mix (must be in hour)

    """

    def __init__(self, time: int = 8760) -> None:
        try:
            from mixsimulator.MixSimulator import MixSimulator  # pylint: disable=import-outside-toplevel
            from mixsimulator.Demand import Demand

            self._mix = MixSimulator()
            self._mix.set_data_to("Toamasina")
            self._demand = Demand()
            self._demand.set_data_to("Toamasina", delimiter=",")
            self._mix.set_demand(self._demand)

        except (KeyError, AttributeError, ModuleNotFoundError) as e:
            # send a skip error so that this does not break the test suit
            raise base.UnsupportedExperiment("mixsimulator dependency issue") from e
        self._mix.set_penalisation_cost(100)
        self._mix.set_carbon_cost(10)
        parameters = self._mix.get_opt_params(time)
        parameters.set_name("dims")
        super().__init__(self._mix.loss_function, parameters)
