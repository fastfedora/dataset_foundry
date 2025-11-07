import logging

from ..core.display import Display
from ...core.pipeline import Pipeline

class LogDisplay(Display):
    def setup_logging(self, log_level: str):
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    async def run_pipeline(self, pipeline: Pipeline, params: dict):
        await pipeline.run(params=params)
