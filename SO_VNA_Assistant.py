from SO_VNA import SO_VNA
import os
import time
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

###CHANGE THESE VALUES TO CHANGE DEFAULT VISA ADDRESS
default_TCPIP_address = '10.10.10.155'
default_port_number = 5025

def VNA_address_menu(default_TCPIP_address, default_port_number):
    print("\nBeginning connection procedure...\n")


    TCPIP_address = None
    port_number = None
    
    print("(Default TCPIP address is: " + default_TCPIP_address + ")")
    print("(Default Port is: "+ str(default_port_number) + ")\n")
    time.sleep(.5)

    address_menu_success = False
    while not address_menu_success:
        use_default_value_input = input("Use default connection details? (Y/N):")

        if use_default_value_input == "Y" or use_default_value_input == "y":
            TCPIP_address = default_TCPIP_address
            port_number = default_port_number    
            address_menu_success = True

        elif use_default_value_input == "N" or use_default_value_input == "n":
            TCPIP_address = input("\nPlease enter TCPIP address:")
            port_number = input("\nPlease enter port number:")
            address_menu_success = True

        else:
            print("\nInvalid input, please type (Y/N)")
    
    VISA_ADDRESS = "TCPIP::" + str(TCPIP_address) + "::" + str(port_number) + "::SOCKET"
    print("\nCurrent TCPIP address: " + str(TCPIP_address))
    print("Current port number: " + str(port_number))
    print("Current VISA address: " + str(VISA_ADDRESS) + "\n")
    
    print("Attempting to connect to VNA...\n")
    return VISA_ADDRESS

def create_my_VNA(VISA_ADDRESS):
    my_VNA = SO_VNA()
    connection_success = my_VNA.connect_to_VNA(VISA_ADDRESS)
    
    if connection_success:
        return my_VNA
    
    else:
        return None
    
def main_menu():
    my_VNA = None
    
    main_menu_success = False
    main_menu_printed = False
    while not main_menu_success:
        
        if not main_menu_printed:
            print("\nMain Menu")
            print("~~~~~~~~~~~~")
            if my_VNA == None:
                print("1. Connect to VNA")
            else:
                print("1. Disconnect from VNA")
            print("2. Take S parameters measurements")
            print("3. Stitch S parameter measurements")
            print("4. Plot single S parameter measurement")
            print("5. Plot multiple S parameter measurements")
            print("6. Take TDR measurement")
            print("7. Plot TDR measurement")
            print("8. Exit\n")
            time.sleep(.5)
        
        main_menu_printed = True
        
        main_menu_input = input("Choose an operation: ")
        
        if main_menu_input == "1":
            if my_VNA == None:
                VISA_ADDRESS = VNA_address_menu()
                my_VNA = create_my_VNA(VISA_ADDRESS)
                main_menu_printed = False
            
            else:
                my_VNA.disconnect()
                my_VNA = None
                print("\nVNA has been disconnected.\n")
            
        elif main_menu_input == "2":
            if my_VNA == None:    
                print("\n1. Take coarse measurement (3GHz to 9GHz, 600KHz resolution: Estimated Time = 3 minutes)")
                print("2. Take fine measurement(3GHz to 9GHz, 20KHz resolution: Estimated Time = 90 minutes)") 
                print("3. Cancel\n")
                measurement_selection_success = False
                while not measurement_selection_success:
                    measurement_type_input = input("Choose an operation: ")
                    
                    if measurement_type_input == "1":
                        take_S_parameters_measurements(my_VNA, 0, 0)
                        measurement_selection_success = True
                        
                    elif measurement_type_input == "2":
                        take_S_parameters_measurements(my_VNA, 1, 20)
                        print("Test 2")
                        measurement_selection_success = True
                    
                    elif measurement_type_input == "3":
                        measurement_selection_success = True
                        
                    else:
                        print("\nInvalid input. Please try again.\n")
                        
                main_menu_printed = False
            else:
                print("\nVNA is not connected. Please choose \"Connect to VNA\" and then try again.\n")
        
        elif main_menu_input == "3":
            stitch_S_parameter_measurements()
            main_menu_printed = False
        
        elif main_menu_input == "4":
            plot_S_parameter_measurements(multiple_plots = False)
            main_menu_printed = False
            
        elif main_menu_input == "5":
            plot_S_parameter_measurements(multiple_plots = True)
            main_menu_printed = False
            
        elif main_menu_input == "6":
            if my_VNA != None:
                take_TDR_measurement(my_VNA)
                main_menu_printed = False
            else:
                print("\nVNA is not connected. Please choose \"Connect to VNA\" and then try again.\n")
        
        elif main_menu_input == "7":
            plot_TDR_measurement()
            main_menu_printed = False
        
        elif main_menu_input == "8":
            print("\nNow exiting. Thank you for using SO_VNA_Assistant!")
            
            if(my_VNA != None):
                my_VNA.disconnect()
            
            return
    
        else:
            print("\nInvalid input. Please try again.\n")
    

