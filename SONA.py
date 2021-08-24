# Authored By: Michael Randall
# Institution: UCSD
# Email: mrandall@ucsd.edu

# Import libraries
import visa
import time
import sys


# SONA is an agent for the FieldFox VNA line.
# SONA facilitates connecting to the VNA and creating a VNA "session".
# The VNA session acts as a connection to the VNA.
# SONA also contains functions used for taking NA measurements.
class SONA:

    # Class initilization 
    def __init__(self):
        self.session = None
        
    # Used to connect to VNA. Creates and returns a VISA session that is connected to the VNA.
    def connect_to_vna(self, visa_address):
        print("Attempting to connect to VNA...\n")

        # Visa is used to connect to VNA
        resource_manager = visa.ResourceManager()

        # Opens a session with VNA. Sets termination character.
        # Termination character is automatically added to end of outgoing messages.
        try:
            # Attmpts to connect to VNA.
            new_session = resource_manager.open_resource(visa_address)
            
            # If connection was successful
            if new_session is not None:
                if new_session.resource_name.startswith('ASRL') or new_session.resource_name.endswith('SOCKET'):
                    new_session.read_termination = '\n'

                print("Connected!")

                self.session = new_session
                return True
            
        except:
            print("Failed to connect to VNA. Check that VNA is on and connected.")
            return False

    # Sets VNA to NA mode. Loop waits for VNA to respond. Exits if incapable.
    def set_vna_to_network_analyzer_mode(self):

        # Tells VNA to change to NA mode.
        # "*OPC?" Tells VNA to send confirmation when finished.
        self.session.write('INST "NA";*OPC?')

        network_analyzer_set_success = False
        network_analyzer_set_loop_count = 0
        while not network_analyzer_set_success:

            # VNA has 10 attempts to connect.
            if network_analyzer_set_loop_count == 10:
                print("Setting VNA mode failed. Program will now close. Check VNA.")
                quit()

            try:
                # Attempts to read confirmation from VNA.
                # Throws error if confirmation hasn't been sent.
                network_analyzer_set_success = self.session.read()
                print("VNA set to NA mode. Configuring Settings...")
                time.sleep(1)

                # Tells VNA to hold measurements (Turn off continuous measurements).
                self.session.write('INIT:CONT 0')
                time.sleep(1)

                # Tells VNA to show all 4 S parameter measurements.
                # Not stricly necessary if not physically watching VNA.
                self.session.write('CALC:PAR:COUN 4')
                time.sleep(1)

                print("VNA Ready.\n")
                time.sleep(1)
                return 1

            except:
                print("Waiting for VNA to be set to NA mode... (" + str(10 - network_analyzer_set_loop_count)
                      + " attempts remaining)")

            network_analyzer_set_loop_count += 1
            time.sleep(1)

    # Completes 3 measurements in current state
    def take_measurements(self):

        # Take three measurements
        for current_measurement_number in range(1, 4):
            print("Beginning measurement number " + str(current_measurement_number) + "...")

            # Tells VNA to take a single sweep.
            # "*OPC?" Tells VNA to send confirmation when finished.
            self.session.write('INIT:IMM;*OPC?')

            measurement_success = '0'
            measurement_loop_count = 0

            while measurement_success == '0':

                # VNA has 10 attempts to finish measurement
                if measurement_loop_count == 10:
                    print("Meaurement number " + str(current_measurement_number)
                          + " has failed. Program will now exit. Check VNA.")

                try:
                    # Attempts to read confirmation from VNA
                    # Throws error if confirmation hasn't been sent.
                    measurement_success = self.session.read()
                    time.sleep(.5)

                    if current_measurement_number == 3:
                        print("Meaurement number 3 successful!\nAll Measurements successful!\n")

                    if current_measurement_number != 3:
                        print("Measurement number " + str(current_measurement_number)
                              + " successful! Program will attempt next measurement in 3 seconds.\n")

                        # Autoscales all traces.
                        # Not strictly necessary if not physically watching VNA.
                        for trace_number in range(1, 5):
                            # Tells VNA to autoscale trace #trace_number
                            self.session.write("DISP:WIND:TRAC" + str(trace_number) + ":Y:AUTO")
                            time.sleep(.5)

                except:
                    print("Waiting for measurement to end... (" + str(10 - measurement_loop_count)
                          + " attempts remaining)")

                measurement_loop_count += 1
                time.sleep(1)

            time.sleep(1)

        return 1

    # Changes the current calstate on the VNA to the desired calstate number
    # VNA expects calstates to be in format "Calstate_#.sta"
    def change_calstate(self, calstate_number):
        print("Switching CalState to Calstate " + str(calstate_number) + "...")

        # Tells VNA to look in internal memmory.
        self.session.write('MMEM:CDIR "[INTERNAL]:"')
        time.sleep(1)

        # Tells VNA to load "Calstate_#.sta".
        # "*OPC?" Tells VNA to send confirmation when finished.
        self.session.write('MMEMory:LOAD:STATe \"CalState_' + str(calstate_number) + '.sta\";*OPC?')
        state_set_success = "0"
        state_set_loop_count = 0

        while state_set_success == '0':

            # VNA has 10 attempts to switch CalState.
            if state_set_loop_count == 10:
                print("Setting state to CalState " + str(calstate_number)
                      + " has failed. Program will now exit. Check VNA.")
                exit()

            try:
                # Attempts to read confirmation from VNA.
                # Throws error if confirmation has not been sent.
                state_set_success = self.session.read()
                print("State set to CalState " + str(calstate_number) + "!\n")

            except:
                print("Waiting for state to change... (" + str(10 - state_set_loop_count)
                      + " attempts remaining)")

            state_set_loop_count += 1
            time.sleep(1)

    # Saves s2p on usbdisk
    def save_s2p_data(self, file_name):
        print("Attempting to save data as " + str(file_name) + ".s2p")

        # Tells VNA to change current directory to "[USBDISK]:\".
        self.session.write('MMEM:CDIR "[USBDISK]:\"')
        time.sleep(1)

        # Tells VNA to save current traces to "file_name.s2p" on USBDISK.
        # "*OPC?" Tells VNA to send confirmation when finished.
        self.session.write('MMEM:STOR:SNP \"' + str(file_name) + '.s2p\";*OPC?')

        save_success = '0'
        save_loop_count = 0

        while save_success == '0':

            # VNA has 10 attempts to save data.
            if save_loop_count == 10:
                print("Saving data failed. Program will now exit. Check VNA.")
                sys.exit()

            try:
                # Attempts to read confirmation from VNA.
                # Throws error if confirmation has not been sent.
                save_success = self.session.read()
                print("Data successfully saved as: " + str(file_name) + ".s2p on USB!\n")
                time.wait(1)
                return

            except:
                print("Waiting on data to save... (" + str(10 - save_loop_count) + " attempts remaining)")

            save_loop_count += 1
            time.sleep(5)

    # Disconnects from VNA.
    def disconnect(self):
        # Clears current session.
        self.session.clear()

        # Closes session.
        self.session.close()

# Thank you for using SONA!#
