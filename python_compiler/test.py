import serial
import numpy as np
import time
import struct

def send_serial(port, file_name, transfer_rate):
  """
  send serial data to arduino
  """
  baudrate = 9600
  ser = serial.Serial(port, baudrate)
  time.sleep(2)   #wait for serial connection
  sending = True 
  try:
    while sending:
      data = file_name
      for d in data:
        print(d)
        ser.write(struct.pack('>B',d))
        time.sleep(transfer_rate)
  except KeyboardInterrupt:
    pass
  ser.close()

if __name__ == "__main__":

  # communication port
  com_port = "/dev/cu.usbmodem14201"
  
  # Initialize parameters
  transfer_rate = 1
  dtime = 0.1
  noise = 0


  # here are the tests 
  test1 = np.array([33,33,33,32,32,32,22,1,1,1,34,1,1,1,34,1,1])
  test2 = np.array([10,20,30,10,10,30,20,10])
  test3 = np.array([255,1,1,255,1,1,255,1,1,255,1,1,255,1,1])
  test4 = np.array([26,1,1,26,1,1,26,1,1,26,1,1,26,1,1])

  # change the second variable [test] to try out different tests
  # while True:
  #   input = int(input("Input: "))
  #   if input == "end" or input == "quit":
  #     break
  #   send_serial(com_port, [input], transfer_rate)

  send_serial(com_port, test1, transfer_rate)