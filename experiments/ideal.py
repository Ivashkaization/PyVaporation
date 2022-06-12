import typing
from pathlib import Path

import attr
import pandas

from component import AllComponents, Component
from permeance import Permeance, PermeanceUnits
from config import Config


@attr.s(auto_attribs=True)
class IdealExperiment:
    """
    Class for specification of Ideal experiments, where Permeance is assumed to be constant
    over considered composition range
    """

    name: str
    temperature: float
    component: Component  # TODO: use real components
    permeance: Permeance
    activation_energy: typing.Optional[float] = None
    comment: typing.Optional[str] = None

    def __attrs_post_init__(self):
        if not self.permeance.units == PermeanceUnits.kg_m2_h_kPa:
            self.permeance = self.permeance.convert(
                to_units=PermeanceUnits.kg_m2_h_kPa, component=self.component  # TODO: learn how to treat Enum!!!
            )

    @classmethod
    def from_dict(
        cls,
        d: typing.Mapping[str, typing.Union[str, float]],
        all_components: AllComponents,
    ) -> "IdealExperiment":
        component = getattr(all_components, d["component"])
        return cls(**d)

    # TODO Add check for units and conversion to kg/(m2*h*kPa) using Permeance.convert()


@attr.s(auto_attribs=True)
class IdealExperiments:
    experiments: typing.List[IdealExperiment]

    def __len__(self):
        return len(self.experiments)

    @classmethod
    def from_csv(cls, path: typing.Union[str, Path], all_components: AllComponents) -> "IdealExperiments":
        frame = pandas.read_csv(path)

        experiments = []
        for _, row in frame.iterrows():
            experiments.append(IdealExperiment.from_dict(row.to_dict(), all_components=all_components))

        return IdealExperiments(experiments=experiments)

    @classmethod
    def from_config(cls, config: Config) -> 'IdealExperiments':
        return cls.from_csv(config.ideal_experiment_path)
