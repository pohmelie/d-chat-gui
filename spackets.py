from construct import *
from construct.adapters import *
from construct.macros import *
from construct.protocols.layer3.ipv4 import IpAddress


class PacketLengthAdapter(Adapter):
    def _encode(self, obj, context):
        obj.length = 0
        obj.length = len(_spacket.build(obj))
        return obj

    def _decode(self, obj, context):
        return obj

_spacket = Struct(
    None,
    Const(ULInt8(None), 0xff),
    Enum(
        ULInt8("packet_id"),
        SID_AUTH_INFO=0x50,
        SID_PING=0x25,
        SID_AUTH_CHECK=0x51,
        SID_LOGONRESPONSE2=0x3a,
        SID_ENTERCHAT=0x0a,
        SID_GETCHANNELLIST=0x0b,
        SID_JOINCHANNEL=0x0c,
        SID_CHATCOMMAND=0x0e,
    ),
    ULInt16("length"),
    Embed(
        Switch(
            None,
            lambda ctx: ctx.packet_id,
            {
                "SID_AUTH_INFO": Struct(
                    None,
                    ULInt32("protocol_id"),
                    Bytes("platform_id", 4),
                    Bytes("product_id", 4),
                    ULInt32("version_byte"),
                    Bytes("product_language", 4),
                    IpAddress("local_ip"),
                    SLInt32("time_zone"),
                    ULInt32("locale_id"),
                    ULInt32("language_id"),
                    CString("country_abreviation"),
                    CString("country")
                ),
                "SID_PING": Struct(
                    None,
                    ULInt32("value"),
                ),
                "SID_AUTH_CHECK": Struct(
                    None,
                    ULInt32("client_token"),
                    ULInt32("exe_version"),
                    ULInt32("exe_hash"),
                    ULInt32("number_of_cd_keys"),
                    ULInt32("spawn_cd_key"),
                    Array(
                        lambda ctx: ctx["number_of_cd_keys"],
                        Struct(
                            "cd_keys",
                            ULInt32("key_length"),
                            ULInt32("cd_key_product"),
                            ULInt32("cd_key_public"),
                            Const(ULInt32(None), 0),
                            Bytes("hash", 5 * 4),
                        )
                    ),
                    CString("exe_info"),
                    CString("cd_key_owner")
                ),
                "SID_LOGONRESPONSE2": Struct(
                    None,
                    ULInt32("client_token"),
                    ULInt32("server_token"),
                    Bytes("hash", 5 * 4),
                    CString("username"),
                ),
                "SID_ENTERCHAT": Struct(
                    None,
                    CString("username"),
                    CString("statstring"),
                ),
                "SID_GETCHANNELLIST": Struct(
                    None,
                    Bytes("product_id", 4),
                ),
                "SID_JOINCHANNEL": Struct(
                    None,
                    ULInt32("unknown"),
                    CString("channel_name"),
                ),
                "SID_CHATCOMMAND": Struct(
                    None,
                    CString("text"),
                ),
            }
        )
    )
)

spacket = PacketLengthAdapter(_spacket)  # client -> server
