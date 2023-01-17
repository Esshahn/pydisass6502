from disass import load_opcodes


def test_opcodes():
    opcodes = load_opcodes('lib/opcodes.json')

    # every byte is covered exactly once
    assert len(opcodes) == 256
    assert len(set(opcodes.keys())) == 256

    # eight relative instuctions
    assert len([d for d in opcodes.values() if d.mode == "rel"]) == 8

    # 105 illegal instructions
    assert len([d for d in opcodes.values() if d.illegal]) == 105

    # check mode enum
    assert {d.mode for d in opcodes.values()} == {"impl", "ind", "imm", "rel", "abs"}

    # ops with targets should have arguments
    assert all(d.arglen > 0 for d in opcodes.values() if d.target is not None)

    default_to_data_after = {"4c", "60", "40"}
    s = set(op for op, d in opcodes.items() if d.nofollow)
    assert s == default_to_data_after

    abs_branch_mnemonics = {"4c", "20"}
    s = {op for op, d in opcodes.items() if d.target == "code" and d.mode != "rel"}
    assert s == set(abs_branch_mnemonics)

    abs_address_mnemonics = {
        "0d", "0e",
        "19", "1d", "1e",
        "2d", "2e",
        "39", "3d", "3e",
        "4d", "4e",
        "59", "5d", "5e",
        "6d", "6e",
        "79", "7d", "7e",
        "8c", "8d", "8e",
        "99", "9d",
        "ac", "ad", "ae",
        "b9", "bc", "bd", "be",
        "cc", "cd", "ce",
        "d9", "dd", "de",
        "ec", "ee", "ed",
        "f9", "fd", "fe"
    }
    abs_address_mnemonics.add("2c")  # ommitted in original
    s = {
        op for op, d in opcodes.items()
        if d.target == "data" and d.mode == "abs" and d.arglen == 2 and not d.illegal
    }
    assert s == abs_address_mnemonics
