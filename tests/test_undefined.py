from __future__ import annotations

import jinjarope


def test_lax_undefined():
    env = jinjarope.Environment(undefined="lax")
    env.render_string(r"{{ a.not_existing }}")
