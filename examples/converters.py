import socket
import struct
import numpy as np
from networking import UDP
from scipy.spatial.distance import cdist
from typing import Generator


class UDPConverter:
    def __init__(self, header_size: int = 2, sensing_range: float = 1.0) -> None:
        self._header_size = header_size
        self._sensing_range = sensing_range

    def __unwrap(self, state: tuple) -> tuple:
        # Create buffers to store data into from packet
        num_drones, _ = state[:self._header_size]
        ids = np.zeros(num_drones, dtype=np.uint32)
        locs = np.empty((num_drones, 3), dtype=np.float32) 
        rots = np.empty((num_drones, 2), dtype=np.float32) 
        dets = np.full(num_drones, fill_value=False, dtype=bool)

        data = state[self._header_size:]

        ids[:] = data[0::7]     # DroneIds
        locs[:, 0] = data[1::7] # x
        locs[:, 1] = data[2::7] # y
        locs[:, 2] = data[3::7] # z
        rots[:, 0] = data[4::7] # phi
        rots[:, 1] = data[5::7] # theta
        dets[:] = data[6::7]    # Detections

        return num_drones, ids, locs, rots, dets
    
    def udp_to_sensor_data(self, state: tuple) -> Generator:
        # Extract tensors of locations, rotations and detections
        # from state packet (sequence of ints, floats and bools).
        num_drones, drone_ids, locs, rots, dets = self.__unwrap(state)

        # Compute pairwise distances between drones
        dists = cdist(locs, locs, metric="euclidean")

        # Derive sensor data
        for i, drone_id in enumerate(drone_ids):
            result = {
                'self_loc': locs[i],
                'self_rot': rots[i],
                'other_locs': locs[dists[i] < self._sensing_range],
                'detected': dets[i]
            }
            yield drone_id, result

    def commands_to_udp(self, commands: list) -> tuple:
        # TODO: add IDs
        return tuple([x for xs in commands for x in xs])



if __name__ == '__main__':
    num_drones = 2

    udp = UDP(
        ip = "127.0.0.1",
        send_port=5000,
        recv_port=5000,
        send_fmt="ii" + num_drones * "ifffff?",
        recv_fmt="ii" + num_drones * "ifffff?"
    )
    sensing = Sensing()

    # (#drones, #survivors_detected, #drones x [droneId, x, y, z, phi, theta, detection])
    def send_sim_state_udp(n=100):
        msg = [n, np.random.randint(0, 10)]
        for i in range(n):
            x, y, z, phi, theta = np.random.random(5)
            detection = np.random.random() > .8
            msg += [i, x, y, z, phi, theta, detection]
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet = struct.pack("ii" + num_drones * "ifffff?", *msg)
        sock.sendto(packet, ("127.0.0.1", 5000))
    

    send_sim_state_udp(n=num_drones)

    sim_state = udp.recv()

    for sensor_data in sensing.to_sensor_data(sim_state):
        print(sensor_data)

