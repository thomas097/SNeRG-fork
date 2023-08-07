import socket
import struct


class UDP:
    def __init__(
            self,
            ip: str = "127.0.0.1",
            send_port: int = 5000,
            recv_port: int = 5005,
            send_fmt: str = "i",
            recv_fmt: str = "i",
            byte_order: str = '@'
            ) -> None:
        
        """UDP networking module used to receive simulator states and send controller 
        commands back to the simulator.

        Args:
            ip (str, optional):         IPv4 address of server on which simulator runs.
            send_port (int, optional):  Server-side port to send data (controller commands) to (Default: 5000).
            recv_port (int, optional):  Controller-side port to receive simulator data on (Default: 5005).
            send_fmt (str, optional):   Format of controller commands. Please refer to:
                                        https://docs.python.org/3/library/struct.html#format-characters
            recv_fmt (str, optional):   Format of simulation state data.
            byte_order (str, optional): Byte order (Default: '@', i.e. 'native').
        """
        # Sender
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send_addr = (ip, send_port)

        # Receiver (precomp size pf message in bytes)
        self._recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._recv_sock.bind((ip, recv_port)) 
        self._recv_bytes = struct.calcsize(self._recv_fmt)

        # Formatting
        self._send_fmt = byte_order + send_fmt
        self._recv_fmt = byte_order + recv_fmt

    def send(self, msg):
        packet = struct.pack(self._send_fmt, *msg)
        self._send_sock.sendto(packet, self._send_addr)

    def recv(self):
        packet, _ = self._recv_sock.recvfrom(self._recv_bytes)
        return struct.unpack(self._recv_fmt, packet)
    
    def close(self):
        self._send_sock.close()
        self._recv_sock.close()