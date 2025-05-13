from machine import SoftI2C, Pin
import time

__version__ = '0.2.1'
__author__ = 'Roberto Sánchez'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

# I2C address for SHT40, usually 0x44
DEFAULT_I2C_ADDRESS = 0x44

class SHT40:
    """
    SHT40 sensor driver in pure python based on I2C bus

    References: 
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Sensirion_Humidity_Sensors_SHT4x_Datasheet_digital.pdf
    """
    
    MEASURE_HIGH_PRECISION_CMD = b'\xFD\x00'
    RESET_CMD = b'\x94\x00'

    def __init__(self, i2c, delta_temp=0, delta_hum=0, i2c_address=DEFAULT_I2C_ADDRESS):
        self.i2c = i2c
        self.i2c_addr = i2c_address
        self.set_delta(delta_temp, delta_hum)
        time.sleep_ms(50)

    def is_present(self):
        """
        Return true if the sensor is correctly connected, False otherwise
        """
        return self.i2c_addr in self.i2c.scan()
    
    def set_delta(self, delta_temp=0, delta_hum=0):
        """
        Apply a delta value on the future measurements of temperature and/or humidity
        The units are Celsius for temperature and percent for humidity (can be negative values)
        """
        self.delta_temp = delta_temp
        self.delta_hum = delta_hum
    
    def send_cmd(self, cmd_request, response_size=6, read_delay_ms=10):
        """
        Send a command to the sensor and read (optionally) the response
        """
        try:
            self.i2c.start()
            self.i2c.writeto(self.i2c_addr, cmd_request)
            if not response_size:
                self.i2c.stop()
                return
            time.sleep_ms(read_delay_ms)
            data = self.i2c.readfrom(self.i2c_addr, response_size)
            self.i2c.stop()
            return data
        except OSError as ex:
            print(ex)
            if 'I2C' in ex.args[0]:
                raise SHT40Error(SHT40Error.BUS_ERROR)
            raise ex

    def reset(self):
        """
        Send a soft-reset to the sensor
        """
        return self.send_cmd(SHT40.RESET_CMD, None)

    def measure(self, raw=False):
        """
        If raw==True returns a bytearray with sensor direct measurement otherwise
        It gets the temperature (T) and humidity (RH) measurement and returns them.
        
        The units are Celsius and percent
        """
        data = self.send_cmd(SHT40.MEASURE_HIGH_PRECISION_CMD, 6)

        if raw:
            return data

        t_ticks = (data[0] << 8) | data[1]
        rh_ticks = (data[3] << 8) | data[4]

        t_celsius = -45 + 175 * (t_ticks / 65535.0) + self.delta_temp
        rh = 100 * (rh_ticks / 65535.0) + self.delta_hum

        return t_celsius, rh


class SHT40Error(Exception):
    """
    Custom exception for errors on sensor management
    """
    BUS_ERROR = 0x01 

    def __init__(self, error_code=None):
        self.error_code = error_code
        super().__init__(self.get_message())
    
    def get_message(self):
        if self.error_code == SHT40Error.BUS_ERROR:
            return "Bus error"
        else:
            return "Unknown error"
