import time
from multiprocessing import Process
from ..network.network import Network
from ..helpers.constants import *

def client_process_freq(client_id, freq):
    network = Network(PORT, 'localhost', BUFSIZE)
    print(f"Client {client_id} started")
    try:
        while True:
            # Simulate sending data to the server at a high frequency
            network.enqueue_packet(f"Data from Client {client_id}")
            network.send()
            time.sleep(freq) 
    except KeyboardInterrupt:
        pass
    finally:
        network.close()


def client_process_noise(client_id, noise_level):
    network = Network(PORT, 'localhost', BUFSIZE)
    print(f"Client {client_id} started")
    try:
        while True:
            # Simulate sending data to the server at a high frequency
            data = "Noise"
            
            # Send the noisy data to the server
            network.enqueue_packet(data)
            network.send(True, noise_level)

            received_data = network.receive()
            
            print("Original data: ", data)
            print("Corrected data: ", received_data)
            print("\n")

    except KeyboardInterrupt:
        pass
    finally:
        network.close()



def test(type):
    max_clients = 2  # Number of clients to simulate
    processes = []

    try:
        # Start multiple client processes

        if type == "noise":
            p = Process(target=client_process_noise, args=(0, 6))
            processes.append(p)
            p.start()
            time.sleep(0.1)
        else:
            for i in range(max_clients):
                p = Process(target=client_process_freq, args=(i, 0.001))
                processes.append(p)
                p.start()
                time.sleep(0.1)  # Add a small delay between starting processes
    except KeyboardInterrupt:
        print("Terminating...")
    finally:
        # Terminate all client processes upon completion
        for p in processes:
            p.terminate()
            p.join()

if __name__ == '__main__':
    test("none")
