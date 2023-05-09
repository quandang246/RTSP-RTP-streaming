import socket
from threading import Thread
from typing import Union, Optional, List, Tuple
from time import sleep
from PIL import Image
from io import BytesIO

from utils.rtsp_packet import RTSPPacket
from utils.rtp_packet import RTPPacket
from utils.video_stream import VideoStream


class Client:
    DEFAULT_CHUNK_SIZE = 4096
    DEFAULT_RECV_DELAY = 20  # in milliseconds

    DEFAULT_LOCAL_HOST = '127.0.0.1'

    RTP_SOFT_TIMEOUT = 5  # in milliseconds
    # for allowing simulated non-blocking operations
    # (useful for keyboard break)
    RTSP_SOFT_TIMEOUT = 100  # in milliseconds
    # if it's present at the end of chunk, client assumes
    # it's the last chunk for current frame (end of frame)
    PACKET_HEADER_LENGTH = 5

    def __init__(
            self,
            file_path: str,
            remote_host_address: str,
            remote_host_port: int,
            rtp_port: int):
        self._rtsp_connection: Union[None, socket.socket] = None
        self._rtp_socket: Union[None, socket.socket] = None
        self._rtp_receive_thread: Union[None, Thread] = None
        self._frame_buffer: List[Image.Image] = []
        self._current_sequence_number = 0
        self.session_id = ''

        self.current_frame_number = -1

        self.is_rtsp_connected = False
        self.is_receiving_rtp = False

        self.file_path = file_path
        self.remote_host_address = remote_host_address
        self.remote_host_port = remote_host_port
        self.rtp_port = rtp_port