def take_S_parameters_measurements(myVNA, calstate_start_number, calstate_end_number):    
    save_file_name = get_file_name()
    
    print("Now beginning S parameters measurements.\n")
    time.sleep(1)
    
    print("Now switching to NA mode...\n")
    time.sleep(1)

    myVNA.set_VNA_to_NA()
    print("Now preparing to begin taking measurements...\n")
    time.sleep(1)
    
    for calstate_number in range (calstate_start_number, calstate_end_number + 1):
        myVNA.change_CalState(calstate_number)
        time.sleep(3)
        myVNA.take_measurements()
        time.sleep(3)
        
        if calstate_number == 0:
            myVNA.save_s2p_data(str(save_file_name))
        
        else:
            myVNA.save_s2p_data(str(save_file_name) + "_" + str(calstate_number))
        
        time.sleep(3)

    print("S parameters measurements complete! Returning to main menu.\n")

#Stitches s2p files created by "take_S_parameter_measurements" into a .ntwk file
def stitch_S_parameter_measurements():
    root = Tk()
    root.withdraw()
    
    print("Please select directory that holds s2p files to be stitched.\n")
    time.sleep(1)
    directory = askdirectory()
    root.update()
    time.sleep(1)
    
    print("Please enter name for .ntwk file (Cannot contain \".\")")
    input_success = False
    while not input_success:
        save_name = input()
        
        if save_name.find(".") == -1:
            input_success = True
        
        else:
            print("\nInvalid save name. Save name cannot contain \".\"")
            
    time.sleep(1)
    
    print("\nPlease select a directory to save .ntwk file.\n")
    time.sleep(1)
    
    save_directory = askdirectory()
    root.update()
    time.sleep(1)
    root.destroy()
    
    s2p_list = []
    for s2p_file in os.listdir(directory):
        s2p_list.append(None)
    
    for s2p_file in os.listdir(directory):
        s2p_number = int(s2p_file[s2p_file.rfind("_")+1:s2p_file.rfind(".")])
        s2p_list[s2p_number-1] = rf.Network(directory + "/" + s2p_file)
    
    stitch_s2p_list(s2p_list)[0].write(save_directory + "/" + save_name)
    
    print("File successfully saved as \"" + save_directory + "/" + save_name + "\"!")
    
def stitch_s2p_list(s2p_list):
    stitched_s2p_list = []
    
    if len(s2p_list) == 1:
        return s2p_list
    
    for i in range (0, len(s2p_list)):
        if i%2 == 1:
            s2p_1 = s2p_list[i-1]
            s2p_2 = s2p_list[i]
            stitched_s2p = rf.stitch(s2p_1, s2p_2)
            stitched_s2p_list.append(stitched_s2p)
            
        if len(s2p_list)%2 != 0 and i == len(s2p_list) - 1:
            stitched_s2p_list.append(s2p_list[i])

    return stitch_s2p_list(stitched_s2p_list)

def plot_S_parameter_measurements(multiple_plots):
    root = Tk()
    root.lift()
    root.wm_attributes('-topmost', 1)
    root.withdraw()
    
    measurements_list = []
    
    if multiple_plots:
        print("\nPlease select directory that contains S parameter measurements to plot.\n")
        time.sleep(1)
        measurement_directory = askdirectory()

        for measurement_file in os.listdir(measurement_directory):
            measurements_list.append(measurement_directory + "/" + measurement_file)
        
        measurements_list = sort_measurements_list(measurements_list)
        
    else:
        print("\nPlease select S parameter measurement to plot.\n")
        time.sleep(1)
        measurement_file = askopenfilename()
        measurements_list.append(measurement_file)
    
    root.update()
    time.sleep(1)
    
    print("Please select save location for plots.\n")
    save_directory = askdirectory()
    
    time.sleep(1)
    print("Creating plots...\n")
    
    for measurement_file in measurements_list:
        plt.figure()
        plot_title = measurement_file[measurement_file.rfind("/")+1:measurement_file.rfind(".")]
        plt.title(plot_title)
        print("Creating plot: \"" + plot_title + "\"...")
        S_parameter_Network = rf.Network(measurement_file)
        S_parameter_Network.plot_s_db(1,0)
        plt.xlim([3e9,9e9])
        plt.ylim([-50,0])
        plt.savefig(save_directory + "/" + plot_title)
        time.sleep(.5)
    
    if multiple_plots:
        print("Creating plot: \"Measurement Comparison\"...\n")
        plt.figure(figsize=(10,10))
        plot_title = "Measurement Comparisons"
        plt.title(plot_title)
        plt.xlim([3e9,9e9])
        plt.ylim([-50,0])
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude (dB)")
        plot_legend = []
        
        for measurement_file in measurements_list:
            S_parameter_Network = rf.Network(measurement_file)
            plt.plot(S_parameter_Network.frequency.f, S_parameter_Network.s_db[:,1,0])
            rf_number = measurement_file[measurement_file.rfind("_")+1:measurement_file.rfind(".")]
            plot_legend.append("RF " + rf_number)
            
        plt.legend(plot_legend)
        plt.savefig(save_directory + "/" + plot_title)
        time.sleep(.5)
        
    root.destroy()
    plt.close('all')
    
    if multiple_plots:
        print("Plots finished!")
    
    else:
        print("Plot finished!")
        
