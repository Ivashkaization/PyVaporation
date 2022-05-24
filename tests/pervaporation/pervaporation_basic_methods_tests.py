from component import AllComponents
from experiments import IdealExperiments, IdealExperiment
from mixture import AllMixtures, Composition, CompositionType
from membrane import Membrane
from pervaporation import Pervaporation
from conditions import Conditions
from pytest import fixture


@fixture
def all_components():
    return AllComponents.load("components.yml")


@fixture
def all_mixtures(all_components):
    return AllMixtures.load("mixtures.yml", all_components)


@fixture
def romakon_pm102_binary(all_components):
    experiment_h2o_1 = IdealExperiment(
        name="Romakon-PM102",
        temperature=313.15,
        component=all_components.h2o,
        permeance=0.05500,
        activation_energy=19944,
    )
    experiment_h2o_2 = IdealExperiment(
        name="Romakon-PM102",
        temperature=323.15,
        component=all_components.h2o,
        permeance=0.06713,
        activation_energy=19944,
    )
    experiment_h2o_3 = IdealExperiment(
        name="Romakon-PM102",
        temperature=333.15,
        component=all_components.h2o,
        permeance=0.08718,
        activation_energy=19944,
    )
    experiment_etoh_1 = IdealExperiment(
        name="Romakon-PM102",
        temperature=313.15,
        component=all_components.etoh,
        permeance=0.00002,
        activation_energy=110806,
    )
    experiment_etoh_2 = IdealExperiment(
        name="Romakon-PM102",
        temperature=323.15,
        component=all_components.etoh,
        permeance=0.00003,
        activation_energy=110806,
    )
    experiment_etoh_3 = IdealExperiment(
        name="Romakon-PM102",
        temperature=333.15,
        component=all_components.etoh,
        permeance=0.00027,
        activation_energy=110806,
    )

    ideal_experiments = IdealExperiments(
        experiments=[
            experiment_h2o_1,
            experiment_h2o_2,
            experiment_h2o_3,
            experiment_etoh_1,
            experiment_etoh_2,
            experiment_etoh_3,
        ]
    )

    return Membrane(ideal_experiments=ideal_experiments, name="Romakon-PM102")


@fixture
def romakon_pm102_real(all_components):
    experiment_h2o_1 = IdealExperiment(
        name="Romakon-PM102",
        temperature=313.15,
        component=all_components.h2o,
        permeance=0.036091,
        activation_energy=19944,
    )

    experiment_etoh_1 = IdealExperiment(
        name="Romakon-PM102",
        temperature=313.15,
        component=all_components.etoh,
        permeance=0.0000282,
        activation_energy=110806,
    )

    ideal_experiments = IdealExperiments(
        experiments=[
            experiment_h2o_1,
            experiment_etoh_1,
        ]
    )

    return Membrane(ideal_experiments=ideal_experiments, name="Romakon-PM102")


@fixture
def test_conditions():
    return Conditions(
        membrane_area=0.05,
        feed_temperature=323.15,
        permeate_temperature=1,
        feed_amount=1,
        initial_feed_composition=Composition(p=0.15, type=CompositionType("weight")),
    )


@fixture()
def pervaporation_binary(romakon_pm102_binary, all_mixtures, test_conditions):
    return Pervaporation(
        membrane=romakon_pm102_binary,
        mixture=all_mixtures.h2o_etoh,
        conditions=test_conditions,
    )


@fixture()
def pervaporation_real(romakon_pm102_real, all_mixtures, test_conditions):
    return Pervaporation(
        membrane=romakon_pm102_real,
        mixture=all_mixtures.h2o_etoh,
        conditions=test_conditions,
    )


def test_check_activation_energies(romakon_pm102_binary, all_components):
    assert (
        abs(
            romakon_pm102_binary.calculate_activation_energy(all_components.h2o)
            - romakon_pm102_binary.get_penetrant_data(all_components.h2o)
            .experiments[0]
            .activation_energy
        )
        < romakon_pm102_binary.get_penetrant_data(all_components.h2o)
        .experiments[0]
        .activation_energy
        * 0.05
    )
    assert (
        abs(
            romakon_pm102_binary.calculate_activation_energy(all_components.etoh)
            - romakon_pm102_binary.get_penetrant_data(all_components.etoh)
            .experiments[0]
            .activation_energy
        )
        < romakon_pm102_binary.get_penetrant_data(all_components.etoh)
        .experiments[0]
        .activation_energy
        * 0.05
    )


def test_calculate_partial_fluxes_variable_concentration(
    pervaporation_binary, all_components
):
    validation_fluxes_40 = [
        (0.4528037879, 0.0002265151515),
        (0.3791491736, 0.0001896694215),
        (0.3120968379, 0.0001561264822),
    ]
    validation_permeate_compositions_40 = [
        Composition(p=0.9995, type=CompositionType("weight")),
        Composition(p=0.9995, type=CompositionType("weight")),
        Composition(p=0.9995, type=CompositionType("weight")),
    ]

    validation_feed_compositions_40 = [
        Composition(p=0.92, type=CompositionType("weight")),
        Composition(p=0.84, type=CompositionType("weight")),
        Composition(p=0.73, type=CompositionType("weight")),
    ]

    modelled_fluxes = [
        pervaporation_binary.calculate_partial_fluxes(
            feed_temperature=313.15, composition=validation_feed_compositions_40[i]
        )
        for i in range(len(validation_fluxes_40))
    ]

    for i in range(len(validation_fluxes_40)):
        assert abs(modelled_fluxes[i][0] - validation_fluxes_40[i][0]) < 7e-2
        assert abs(modelled_fluxes[i][1] - validation_fluxes_40[i][1]) < 2e-4


def test_calculate_partial_fluxes_variable_permeate_temperature(
    pervaporation_real, romakon_pm102_real
):
    validation_permeate_temperatures = [80, 276.15, 290.15]
    validation_fluxes = [1.107195, 1.069, 1.0416]

    for i in range(len(validation_permeate_temperatures)):
        assert (
            abs(
                pervaporation_real.calculate_partial_fluxes(
                    feed_temperature=333.15,
                    composition=Composition(p=0.9362, type=CompositionType("weight")),
                    precision=5e-5,
                    permeate_temperature=validation_permeate_temperatures[i],
                )[0]
                - validation_fluxes[i]
            )
            < 5e-2
        )


def test_calculate_permeate_composition_variable_permeate_temperature(pervaporation_real):
    validation_permeate_compositions = [
        Composition(p=0.9995, type=CompositionType("weight")),
        Composition(p=0.9995, type=CompositionType("weight")),
        Composition(p=0.9970, type=CompositionType("weight")),
    ]
    validation_permeate_temperatures = [80, 276.15, 290.15]

    for i in range(len(validation_permeate_temperatures)):
        assert (
            abs(
                pervaporation_real.calculate_permeate_composition(
                    feed_temperature=333.15,
                    composition=Composition(p=0.9362, type=CompositionType("weight")),
                    permeate_temperature=validation_permeate_temperatures[i],
                ).second
                - validation_permeate_compositions[i].second
            )
            < 2e-3
        )
def test_calculate_partial_fluxes_variable_precision(pervaporation_real):
    precision_range = [1,0.5,0.05,0.005, 0.0005, 0.00005]
    pervaporation_real.calculate_partial_fluxes(

    )