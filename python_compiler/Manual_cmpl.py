import serial
import numpy as np
import time
import struct
import re


class Manual_Compiler:

    def __init__(self, transfer_rate, com_port):
        # Initialize constants
        self.transfer_rate = transfer_rate
        self.tests = self.default_tests()

        # Communication port
        self.com_port = com_port
        self.baud_rate = 9600

    def default_tests(self):
        test1 = np.array(
            [33, 33, 33, 32, 32, 32, 22, 1, 1, 1, 34, 1, 1, 1, 34, 1, 1])
        test2 = np.array([10, 20, 30, 10, 10, 30, 20, 10])
        test3 = np.array([26, 1, 1, 26, 1, 1, 26, 1, 1, 26, 1, 1, 26, 1, 1])
        test4 = np.array([50, 50, 50, 50, 50, 1, 1, 1, 1, 1, 1, 1])
        test5 = np.array([50, 60, 60, 50, 50, 40, 40,
                         30, 30, 30, 25, 25, 20, 20])
        return [test1, test2, test3, test4, test5]

    def send_serial(self, data):
        """
    send serial data to arduino
    run index [test_i] of self.tests
    """
        ser = serial.Serial(self.com_port, self.baud_rate)
        time.sleep(2)  # wait for serial connection
        sending = True
        try:
            while sending:
                for d in data:
                    print(d)
                    ser.write(struct.pack('>B', d))
                    time.sleep(self.transfer_rate)
        except KeyboardInterrupt:
            print("quit process")
        ser.write(struct.pack('>B', 1))
        ser.write(struct.pack('>B', 1))
        ser.close()

    def add_test(self, new_test):
        self.tests.append(new_test)

    def interactive(self):
        """
    Interactive user session

    when input non-negative integer, the pressure regulator will run constant digital value
    when input non-negative integer followed by "t" (stands for test), the pressure regulator will run self.test[i]
    when input is "end" or "quit", return
    """
        while True:
            user = input("Input or quit: ")
            if user == "end" or user == "quit":
                break
            elif re.fullmatch(r'\d+', user):
                user = [int(user)]
            elif re.fullmatch(r't\d+', user):
                try:
                    user = self.tests[int(user[1:])-1]
                except:
                    print("index of test not found")
                    continue
            else:
                continue
            self.send_serial(user)


if __name__ == "__main__":

    com_port = "/dev/cu.usbmodem141101"
    transfer_rate = 1

    compiler = Manual_Compiler(transfer_rate, com_port)
    compiler.interactive()
