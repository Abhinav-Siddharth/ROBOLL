from .. import prompts
from ..core import Decision, MODES


class B4LLMHistory:
    """The LLM chooses retry/modify/replan/escalate/abstain and sees the FULL failure history."""
    name = "B4"

    def on_failure(self, ctx):
        msgs = prompts.mode_messages(
            ctx.task, ctx.call, ctx.result, history=ctx.history, remaining=ctx.remaining,
            untried=ctx.untried if ctx.param_field else None, n_fail=ctx.n_fail,
        )
        out = ctx.llm.call(msgs, prompts.MODE_SCHEMA)
        mode = out.get("mode") if out else None
        if mode not in MODES:
            return Decision("retry", "parse failure -> retry")
        return Decision(mode, out.get("why", ""))
