from ..core import Decision


class B0Retry:
    """Naive retry: always retry (the runner cuts the episode at max_failures)."""
    name = "B0"

    def on_failure(self, ctx):
        return Decision("retry", "always retry")
