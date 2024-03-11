import logging
from socket import *
from _thread import start_new_thread
import time
import psutil
from helpers.constants import *
from network.reed_solomon import ReedSolomon
from objects import paddle, ball
import pickle

# No need for queue on server side since we
# will only receive and forward packets

# Global variables
HOST = 'localhost'
ADDR = (HOST, PORT)

corr = ReedSolomon(ECC)

server_socket = socket(AF_INET, SOCK_DGRAM)

inital_paddles = [paddle.Paddle(0, (WIN_HEIGHT - PADDLE_HEIGHT) / 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255)), paddle.Paddle(WIN_WIDTH - PADDLE_WIDTH, (WIN_HEIGHT - PADDLE_HEIGHT) / 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))]
initial_ball = ball.Ball(WIN_WIDTH / 2, WIN_HEIGHT / 2, BALL_RADIUS, (255, 255, 255))

paddles = {}    # Dictionary mapping paddles and addresses
balls = {}      # Dictionary mapping balls and addresses

def initialize(addr):

    if len(paddles) == 0:
        paddles[addr] = inital_paddles[0]
        balls[addr] = initial_ball
    elif len(paddles) == 1:
        currAddr = next(k for k, v in paddles.items() if k != addr)
        if paddles[currAddr].x == 0:
            paddles[addr] = inital_paddles[1]
            paddles[currAddr] = inital_paddles[0]
        else:
            paddles[addr] = inital_paddles[0]
            paddles[currAddr] = inital_paddles[1]
        balls[addr] = initial_ball
        balls[currAddr] = initial_ball
    else:
        # If we have more than 2 clients trying to connect
        return False
    return True

def client_thread(data, addr):

    if isinstance(data, paddle.Paddle):
        # We received a paddle
        paddles[addr] = data
        reply = next(v for k, v in paddles.items() if k != addr)
    elif isinstance(data, ball.Ball):
        # We received a ball
        balls[addr] = data
        reply = next(v for k, v in balls.items() if k != addr)
    else:
        reply = data

    encoded_data = corr.reed_solo_encode(pickle.dumps(reply))

    server_socket.sendto(encoded_data, addr)

    #print ("Received ", data)
    #print ("Sending ", reply)

def process_data(decoded_data, addr, log=False):
    if len(paddles) < 2 and not log:
        encoded_data = corr.reed_solo_encode(pickle.dumps("wait"))
        server_socket.sendto(encoded_data, addr)
        return False
    elif decoded_data == "init_paddle":
        encoded_data = corr.reed_solo_encode(pickle.dumps(paddles[addr]))
        server_socket.sendto(encoded_data, addr)
    elif decoded_data == "init_ball":
        encoded_data = corr.reed_solo_encode(pickle.dumps(balls[addr]))
        server_socket.sendto(encoded_data, addr)
    elif decoded_data == "end":
        paddles.pop(addr)
        balls.pop(addr)
    else:
        start_new_thread(client_thread, (decoded_data, addr))
    return True

def main():

    try:
        server_socket.bind(ADDR)
    except error as e:
        str(e)

    print("Waiting for data, server started")

    try:

        # Looping infinetely until we receive data
        while True:

            data, addr = server_socket.recvfrom(BUFSIZE)

            # Verifying if this address has sent data before
            if addr not in paddles:
                if not initialize(addr):
                    continue
                else:
                    print("Address", addr, "added")

            decoded_data = corr.reed_solo_decode(data)
            decoded_data = pickle.loads(decoded_data)

            if not process_data(decoded_data, addr):
                continue
            
    except KeyboardInterrupt:
        print("Server stopped")

def log():

    try:
        server_socket.bind(ADDR)
    except error as e:
        str(e)
    
    logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        start_time = time.time()  # Start time for calculating throughput
        total_data_received = 0  
        
        while True:
            # Measure response time
            start_resp_time = time.time()
            
            data, addr = server_socket.recvfrom(BUFSIZE)
            decoded_data = corr.reed_solo_decode(data)
            decoded_data = pickle.loads(decoded_data)

            if not process_data(decoded_data, addr, True):
                continue
            
            # Logging response time
            end_resp_time = time.time()
            response_time = end_resp_time - start_resp_time
            logging.info(f'Response Time: {response_time}')

            # Accumulate length of data received
            total_data_received += len(data)

            # Measure resource utilization
            cpu_percent = psutil.cpu_percent()  # CPU utilization as a percentage
            mem_percent = psutil.virtual_memory().percent  # Memory utilization as a percentage
            logging.info(f'CPU Utilization: {cpu_percent}%')
            logging.info(f'Memory Utilization: {mem_percent}%')

    except KeyboardInterrupt:

        end_time = time.time()
        time_elapsed = end_time - start_time
        throughput = total_data_received / time_elapsed  # Total throughput in bytes per second
        logging.info(f'Throughput: {throughput} B/s')

        logging.info('Server stopped')


if __name__ == '__main__':
    main()
    #log()