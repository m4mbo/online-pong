import random
import time
from socket import *
from queue import Queue
from network.reed_solomon import ReedSolomon
from helpers.constants import *
import pickle

# Helper class to encapsulate procedures related to network connection

class Network():

    def __init__(self, port, ip, bufsize):
        self.client = socket(AF_INET, SOCK_DGRAM)
        self.port = port
        self.ip = ip
        self.bufsize = bufsize
        self.address = (ip, port)

        self.corr = ReedSolomon(ECC)  # Forward error correction

        self.packet_queue = Queue()  # Packet queue for outgoing packets

        self.last_sent_time = time.time()
        self.last_received_time = None

        self.rtt_history = []

        self.delay = 0

    def enqueue_packet(self, data):
        self.packet_queue.put(pickle.dumps(data))

    def dequeue_packet(self):
        return self.packet_queue.get()

    def send(self, noise=False, noise_level=0):
        
        timed_delay = 0

        # Looping until we have sent every packet in the queue
        while not self.packet_queue.empty():
            
            # Calculating current time
            current_time = time.time()

            if self.delay != 0:
                timed_delay = current_time + self.delay
                self.delay = 0

            if current_time < timed_delay:
                continue

            # Comparing it with the last time we sent a packet
            time_since_last_sent = current_time - self.last_sent_time

            # Preventing network from overflooding
            if time_since_last_sent >= 1 / MAX_TRANS_RATE:
                data = self.dequeue_packet()
                encoded_data = self.corr.reed_solo_encode(data)
                if noise:
                    encoded_data = self.inject_noise(encoded_data, noise_level)
                self.client.sendto(encoded_data, self.address)
                self.last_sent_time = current_time
    
    def inject_noise(self, data, noise_level):
        num_errors = noise_level
        for _ in range(num_errors):
            index = random.randint(0, len(data) - 1)
            data[index] ^= 1  # Flip a bit
        return data

    def receive(self):

        data, _ = self.client.recvfrom(self.bufsize)

        self.last_received_time = time.time()   # Updating received time

        decoded_data = self.corr.reed_solo_decode(data)
        
        return pickle.loads(decoded_data)

    def assess(self):

        rtt = self.getRTT()

        if rtt is not None:

            # Assesing only last 50 rtts
            if len(self.rtt_history) > 100:
                avg_rtt = sum(self.rtt_history) / len(self.rtt_history)
                threshold = avg_rtt * 1e4  # Testing if the new RTT is 1e4 times higher than the previous average
                self.rtt_history.pop(0)  # Remove the oldest RTT from the history
                
                if rtt > threshold:
                    print("RTT exceeded threshold:", rtt)
                    self.delay = 5e-6

            self.rtt_history.append(rtt)
            
    def getRTT(self):
        if self.last_received_time is not None:
            return self.last_received_time - self.last_sent_time 
        else:
            return None


    def close(self):
        self.client.close()

