init 4 python:
    #config.log = "debuglog.txt"
    registerAddition("MASMC", "MASM Communicator", "0.1.6")
    import signal
    import socket
    import select
    import threading
    import subprocess
    import time
    import atexit

    if additionIsEnabled("MASMC"):
        # Threaded socket communicator
        class MASM_Communicator:
            data = []
            server = None
            masmApp = None
            appPath = None
            appExists = False

            def __init__(self):
                self.clientAddr = None
                self.thread = None

            def connectMASM(self):
                ''' # TCP
                self.server.listen(5)
                while True:
                    try:
                        MASM_Communicator.client, self.clientAddr = self.server.accept()
                    except socket.error:
                        continue
                    break
                '''
                MASM_Communicator.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                MASM_Communicator.server.settimeout(0.01)
                MASM_Communicator.server.bind(("127.0.0.1", 12345))

                self.thread = threading.Thread(target = self.communicateWithClient)
                self.thread.setDaemon(True)
                self.thread.start()

            def communicateWithClient(self):
                while True:
                    received = None
                    try:
                        #rtr, rtw, err = select.select((MASM_Communicator.client,), (), (), 0)
                        #if rtr:
                        received, addr = self.server.recvfrom(64)
                        if len(received) == 0:
                            received = received.decode('utf-8')
                            break
                    except socket.error: # No data
                        pass

                    if received is not None:
                        #renpy.log("MASMC received data: {}".format(received))
                        MASM_Communicator.data.append(received)

                    if MASM_Communicator.masmApp is not None:
                        poll = MASM_Communicator.masmApp.poll()
                        if poll == None:
                            MASM_Communicator.appExists = True
                        else:
                            MASM_Communicator.appExists = False

                    time.sleep(0.001) # ease up tiny bit
                    
            @staticmethod
            def hasData(dat):
                if dat in MASM_Communicator.data:
                    MASM_Communicator.data.remove(dat)
                    return True
                else:
                    return False

            @staticmethod
            def canUse():
                return MASM_Communicator.appExists

            @staticmethod
            def clientSend(toSend):
                if MASM_Communicator.server is not None:
                    MASM_Communicator.server.sendto(toSend.encode('utf-8'), ("127.0.0.1", 23456))

            @staticmethod
            def exiting():
                if MASM_Communicator.masmApp is not None:
                    poll = MASM_Communicator.masmApp.poll()
                    if poll == None:
                        os.kill(MASM_Communicator.masmApp.pid, signal.SIGTERM) # do it peacefully Python

            @staticmethod
            def startMASM():
                for dirpath,subdirs,files in os.walk('.'):
                    if 'MASM' in subdirs:
                        MASM_Communicator.appPath = dirpath
                        break

                if MASM_Communicator.appPath is not None:
                    if renpy.windows: # If we are running on Windows OS
                        MASM_Communicator.masmApp = subprocess.Popen(renpy.loader.transfn(os.path.join(MASM_Communicator.appPath, '/MASM/MASM.exe'))) # Open MASM application subprocess
                    elif renpy.linux or renpy.macintosh: # Linux / Mac..
                        MASM_Communicator.masmApp = subprocess.Popen(renpy.loader.transfn(os.path.join(MASM_Communicator.appPath, '/MASM/MASM'))) # Good luck!

                    if MASM_Communicator.masmApp is not None:
                        MASM_Communicator.appExists = True

                atexit.register(MASM_Communicator.exiting) # Because subprocesses
                signal.signal(signal.SIGTERM, MASM_Communicator.exiting)
                signal.signal(signal.SIGINT, MASM_Communicator.exiting)

        communicator = MASM_Communicator()
        communicator.startMASM()
        communicator.connectMASM()

        if isAdditionFirstRun("MASMC"):
            MASM_Communicator.clientSend("first")
        else:
            MASM_Communicator.clientSend("notFirst")