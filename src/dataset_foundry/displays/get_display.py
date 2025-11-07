from .full.full_display import FullDisplay
from .log.log_display import LogDisplay
from .none.none_display import NoneDisplay

def get_display(display_type: str):
    if display_type == "log":
        return LogDisplay()
    elif display_type == "full":
        return FullDisplay()
    elif display_type == "none":
        return NoneDisplay()
    else:
        raise ValueError(f"Invalid display type: {display_type}")
