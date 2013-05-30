from construct import *
from construct.adapters import *
from construct.macros import *
from construct.protocols.layer3.ipv4 import IpAddress


rpacket = Struct(
    "rpackets",
    Const(ULInt8(None), 0xff),
    Enum(
        ULInt8("packet_id"),
        SID_PING=0x25,
        SID_AUTH_INFO=0x50,
        SID_AUTH_CHECK=0x51,
        SID_LOGONRESPONSE2=0x3a,
        SID_ENTERCHAT=0x0a,
        SID_GETCHANNELLIST=0x0b,
        SID_CHATEVENT=0x0f,
    ),
    ULInt16("length"),
    Embed(
        Switch(
            None,
            lambda ctx: ctx.packet_id,
            {
                "SID_PING": Struct(
                    None,
                    ULInt32("value"),
                ),
                "SID_AUTH_INFO": Struct(
                    None,
                    ULInt32("logon_type"),
                    ULInt32("server_token"),
                    ULInt32("udp_value"),
                    Bytes("file_time", 8),
                    CString("file_name"),
                    CString("seed_values")
                ),
                "SID_AUTH_CHECK": Struct(
                    None,
                    ULInt32("result"),
                    CString("info"),
                ),
                "SID_LOGONRESPONSE2": Struct(
                    None,
                    ULInt32("result"),
                    Optional(CString("info")),
                ),
                "SID_ENTERCHAT": Struct(
                    None,
                    CString("unique_name"),
                    CString("statstring"),
                    CString("account_name"),
                ),
                "SID_GETCHANNELLIST": Struct(
                    None,
                    OptionalGreedyRange(CString("channels")),
                ),
                "SID_CHATEVENT": Struct(
                    None,
                    Enum(
                        ULInt32("event_id"),
                        ID_USER=0x01,
                        ID_JOIN=0x02,
                        ID_LEAVE=0x03,
                        ID_WHISPER=0x04,
                        ID_TALK=0x05,
                        ID_BROADCAST=0x06,
                        ID_CHANNEL=0x07,
                        ID_USERFLAGS=0x09,
                        ID_WHISPERSENT=0x0a,
                        ID_CHANNELFULL=0x0d,
                        ID_CHANNELDOESNOTEXIST=0x0e,
                        ID_CHANNELRESTRICTED=0x0f,
                        ID_INFO=0x12,
                        ID_ERROR=0x13,
                        ID_EMOTE=0x17,
                        ID_SYSTEMBLUE=0x18,
                        ID_SYSTEMRED=0x19,
                    ),
                    ULInt32("user_flags"),
                    ULInt32("ping"),
                    IpAddress("ip_address"),
                    ULInt32("account_number"),
                    ULInt32("registration_authority"),
                    CString("username"),
                    CString("text"),
                ),
            }
        )
    )
)

rpackets = Struct(
    None,
    OptionalGreedyRange(rpacket),
    ExprAdapter(
        OptionalGreedyRange(Byte("tail")),
        encoder=lambda obj, ctx: list(obj),
        decoder=lambda obj, ctx: bytes(obj)
    )
)
