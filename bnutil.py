import struct
import os.path
from functools import reduce
from xsha1 import calc_hash_buffer


def bsha1(data):
    return struct.pack("5i", *calc_hash_buffer(data))

mpq_hash_codes = (
    0xE7F4CB62,
    0xF6A14FFC,
    0xAA5504AF,
    0x871FCDC2,
    0x11BF6A18,
    0xC57292E6,
    0x7927D27E,
    0x2FEC8733
)


def check_revision(formula, mpq, path="d2xp"):

    mpq_hash = mpq_hash_codes[mpq[9] - ord("0")]
    formula = str(formula, "ascii").split()

    for i in range(len(formula)):
        if formula[i].isdigit():
            init, actions = formula[:i], formula[i + 1:]
            break

    for i in range(len(actions)):
        var, expr = actions[i].split("=")
        actions[i] = var + "=(" + expr + ") % (1 << 32)"

    actions = compile(str.join("\n", actions), "<string>", mode="exec")

    get_raw = lambda fname: open(os.path.join(path, fname), mode="rb", buffering=0).readall()
    data = bytes.join(b"", map(get_raw, ("Game.exe", "Bnclient.dll", "D2Client.dll")))
    nums = struct.unpack(str.format("{}I", len(data) // 4), data)

    env = {}
    exec(str.join("\n", init), env)
    env["A"] ^= mpq_hash
    for env["S"] in nums:
        exec(actions, env)

    return env["C"]

alpha_map = (
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF,	0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0x00, 0xFF, 0x01, 0xFF, 0x02, 0x03,
    0x04, 0x05, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
    0x0C, 0xFF, 0x0D, 0x0E, 0xFF, 0x0F, 0x10, 0xFF,
    0x11, 0xFF,	0x12, 0xFF, 0x13, 0xFF, 0x14, 0x15,
    0x16, 0xFF, 0x17, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
    0x0C, 0xFF, 0x0D, 0x0E, 0xFF, 0x0F, 0x10, 0xFF,
    0x11, 0xFF, 0x12, 0xFF, 0x13, 0xFF, 0x14, 0x15,
    0x16, 0xFF, 0x17, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF,	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
)


def hash_d2key(cdkey, client_token, server_token):

    checksum = 0
    m_key = [None] * len(cdkey)

    for i in range(0, len(cdkey), 2):
        n = alpha_map[cdkey[i]] * 24 + alpha_map[cdkey[i + 1]]
        if n >= 0x100:
            n -= 0x100
            checksum |= 1 << (i >> 1)
        m_key[i] = str.format("{:X}", (n >> 4) & 0xf)
        m_key[i + 1] = str.format("{:X}", n & 0xf)

    if reduce(lambda v, ch: v + (int(ch, 16) ^ (v * 2)), m_key, 3) & 0xff != checksum:
        return None, None  # invalid CD-key

    for i in range(len(cdkey) - 1, -1, -1):
        n = (i - 9) % 0x10
        m_key[i], m_key[n] = m_key[n], m_key[i]

    v2 = 0x13AC9741
    for i in range(len(cdkey) - 1, -1, -1):
        if ord(m_key[i]) <= ord("7"):
            m_key[i] = chr((v2 & 7) ^ ord(m_key[i]))
            v2 >>= 3
        elif ord(m_key[i]) < ord("A"):
            m_key[i] = chr((i & 1) ^ ord(m_key[i]))

    m_key = str.join("", map(str, m_key))

    public_value = int(m_key[2:8], 16)
    hash_data = struct.pack(
        "6I",
        client_token,
        server_token,
        int(m_key[:2], 16),
        int(m_key[2:8], 16),
        0,
        int(m_key[8:16], 16)
    )

    return public_value, bsha1(hash_data)


def sub_double_hash(client_token, server_token, hashpass):
    return bsha1(struct.pack("2I20s", client_token, server_token, hashpass))
