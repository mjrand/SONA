###Import libraries
import visa
import time
import sys

class SO_VNA:
    
    def __init__(self, VISA_ADDRESS = 'TCPIP::10.10.10.155::5025::SOCKET'):
        self.session = None
        
    ###Used to connect to VNA. Creates and returns a VISA session that is connected to the VNA.
    def connect_to_VNA(self, VISA_ADDRESS):
        new_session = None
        
        ###Visa is used to connect to VNA
        resourceManager = visa.ResourceManager()

        ###Opens a session with VNA. Sets termination character. 
        ###Termination character is automatically added to end of outgoing messages.
        try:
            new_session = resourceManager.open_resource(VISA_ADDRESS)
            
        except:
            print("Failed to connect to VNA. Check that VNA is on and connected.")
            return False
        
        if new_session != None:
            if new_session.resource_name.startswith('ASRL') or new_session.resource_name.endswith('SOCKET'):
                    new_session.read_termination = '\n'

            ###VNA identifies itself
            new_session.write('*IDN?')
            idn = new_session.read()

            ###Prints connection info once connected
            print("Connected!")
            print('IP: %s\nHostname: %s\nPort: %s\n' %
                (new_session.get_visa_attribute(visa.constants.VI_ATTR_TCPIP_ADDR),
                new_session.get_visa_attribute(visa.constants.VI_ATTR_TCPIP_PORT), idn.rstrip('\n')))
            
            self.session = new_session
            return True
        
    ###Sets VNA to NA mode. Loop waits for VNA to respond. Exits if incapable.
    def set_VNA_to_NA(self):
        self.session.write('INST "NA";*OPC?')

        NA_set_success = '0'
        NA_set_loop_count = 0
        while NA_set_success == '0':

            if NA_set_loop_count == 10:
                print("Setting VNA mode failed. Program will now close. Check VNA.")
                quit()

            try:
                NA_set_success = self.session.read()
                print("VNA set to NA mode. Configuring Settings...")
                time.sleep(1)
                self.session.write('INIT:CONT 0')
                time.sleep(1)
                self.session.write('CALC:PAR:COUN 4')
                time.sleep(1)
                print("VNA Ready.\n")
                time.sleep(1)
                return 1

            except:
                print("Waiting for VNA to be set to NA mode... (" + str(10 - NA_set_loop_count)
                      + " attempts remaining)")

            NA_set_loop_count += 1
            time.sleep(1)


    ###Completes 3 measurements in current state
    def take_measurements(self):

        for current_measurement_number in range(1,4):
            print("Beginning measurement number " + str(current_measurement_number) + "...")
            self.session.write('INIT:IMM;*OPC?')

            measurement_success = '0'
            measurement_loop_count = 0

            while measurement_success == '0':

                if measurement_loop_count == 10:
                    print("Meaurement number " + str(current_measurement_number)  
                          + " has failed. Program will now exit. Check VNA.")

                try:
                    measurement_success = self.session.read()
                    time.sleep(.5)
    
                    if current_measurement_number == 3:
                        print("Meaurement number 3 successful!\nAll Measurements successful!\n")
                    
                    if current_measurement_number != 3:
                        print("Measurement number " + str(current_measurement_number) 
                          + " successful! Program will attempt next measurement in 3 seconds.\n")

                    for trace_number in range (1,5):
                        self.session.write("DISP:WIND:TRAC" + str(trace_number)+":Y:AUTO")
                        time.sleep(.5)

                except:
                    print("Waiting for measurement to end... (" + str(10-measurement_loop_count) 
                          + " attempts remaining)")

                measurement_loop_count +=1
                time.sleep(1)

            time.sleep(1)

        return 1


    ###Changes the current calstate on the VNA to the desired calstate number
    def change_CalState(self, calstate_number):
        print("Switching CalState to Calstate " + str(calstate_number) + "...")
        self.session.write('MMEM:CDIR "[INTERNAL]:"')
        time.sleep(1)
        self.session.write('MMEMory:LOAD:STATe \"CalState_' + str(calstate_number) + '.sta\";*OPC?')
        state_set_success = "0"
        state_set_loop_count = 0

        while state_set_success == '0':

            if state_set_loop_count == 10:
                print("Setting state to CalState " + str(calstate_number) 
                      + " has failed. Program will now exit. Check VNA.")
                exit()

            try:
                state_set_success = self.session.read()
                print("State set to CalState " + str(calstate_number) + "!\n")

            except:
                print("Waiting for state to change... (" + str(10-state_set_loop_count) 
                      + " attempts remaining)")

            state_set_loop_count +=1
            time.sleep(1)


    def save_s2p_data(self, file_name):
        print ("Attempting to save data as " + str(file_name) + ".s2p")
        self.session.write('MMEM:CDIR "[USBDISK]:\"')
        time.sleep(1)
        self.session.write('MMEM:STOR:SNP \"' + str(file_name) +'.s2p\";*OPC?')

        save_success = '0'
        save_loop_count = 0

        while save_success == '0':
            if(save_loop_count == 10):
                print("Saving data failed. Program will now exit. Check VNA.")
                sys.exit()

            try:
                save_success = self.session.read()
                print("Data successfully saved as: " + str(file_name) +".s2p on USB!\n")
                time.wait(1)
                return

            except:
                print("Waiting on data to save... (" + str(10 - save_loop_count) + " attempts remaining)")
                
            save_loop_count += 1
            time.sleep(5)
        
    def disconnect(self):
        self.session.clear()
        self.session.close()
        
    def session_test(self):
        self.session.write("*IDN?")
        print(self.session.read())
