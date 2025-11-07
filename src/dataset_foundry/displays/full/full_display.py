import asyncio

from ...core.pipeline import Pipeline
from ..core.display import Display
from ..core.pipeline_log_handler import install_pipeline_log_handler
from .full_display_app import FullDisplayApp

class FullDisplay(Display):
    def setup_logging(self, log_level: str):
        install_pipeline_log_handler(log_level)

    async def run_pipeline(self, pipeline: Pipeline, params: dict):
        app = FullDisplayApp()

        async def run_pipeline_task():
            await pipeline.run(params=params)

        async def run_app_task():
            await app.run_async()

        pipeline_task = asyncio.create_task(run_pipeline_task())
        app_task = asyncio.create_task(run_app_task())

        done, _pending = await asyncio.wait(
            {pipeline_task, app_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if app_task in done and not pipeline_task.done():
            print("Shutting down Docker containers... Please wait for cleanup to complete.")
            pipeline_task.cancel()
            try:
                await pipeline_task
            except asyncio.CancelledError:
                pass

        # If pipeline finished first, properly exit the app before cancelling the task
        if pipeline_task in done and not app_task.done():
            if not params.get("no_exit", False):
                app.exit()

            try:
                await app_task
            except asyncio.CancelledError:
                pass
