import os  # pylint: disable=C0114,missing-module-docstring
import shutil
from pathlib import Path
from typing import Union

import yaml

PATH_CONFIG_DEFAULT = Path(__file__).parent / "default.yaml"


class Config:
    def __init__(self, path_cfg: Union[Path, None] = None):
        self.path_cfg = path_cfg
        self.load_config(path_cfg)

    def load_config(self, path_cfg: Union[Path, None] = None):
        if path_cfg is None:
            path_cwd = Path(os.getcwd())
            path_cfg = path_cwd / "pyomd-config.yaml"
        if path_cfg.exists():
            with open(path_cfg, "r") as f:
                u_cfg = yaml.load(f, Loader=yaml.Loader)  # type: ignore
            # TODO check validity of user config
            cfg = u_cfg
        else:
            with open(PATH_CONFIG_DEFAULT, "r") as f:
                d_cfg = yaml.load(f, Loader=yaml.Loader)  # type: ignore
            cfg = d_cfg
        self.cfg = cfg

    @classmethod
    def create_config_file(cls, path_cfg: Union[Path, None] = None):
        if path_cfg is None:
            path_cwd = Path(os.getcwd())
            path_cfg = path_cwd / "pyomd-config.yaml"
        shutil.copy(PATH_CONFIG_DEFAULT, path_cfg)
