from argparse import ArgumentParser
from typing import Optional
import os

class AdvancedArgumentParser(ArgumentParser):
    def add_argument(self, *args, env: Optional[str] = None, **kwargs):
        if env and env in os.environ:
            kwargs['default'] = os.environ[env]
            kwargs['required'] = False

        return super().add_argument(*args, **kwargs)

    def _add_action(self, action):
        if hasattr(action, 'env') and action.env and action.env in os.environ:
            action.default = os.environ[action.env]
            action.required = False

        return super()._add_action(action)
