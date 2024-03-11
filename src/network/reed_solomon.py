from reedsolo import RSCodec

# Helper class for handling forward error correction(FEC)
# Uses reed solomon codes
class ReedSolomon():

    def __init__(self, ecc):
        self.rsc = RSCodec(ecc)

    # Expects serialized data
    def reed_solo_encode(self, data):
        return self.rsc.encode(data)
    
    # Returns serialized data
    def reed_solo_decode(self, data):
        decoded_data = self.rsc.decode(data)[0]
        # Logging if we corrected an error
        if not self.find_discrepancy(data, decoded_data):
            print("Message corrected")

        return decoded_data
    
    def find_discrepancy(self, byte_array, substring):
        return byte_array.find(substring) != -1
