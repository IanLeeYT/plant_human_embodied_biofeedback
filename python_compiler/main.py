import RealTimeAudio_cmpl
import Manual_cmpl
import Audio_cmpl

if __name__ == "__main__":

    # Initialize parameters
    com_port = "/dev/cu.usbmodem142301"
    transfer_rate = 1

    dtime = 0.1
    freq = 22050

    input_freq = 44100
    blocks = 10
    blocksize = input_freq // blocks
    buffer_size = blocks * 2

    # Compilers
    RTA_Compiler = RealTimeAudio_cmpl.RTA_Compiler(com_port,
                                                   input_freq, blocksize, buffer_size)
    Manual_Compiler = Manual_cmpl.Manual_Compiler(
        transfer_rate, com_port)
    Audio_Compiler = Audio_cmpl.Audio_Compiler(
        dtime, transfer_rate, com_port, freq)

    valid = ["1", "2", "3", "quit", "end"]
    user = None
    while True:
        print("\n")
        print("1) Audio File Compilation")
        print("2) Real Time Audio Compilation")
        print("3) Manual testing")
        print("\n")

        user = input("Enter Compiler index to run or quit: ").strip()
        while user not in valid:
            # print("Invalid. Try again")
            user = input("Enter Compiler index to run or quit: ").strip()

        if user == "1":
            Audio_Compiler.interactive()
        elif user == "2":
            RTA_Compiler.interactive()
        elif user == "3":
            Manual_Compiler.interactive()
        elif user == "quit" or user == "end":
            break
        else:
            raise Exception("Program error")
    print("Thank you")
