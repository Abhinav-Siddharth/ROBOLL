"""B2 with matched budget/untried hints but no earlier failure history."""
from .. import prompts
from ..core import Decision, MODES


class B2Context:
    name = 'B2C'

    def on_failure(self, ctx):
        messages = prompts.mode_messages(
            ctx.task, ctx.call, ctx.result, history=None, remaining=ctx.remaining,
            untried=ctx.untried if ctx.param_field else None,
            n_fail=ctx.n_fail, context_only=True)
        out = ctx.llm.call(messages, prompts.MODE_SCHEMA)
        mode = out.get('mode') if out else None
        if mode not in MODES:
            return Decision('retry', 'parse failure -> retry')
        return Decision(mode, out.get('why', ''))