def sort_measurements_list(measurements_list):
    rf_number_list = []

    for measurement_file in measurements_list:
        rf_number = measurement_file[measurement_file.rfind("_")+1:measurement_file.rfind(".")]
        rf_number_list.append(int(rf_number))
    
    for i in range(0, len(rf_number_list)):
        smallest_rf_number = rf_number_list[i]
        smallest_rf_number_index = i
        for j in range (i, len(rf_number_list)):
            if rf_number_list[j] < smallest_rf_number:
                smallest_rf_number = rf_number_list[j]
                smallest_rf_number_index = j
        
        temp_measurement = measurements_list[i]
        measurements_list[i] = measurements_list[smallest_rf_number_index]
        measurements_list[smallest_rf_number_index] = temp_measurement
        
        temp_rf_number = rf_number_list[i]
        rf_number_list[i] = rf_number_list[smallest_rf_number_index]
        rf_number_list[smallest_rf_number_index] = temp_rf_number
    
    return measurements_list

def swap(a, b):
    temp = a
    a = b
    b = temp

def take_TDR_measurement(myVNA):
    VISA_ADDRESS = VNA_address_menu()
    myVNA = SO_VNA(VISA_ADDRESS)
    print(str(VISA_ADDRESS))
    
    save_file_name = get_file_name()
    
    print("Now beginning TDR measurements.\n")
    time.sleep(1)
    
    print("Now switching to NA mode...\n")
    time.sleep(1)
    myVNA.set_VNA_to_NA()
    
    print("Now perparing to begin taking measurements...\n")
    
    myVNA.change_CalState(-1)
    time.sleep(3)
    myVNA.take_measurements()
    time.sleep(3)
    myVNA.save_s2p_data(str(save_file_name))
    time.sleep(3)
    
    print("TDR measurement complete! Returning to main menu")
    
def plot_TDR_measurement():
    root = Tk()
    root.withdraw()

    plt.ion()

    Z0 = 50
    c = 299792458
    vf = 0.695
    vs = c*vf

    print("Select non-biased s2p file")
    No_Amp_File = askopenfilename()
    root.update()
    time.sleep(1)

    print("Select biased s2p file")
    With_Amp_File = askopenfilename()
    root.update()
    time.sleep(1)

    root.destroy()

    No_Amp_Net = rf.Network(No_Amp_File)
    With_Amp_Net = rf.Network(With_Amp_File)

    No_Amp_t = No_Amp_Net.frequency.t
    With_Amp_t = With_Amp_Net.frequency.t

    No_Amp_d = No_Amp_t*vs/2
    With_Amp_d = With_Amp_t*vs/2

    No_Amp_gamma1 = np.real(No_Amp_Net.s11.s_time[:,0,0])
    With_Amp_gamma1 = np.real(With_Amp_Net.s11.s_time[:,0,0])
    No_Amp_gamma2 = np.real(No_Amp_Net.s22.s_time[:,0,0])
    With_Amp_gamma2 = np.real(With_Amp_Net.s22.s_time[:,0,0])

    No_Amp_Z1 = Z0*(1+No_Amp_gamma1)/(1-No_Amp_gamma1)
    With_Amp_Z1 = Z0*(1+With_Amp_gamma1)/(1-With_Amp_gamma1)
    No_Amp_Z2 = Z0*(1+No_Amp_gamma2)/(1-No_Amp_gamma2)
    With_Amp_Z2 = Z0*(1+With_Amp_gamma2)/(1-With_Amp_gamma2)

    plt.figure()
    plt.plot(No_Amp_d,No_Amp_Z1,label = 'No Amplifier Biased')
    plt.plot(With_Amp_d,With_Amp_Z1,label = 'With Amplifier Biased')
    plt.xlim([-0.25,3.75/2])  
    plt.xlabel('Distance [m]',fontsize = 16) 
    plt.ylabel('zImpedance [Ohm]',fontsize = 16)   
    plt.title('RF Line 2, Port 1/RF In TDR',fontsize = 16)
    plt.legend()

    plt.figure()
    plt.plot(No_Amp_d,No_Amp_Z2,label = 'No Amplifier Biased')
    plt.plot(With_Amp_d,With_Amp_Z2,label = 'With Amplifier Biased')
    plt.xlim([-0.25,3.75/2])  
    plt.xlabel('Distance [m]',fontsize = 16) 
    plt.ylabel('Impedance [Ohm]',fontsize = 16)   
    plt.title('RF Line 2, Port 2/RF Out TDR',fontsize = 16)
    plt.legend()
    
    plt.plot()
    
def get_file_name():
    print("Please enter name for save file:\n")
    save_file_name = input()
    return save_file_name

def main():
    print("Welcome to SO_VNA_Assistant!")
    main_menu()
    
main()
