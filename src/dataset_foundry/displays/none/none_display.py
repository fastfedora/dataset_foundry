from ..core.display import Display
from ...core.pipeline import Pipeline

class NoneDisplay(Display):
    def setup_logging(self, log_level: str):
        # If we don't want anything to display, then just don't setup logging
        pass

    async def run_pipeline(self, pipeline: Pipeline, params: dict):
        await pipeline.run(params=params)
