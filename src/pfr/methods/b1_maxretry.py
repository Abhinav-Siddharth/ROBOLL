from ..core import Decision


class B1MaxRetry:
    """Allow k=3 attempts in total, then abstain."""
    name = "B1"

    def __init__(self, k: int = 3):
        self.k = k

    def on_failure(self, ctx):
        if ctx.n_fail < self.k:
            return Decision("retry", f"{ctx.n_fail} < {self.k}")
        return Decision("abstain", f"{self.k} attempts used")
