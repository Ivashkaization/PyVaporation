import attr
import yaml
import typing

from pathlib import Path


@attr.s(auto_attribs=True)
class Config:
    membrane_path: Path
    results_path: Path

    def __attrs_post_init__(self):
        self.results_path.mkdir(parents=True, exist_ok=True)

        self.ideal_experiment_path: typing.Optional[Path] = self.membrane_path / 'ideal_experiments.csv'
        if not self.ideal_experiment_path.exists():
            self.ideal_experiment_path = None

        self.diffusion_curve_sets_path: typing.Optional[Path] = self.membrane_path / 'diffusion_curve_sets'
        if not self.diffusion_curve_sets_path.exists():
            self.diffusion_curve_sets_path = None

        if not (self.ideal_experiment_path is not None) or (self.diffusion_curve_sets_path is not None):
            raise FileExistsError('No experimental data found.')

    @classmethod
    def load(cls, path: typing.Union[str, Path]):
        with open(path, 'rb') as handle:
            return cls(**yaml.load(handle, Loader=yaml.FullLoader))
