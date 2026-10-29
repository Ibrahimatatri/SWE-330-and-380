from skillguard.parsing import is_shell, parse


def contexts(text):
    return [(l.no, l.context) for l in parse(text)]


def test_front_matter_prose_and_fences():
    text = "---\nname: x\n---\nIntro\n```bash\nls\n```\n~~~python\nprint(1)\n~~~\n```\nplain\n```"
    assert contexts(text) == [(2, "front_matter"), (4, "prose"), (6, "code:bash"), (9, "code:python"), (12, "code:")]


def test_fence_with_info_string_does_not_close_block():
    text = "````md\n```bash\nls\n```\n````\nafter"
    assert contexts(text) == [(2, "code:md"), (3, "code:md"), (4, "code:md"), (6, "prose")]


def test_unclosed_front_matter_is_prose():
    assert contexts("---\nname: x\nbody") == [(1, "prose"), (2, "prose"), (3, "prose")]


def test_is_shell():
    assert is_shell("code:bash") and is_shell("code:powershell")
    assert not is_shell("code:python") and not is_shell("code:") and not is_shell("prose")
