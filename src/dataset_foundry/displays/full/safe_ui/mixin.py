from typing import Callable


class SafeUiMixin:
    """
    Mixin providing helpers to safely perform UI mutations from non-UI tasks.
    """

    def safe_ui_call(self, fn: Callable[[], None]) -> None:
        """
        Safely execute a UI mutation, falling back to the app's UI thread if needed.

        Attempts to run the function directly; if a RuntimeError is raised due to
        thread/task or lifecycle constraints, uses `app.call_from_thread(fn)` when
        available.
        """
        try:
            fn()
        except RuntimeError:
            app = getattr(self, "app", None)
            if app is not None and hasattr(app, "call_from_thread"):
                app.call_from_thread(fn)
