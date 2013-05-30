import time
import logging

from construct import Container
from random import randint
from socket import socket

from spackets import spacket
from rpackets import rpackets
from bnutil import check_revision, hash_d2key, sub_double_hash, bsha1


class Bnet():
    def __init__(self, host, port, login_error=None, chat_event=None):
        self.host = host
        self.port = port

        self.login_error = login_error or (lambda packet_id, retcode: None)
        self.chat_event = chat_event or (lambda packet: None)

    def login(self, username, password):
        self.username = bytes(username, "ascii")
        self.hashpass = bsha1(bytes(password, "ascii"))

        self.head = b""

        self.sock = socket()
        try:
            self.sock.connect((self.host, self.port))
        except:
            self.login_error("Connecting to server")
            return

        self.sock.sendall(b"\x01")
        self.sock.sendall(
            spacket.build(
                Container(
                    packet_id="SID_AUTH_INFO",
                    protocol_id=0,
                    platform_id=b'68XI',
                    product_id=b'PX2D',
                    version_byte=13,
                    product_language=b'SUne',
                    local_ip="192.168.0.100",
                    time_zone=time.altzone // 60,
                    locale_id=1049,
                    language_id=1049,
                    country_abreviation=b'RUS',
                    country=b'Russia',
                )
            )
        )

    def say(self, msg):
        self.sock.sendall(
            spacket.build(
                Container(
                    packet_id="SID_CHATCOMMAND",
                    text=bytes(msg, "utf-8"),
                )
            )
        )

    def on_packet(self):
        unparsed = rpackets.parse(self.head + self.sock.recv(2 ** 16))
        self.head = unparsed.tail

        if len(unparsed.rpackets) == 0:
            logging.info("[bnet.py] Nothing to proceed, but data there")

        for pack in unparsed.rpackets:

            if pack.packet_id == "SID_PING":
                self.sock.sendall(spacket.build(pack))

            elif pack.packet_id == "SID_AUTH_INFO":
                self.client_token = randint(10 * 60 * 1000, 2 ** 32 - 1)
                self.server_token = pack.server_token

                clpub, clhash = hash_d2key(b"DPTGEGHRPH4EB7EV", self.client_token, self.server_token)
                lodpub, lodhash = hash_d2key(b"KFE6H7RPTRTHDEJE", self.client_token, self.server_token)

                self.sock.sendall(
                    spacket.build(
                        Container(
                            packet_id="SID_AUTH_CHECK",
                            client_token=self.client_token,
                            exe_version=0x01000d00,
                            exe_hash=check_revision(
                                pack.seed_values,
                                pack.file_name
                            ),
                            number_of_cd_keys=2,
                            spawn_cd_key=0,
                            cd_keys=[
                                Container(
                                    key_length=16,
                                    cd_key_product=6,
                                    cd_key_public=clpub,
                                    hash=clhash,
                                ),
                                Container(
                                    key_length=16,
                                    cd_key_product=12,
                                    cd_key_public=lodpub,
                                    hash=lodhash,
                                ),
                            ],
                            exe_info=b"Game.exe 10/18/11 20:48:14 65536",
                            cd_key_owner=b"yoba",
                        )
                    )
                )

            elif pack.packet_id == "SID_AUTH_CHECK":
                if pack.result != 0:
                    logging.info(str.format("[bnet.py] Non-zero result on \n{}", pack))
                    self.login_error(pack.packet_id, pack.result)
                else:
                    self.sock.sendall(
                        spacket.build(
                            Container(
                                packet_id="SID_LOGONRESPONSE2",
                                client_token=self.client_token,
                                server_token=self.server_token,
                                hash=sub_double_hash(
                                    self.client_token,
                                    self.server_token,
                                    self.hashpass
                                ),
                                username=self.username,
                            )
                        )
                    )

            elif pack.packet_id == "SID_LOGONRESPONSE2":
                if pack.result != 0:
                    logging.info(str.format("[bnet.py] Non-zero result on \n{}", pack))
                    self.login_error(pack.packet_id, pack.result)
                else:
                    self.sock.sendall(
                        spacket.build(
                            Container(
                                packet_id="SID_ENTERCHAT",
                                username=self.username,
                                statstring=b"",
                            )
                        )
                    )

            elif pack.packet_id == "SID_ENTERCHAT":
                self.sock.sendall(
                    spacket.build(
                        Container(
                            packet_id="SID_JOINCHANNEL",
                            unknown=5,
                            channel_name=b"Diablo II",
                        )
                    )
                )

            elif pack.packet_id == "SID_CHATEVENT":
                self.chat_event(pack)

            else:
                logging.info(str.format("[bnet.py] unhandled packet\n{}", pack))
