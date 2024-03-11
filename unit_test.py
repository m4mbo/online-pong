import unittest
from unittest.mock import patch
from network.reed_solomon import ReedSolomon
from client import interpolateBalls
from objects.ball import Ball
from helpers.constants import *

class UnitTest(unittest.TestCase):
    def test_reed_solo(self):
        # Test reed_solo_encode/decode method
        reed_solomon = ReedSolomon(ecc=10)  # Assuming you need to pass some parameter like 'ecc'
        input_data = b'Test data'  # Define input data as bytes
        encoded_data = reed_solomon.reed_solo_encode(input_data)
        decoded_data = reed_solomon.reed_solo_decode(encoded_data)
        self.assertEqual(decoded_data, input_data)
    
    @patch('network.network.Network')
    def test_interpolation(self, mock_network):
        # Set up mock network instance
        network_instance = mock_network.Network.return_value
        # Define expected data to be received from the network
        mock_received_data = Ball(200, 150, BALL_RADIUS, (0, 0, 0))
        mock_received_data.direction = [0, 1]
        # Set up the side effect for the receive method of the network instance
        network_instance.receive.side_effect = [mock_received_data]
        
        # Set up initial ball position and direction
        initial_ball = Ball(100, 100, BALL_RADIUS, (0, 0, 0))
        initial_ball.direction = [1, -1]

        interpolateBalls(initial_ball, network_instance)
        
        expected_x_position = 150
        expected_y_position = 125
        expected_direction = [0, 1]
        
        self.assertEqual(initial_ball.x, expected_x_position)
        self.assertEqual(initial_ball.y, expected_y_position)
        self.assertEqual(initial_ball.direction, expected_direction)


    def test_reset_position(self):
        ball = Ball(100, 100, BALL_RADIUS, (0, 0, 0))
        ball.x = 50
        ball.y = 50
        ball.resetPos()

        self.assertEqual(ball.x, ball.init_x)
        self.assertEqual(ball.y, ball.init_y)
    #def test_ball_movement(self):
       # ball = Ball(x=1, y=1, )
if __name__ == '__main__':
    unittest.main()
