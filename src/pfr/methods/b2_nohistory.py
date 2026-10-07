from .. import prompts
from ..core import Decision, MODES


class B2NoHistory:
    """Same MODE prompt as B4 but WITHOUT any history: only the current error. Tests whether history helps."""
    name = "B2"

    def on_failure(self, ctx):
        msgs = prompts.mode_messages(ctx.task, ctx.call, ctx.result, history=None)
        out = ctx.llm.call(msgs, prompts.MODE_SCHEMA)
        mode = out.get("mode") if out else None
        if mode not in MODES:
            return Decision("retry", "parse failure -> retry")
        return Decision(mode, out.get("why", ""))
