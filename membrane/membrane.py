import typing

import attr
import numpy

from component import Component
from diffusion_curve import DiffusionCurveSet
from experiments import IdealExperiments
from permeance import Permeance, PermeanceUnits
from utils import R


@attr.s(auto_attribs=True)
class Membrane:
    name: str
    ideal_experiments: typing.Optional[IdealExperiments] = None
    diffusion_curve_sets: typing.Optional[typing.List[DiffusionCurveSet]] = None

    # TODO: non ideal experiments - Diffusion curves

    def get_penetrant_data(self, component: Component) -> IdealExperiments:
        """
        Gets all ideal experiments of the membrane for a specified Component
        """
        return IdealExperiments(
            experiments=list(
                filter(
                    lambda x: x.component.name == component.name,
                    self.ideal_experiments.experiments,
                )
            )
        )

    def calculate_activation_energy(
        self,
        component: Component,
    ) -> float:
        """
        Calculates Apparent Activation Energy of Transport i J/mol
        for a specified component, based on its Ideal Experiments.
        Activation energy is assumed to be independent of concentration for Ideal Process

        """
        component_experiments = self.get_penetrant_data(component)
        stated_activation_energy = component_experiments.experiments[
            0
        ].activation_energy

        if len(component_experiments) < 2 and stated_activation_energy is None:
            raise ValueError(
                "At least two measurements at different temperatures are required for "
                "the calculation of Apparent Activation Energy"
            )
        elif len(component_experiments) < 2 and stated_activation_energy is not None:
            return stated_activation_energy

        x = numpy.divide(
            1,
            [
                ideal_experiment.temperature
                for ideal_experiment in component_experiments.experiments
            ],
        )

        y = numpy.log(
            [
                ideal_experiment.permeance.value
                for ideal_experiment in component_experiments.experiments
            ]
        )

        a = numpy.vstack([x, numpy.ones(len(x))]).T

        activation_energy, c = numpy.linalg.lstsq(a, y, rcond=-1)[0] * R

        return -activation_energy

    def get_permeance(
        self,
        temperature: float,
        component: Component,
        initial_permeance: typing.Optional[Permeance] = None,
    ) -> Permeance:
        """
        Calculates Permeance of a specified component (kg/(m2*h*kPa)) at a specified Temperature (K)
        based on a given or calculated Apparent Activation Energy of Transport
        """

        component_experiments = self.get_penetrant_data(component)

        temperature_list = [
            ideal_experiment.temperature
            for ideal_experiment in component_experiments.experiments
        ]

        index = min(
            range(len(temperature_list)),
            key=lambda i: abs(temperature_list[i] - temperature),
        )

        given_permeance = component_experiments.experiments[index].permeance.convert(
            to_units=PermeanceUnits.kg_m2_h_kPa, component=component
        )

        if (
            component_experiments.experiments[index].activation_energy is None
            and component_experiments.experiments[index].temperature != temperature
        ):
            # TODO: add logs
            activation_energy = self.calculate_activation_energy(component)
            return Permeance(
                value=given_permeance.value
                * numpy.exp(
                    -activation_energy
                    / R
                    * (1 / temperature - 1 / temperature_list[index])
                )
            )
        elif component_experiments.experiments[index].temperature == temperature:
            return given_permeance

        elif initial_permeance is not None:
            return Permeance(
                value=initial_permeance.value
                * numpy.exp(
                    -component_experiments.experiments[index].activation_energy
                    / R
                    * (1 / temperature - 1 / temperature_list[index])
                )
            )

        else:
            return Permeance(
                value=given_permeance.value
                * numpy.exp(
                    -component_experiments.experiments[index].activation_energy
                    / R
                    * (1 / temperature - 1 / temperature_list[index])
                )
            )

    def get_ideal_selectivity(
        self,
        temperature: float,
        first_component: Component,
        second_component: Component,
        calculation_type: typing.Optional[str] = "molar",
    ) -> float:
        """
        Calculates Ideal selectivity of one specified component over the other at a specified temperature.
        """
        if calculation_type == "weight":
            return (
                self.get_permeance(temperature, first_component).value
                / self.get_permeance(temperature, second_component).value
            )
        elif calculation_type == "molar":
            return (
                self.get_permeance(temperature, first_component)
                .convert(to_units=PermeanceUnits.si, component=first_component)
                .value
                / self.get_permeance(temperature, second_component)
                .convert(to_units=PermeanceUnits.si, component=second_component)
                .value
            )

    def get_estimated_pure_component_flux(
        self,
        temperature: float,
        component: Component,
        permeate_temperature: typing.Optional[float] = None,
        permeate_pressure: typing.Optional[float] = None,
    ) -> float:
        """
        Calculates Flux of a specified component during individual Pervaporation based on the specified Permeance
        from Ideal Experiments Of the Component.
        May be performed either on the basis of permeate temperature in K or permeate pressure in kPa.
        If permeate conditions are not stated partial pressure of the component in permeate is considered zero.
        """
        if permeate_temperature is None and permeate_pressure is None:
            return self.get_permeance(
                temperature, component
            ).value * component.get_vapor_pressure(temperature)
        elif permeate_temperature is not None and permeate_pressure is None:
            return self.get_permeance(temperature, component).value * (
                component.get_vapor_pressure(temperature)
                - component.get_vapor_pressure(permeate_temperature)
            )
        elif permeate_pressure is not None and permeate_temperature is None:
            return self.get_permeance(temperature, component).value * (
                component.get_vapor_pressure(temperature) - permeate_pressure
            )
        else:
            raise ValueError(
                "Either permeate temperature or permeate pressure could be stated not both"
            )
