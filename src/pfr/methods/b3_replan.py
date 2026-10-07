from ..core import Decision


class B3Replan:
    """Replan after every failure. Looks only at the current failure, keeps no history."""
    name = "B3"

    def on_failure(self, ctx):
        return Decision("replan", "always replan")
