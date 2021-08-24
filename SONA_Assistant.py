# Authored by: Michael Randall
# Institution: UCSD
# Email: mrandall@ucsd.edu

# Import dependencies
from SONA import SONA
import os
import time
import smtplib
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory


# Greets and calls main menu function.
def main():
    print("Welcome to SONA_Assistant!")
    main_menu()


# Main menu for SONA_Assistant.
def main_menu():
    # vna_session is the current connection to the VNA.
    # vna_session begins as none until connection is created.
    # vna_session is used to control VNA.
    vna_session = None

    # main_menu_success is used to break main_menu loop.
    main_menu_success = False

    # main_menu_printed is used to track when to print main menu.
    main_menu_printed = False

    plot_settings = [True, (10, 10), (3e9, 9e9), (-50, 0)]

    # Email alerts are turned off by default.
    email_alerts_address_list = []

    # Main menu is run until exited by user, controlled my main_menu_success.
    while not main_menu_success:

        if not main_menu_printed:

            # Main menu lists SONA_Assistant functions.
            print("\nMain Menu")
            print("~~~~~~~~~~~~")
            if vna_session is None:
                print("1. Connect to VNA")
            else:
                print("1. Disconnect from VNA")
            print("2. Take S parameters measurements")
            print("3. Stitch S parameter measurements")
            print("4. Plot single S parameter measurement")
            print("5. Plot multiple S parameter measurements")
            print("6. Take TDR measurement")
            print("7. Plot TDR measurement")
            print("8. Configure plot settings")
            print("9. Configure email alerts")
            print("0. Exit\n")
            time.sleep(.5)

        main_menu_printed = True

        # Used to take user input.
        main_menu_input = input("Choose an operation: ")

        if main_menu_input == "1":

            # If VNA is not connected.
            if vna_session is None:
                # Get visa_address.
                visa_address = vna_address_menu()

                # Creates VNA session.
                vna_session = create_vna_session(visa_address)

                # Reprint Menu.
                main_menu_printed = False

        elif main_menu_input == "2":

            # If VNA is connected
            if vna_session is not None:

                # Print secondary menu to choose measurement type.
                print("\n1. Take coarse measurement (3GHz to 9GHz, 600KHz resolution: Estimated Time = 2 minutes)")
                print("2. Take fine measurement(3GHz to 9GHz, 20KHz resolution: Estimated Time = 40 minutes)")
                print("3. Cancel\n")

                # measurement_selection_success ends menu to choose measurement type.
                measurement_selection_success = False
                while not measurement_selection_success:

                    # Prompts user to choose measurement type.
                    measurement_type_input = input("Choose an operation: ")

                    if measurement_type_input == "1":

                        # Takes measurement on CalState 0.
                        # CalState_0 is the CalState with the coarse measurement range defined above.
                        take_s_parameters_measurements(vna_session, 0, 0)
                        measurement_selection_success = True

                    elif measurement_type_input == "2":

                        # Takes measurements on CalStates #1-#30
                        # These CalStates have ranges of 200MHz for 20Khz resolution.
                        take_s_parameters_measurements(vna_session, 1, 30)
                        send_email_alert(email_alerts_address_list)
                        measurement_selection_success = True

                    elif measurement_type_input == "3":
                        measurement_selection_success = True

                    else:
                        print("\nInvalid input. Please try again.\n")

                main_menu_printed = False
            else:
                print("\nVNA is not connected. Please choose \"Connect to VNA\" and then try again.\n")

        elif main_menu_input == "3":
            stitch_s_parameter_measurements()

            # Reprint Menu.
            main_menu_printed = False

        elif main_menu_input == "4":
            plot_s_parameter_measurements(False, plot_settings)

            # Reprint Menu.
            main_menu_printed = False

        elif main_menu_input == "5":
            plot_s_parameter_measurements(True, plot_settings)

            # Reprint Menu.
            main_menu_printed = False

        elif main_menu_input == "6":

            # If VNA is connected.
            if vna_session is not None:
                take_tdr_measurement(vna_session)

                # Reprint Menu.
                main_menu_printed = False

            # If VNA isn't connected.
            else:
                print("\nVNA is not connected. Please choose \"Connect to VNA\" and then try again.\n")

        elif main_menu_input == "7":
            plot_tdr_measurement(plot_settings)

            # Reprint Menu
            main_menu_printed = False

        elif main_menu_input == "8":
            plot_settings = configure_plot_settings(plot_settings)
            main_menu_printed = False

        elif main_menu_input == "9":
            email_alerts_address_list = configure_email_alerts(email_alerts_address_list)
            main_menu_printed = False

        elif main_menu_input == "0":
            print("\nNow exiting. Thank you for using SONA_Assistant!")

            # If VNA is connected.
            if vna_session is not None:
                vna_session.disconnect()

            # End main menu.
            return

        else:
            print("\nInvalid input. Please try again.\n")


# Menu used to obtain visa_address
def vna_address_menu():
    print("\nBeginning connection procedure...\n")

    # Default VISA Address values.
    # Change these to change default values.
    default_tcpip_address = '10.10.10.155'
    default_port_number = 5025

    # Values used to create VISA Address.
    tcpip_address = None
    port_number = None

    # Print default values
    print("(Default TCPIP address is: " + default_tcpip_address + ")")
    print("(Default Port is: " + str(default_port_number) + ")\n")
    time.sleep(.5)

    # address_menu_success is used to end VNA_address_menu() loop.
    address_menu_success = False

    while not address_menu_success:
        use_default_value_input = input("Use default connection details? (Y/N):")

        if use_default_value_input == "Y" or use_default_value_input == "y":

            # Set VISA Address values to default values.
            tcpip_address = default_tcpip_address
            port_number = default_port_number
            address_menu_success = True

        elif use_default_value_input == "N" or use_default_value_input == "n":

            # Gets VISA Address values from user.
            tcpip_address = input("\nPlease enter TCPIP address:")
            port_number = input("\nPlease enter port number:")
            address_menu_success = True

        else:
            print("\nInvalid input, please type (Y/N)")

    # Constructs visa_address.
    visa_address = "TCPIP::" + str(tcpip_address) + "::" + str(port_number) + "::SOCKET"
    print("\nCurrent TCPIP address: " + str(tcpip_address))
    print("Current port number: " + str(port_number))
    print("Current VISA address: " + str(visa_address) + "\n")

    return visa_address


# Connects to VNA.
def create_vna_session(visa_address):
    # Create vna_session from SONA
    vna_session = SONA()

    # Connects to VNA.
    # Returns whether connection was successful or not.
    connection_success = vna_session.connect_to_vna(visa_address)

    if connection_success:
        return vna_session

    else:
        return None


# Takes full 2 port S parameter measurements of VNA.
# Expects CalStates with format "CalState_#" on [INTERNAL]: of VNA.
# Creates a list of .s2p files in the format -> "filename_CalState#.s2p".
# These .s2p files are later stitched together into a single .ntwk file by stitch_S_parameter_measurements().
# !!!It is STRONGLY advised to choose a save file name with format -> "measurement_name_RF_#" for later!!!
def take_s_parameters_measurements(vna_session, calstate_start_number, calstate_end_number):
    # Prompts user for save file name.
    save_file_name = get_save_file_name()

    print("Now beginning S parameters measurements.\n")

    time.sleep(1)

    print("Now switching to NA mode...\n")

    time.sleep(1)

    # Switches VNA to NA mode.
    # No error is thrown is VNA is already in NA mode.
    vna_session.set_vna_to_network_analyzer_mode()

    print("Now preparing to begin taking measurements...\n")

    time.sleep(1)

    # For each calstate defined by "calstate_start number" and "calstate_end_number"...
    for calstate_number in range(calstate_start_number, calstate_end_number + 1):

        # Tell VNA to change to CalState #"calstate_number".
        vna_session.change_calstate(calstate_number)

        time.sleep(3)

        # Tell VNA to take measurements.
        vna_session.take_measurements()

        time.sleep(3)

        # CalState 0 is a special Calstate # reserved for coarse measurements.
        if calstate_number == 0:
            vna_session.save_s2p_data(str(save_file_name))

        # If high resolution measurements are being made, many .s2p files will be made.
        # The .s2p files will be saved and labeled by their calstate numbers.
        # The format is "save_file_name_CalState#.s2p"
        # They will be stitched together later by stitch_S_parameter_measurements().
        else:
            vna_session.save_s2p_data(str(save_file_name) + "_" + str(calstate_number))

        time.sleep(3)

    print("S parameters measurements complete!\n")


# Stitches .s2p files created by "take_S_parameter_measurements" into a .ntwk file.
# Saves .ntwk file in directory specified by user.
# Function expects ONLY .s2p files in a format of "filename_CalState#.s2p".
# Files are automatically created in this format by take_S_parameter_measurements().
def stitch_s_parameter_measurements():
    # Create and ready Tkinter object for GUI creation.
    root = Tk()
    root.withdraw()

    save_name = ""

    print("Please select directory that holds s2p files to be stitched.\n")

    time.sleep(1)

    # Prompts user to select directory using Tkinter.
    # Updates Tkinter object.
    directory = askdirectory()
    root.update()

    time.sleep(1)

    # Prompts user for a file name for new stitched file.
    # Ensures filename is valid (no ".").
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

    # Prompts user to select directory using Tkinter.
    # Updates and destroys Tkinter object.
    save_directory = askdirectory()
    root.update()

    time.sleep(1)

    root.destroy()

    # Creates a list of s2p files from directory.
    s2p_list = []
    for _ in os.listdir(directory):
        s2p_list.append(None)

    # Sorts all files in directory by CalState number.
    for s2p_file in os.listdir(directory):
        s2p_number = int(s2p_file[s2p_file.rfind("_") + 1:s2p_file.rfind(".")])
        s2p_list[s2p_number - 1] = rf.Network(directory + "/" + s2p_file)

    # Stitches s2p list to a .ntwk file and writes it in save_directory with name "save_name".
    stitch_s2p_list(s2p_list)[0].write(save_directory + "/" + save_name)

    print("File successfully saved as \"" + save_directory + "/" + save_name + "\"!")


# Stitches a sorted list of .s2p files using skrf.
# This is a recursive function.
def stitch_s2p_list(s2p_list):
    # A temporary list to hold stitched files.
    stitched_s2p_list = []

    # Recursive end condition.
    # Once list is one element long, stitching is complete.
    if len(s2p_list) == 1:
        return s2p_list

    # For every element in s2p_list...
    for i in range(0, len(s2p_list)):

        # For every other element in s2p_list...
        if i % 2 == 1:
            # Take the prior element.
            s2p_1 = s2p_list[i - 1]

            # Take the current element.
            s2p_2 = s2p_list[i]

            # Stitch the two elements together.
            stitched_s2p = rf.stitch(s2p_1, s2p_2)

            # Append the stitched .s2p file to temporary list.
            stitched_s2p_list.append(stitched_s2p)

        # If the length of s2p_list is odd and the current element is the last in the list....
        if len(s2p_list) % 2 != 0 and i == len(s2p_list) - 1:
            # Append the element to the temporary list.
            stitched_s2p_list.append(s2p_list[i])

    # Recursively stitch temporary list until all elements are stitched together.
    return stitch_s2p_list(stitched_s2p_list)


# Plots S21 trace of selected .s2p file.
# Function expects EITHER .s2p files or .ntwk files.
# !!!Function expects file format of "filename_RF_#", THIS IS UP TO THE USER!!!
def plot_s_parameter_measurements(multiple_plots, plot_settings):
    # Create and ready Tkinter object for GUI creation.
    # Force GUI to front.
    root = Tk()
    root.lift()
    root.wm_attributes('-topmost', 1)
    root.withdraw()

    # List plot settings for easy access
    auto_scale_on = plot_settings[0]
    plot_dimensions = plot_settings[1]
    plot_x_axis_range = plot_settings[2]
    plot_y_axis_range = plot_settings[3]

    # List of .s2p measurements to plot.
    measurements_list = []

    # If there are multiple measurements to plot.
    if multiple_plots:
        print("\nPlease select directory that contains S parameter measurements to plot.\n")

        time.sleep(1)

        # Prompts user to select directory holding .s2p measurements to plot.
        measurement_directory = askdirectory()

        # Add all measurements to list.
        for measurement_file in os.listdir(measurement_directory):
            measurements_list.append(measurement_directory + "/" + measurement_file)

        # Sort the list by RF number.
        measurements_list = sort_measurements_list(measurements_list)

    # If there is only one measruement to plot.
    else:
        print("\nPlease select S parameter measurement to plot.\n")

        time.sleep(1)

        # Prompts user to select .s2p measurement to plot.
        measurement_file = askopenfilename()

        # Add measurement to list.
        measurements_list.append(measurement_file)

    # Update Tkinter object.
    root.update()

    time.sleep(1)

    print("Please select save location for plots.\n")

    # Prompts user to select directory to save plot(s).
    save_directory = askdirectory()

    time.sleep(1)

    print("Creating plots...\n")

    # Create plot for each .s2p measurement in list.
    for measurement_file in measurements_list:
        plt.figure(figsize = plot_dimensions)

        # Plot title is "filename" taken from "directory/filename.s2p"
        plot_title = measurement_file[measurement_file.rfind("/") + 1:measurement_file.rfind(".")]
        plt.title(plot_title)

        print("Creating plot: \"" + plot_title + "\"...")

        # Uses skrf to plot .s2p measurements.
        # skrf automatically sets axis titles and legend.
        s_parameter_network = rf.Network(measurement_file)

        # Plot only S21
        s_parameter_network.plot_s_db(1, 0)

        # Plot bounds (Change at will)
        plt.xlim(plot_x_axis_range)
        plt.ylim(plot_y_axis_range)

        # If auto-scaling is turned on, auto-scale the plot.
        # This overrides the previously set axis ranges
        if auto_scale_on:
            plt.autoscale(enable = True)

        plt.grid()

        # Saves file in save_directory.
        plt.savefig(save_directory + "/" + plot_title)

        time.sleep(.5)

    # If there are multiple plots, it is convenient to create a plot to compare.
    if multiple_plots:
        print("Creating plot: \"Measurement Comparison\"...\n")
        plt.figure(figsize = plot_dimensions)
        plot_title = "Measurement Comparisons"
        plt.title(plot_title)
        plt.xlim(plot_x_axis_range)
        plt.ylim(plot_y_axis_range)

        # If auto-scaling is turned on, auto-scale the plot.
        # This overrides the previously set axis ranges
        if auto_scale_on:
            plt.autoscale(enable = True)

        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude (dB)")
        plot_legend = []

        # For each measurement, add the measurement to the comparison plot.
        for measurement_file in measurements_list:
            # Uses skrf to plot .s2p/.ntwk files.
            s_parameter_network = rf.Network(measurement_file)
            plt.plot(s_parameter_network.frequency.f, s_parameter_network.s_db[:, 1, 0])

            # Labels plots by RF #.
            rf_number = measurement_file[measurement_file.rfind("_") + 1:measurement_file.rfind(".")]
            plot_legend.append("RF " + rf_number)

        plt.legend(plot_legend)
        plt.grid()

        plt.savefig(save_directory + "/" + plot_title)
        time.sleep(.5)

    # Destroy Tkinter object and close all plots.
    root.destroy()
    plt.close('all')

    if multiple_plots:
        print("Plots finished!")

    else:
        print("\nPlot finished!")


# Sort measurements in list by RF #
# !!!Function expects file format of "filename_RF_#", THIS IS UP TO THE USER!!!
def sort_measurements_list(measurements_list):
    # List of RF #'s
    rf_number_list = []

    # For each measurement in list
    for measurement_file in measurements_list:
        # Grab the RF # from file and add it to RF # list.
        # Measurement list and RF # list will be in same order.
        rf_number = measurement_file[measurement_file.rfind("_") + 1:measurement_file.rfind(".")]
        rf_number_list.append(int(rf_number))

    # Sort RF # list and measurement list in parallel.
    # For each element in rf_number_list
    for i in range(0, len(rf_number_list)):

        # Set the smallest rf number and its index to current element
        smallest_rf_number = rf_number_list[i]
        smallest_rf_number_index = i

        # For all elements after current index (i)
        for j in range(i, len(rf_number_list)):

            # If the RF # at current (j) index is smaller than the smallest RF #...
            # Set new smallest RF # and its index to RF # at j'th index and j respectively.
            if rf_number_list[j] < smallest_rf_number:
                smallest_rf_number = rf_number_list[j]
                smallest_rf_number_index = j

        # Swap position of elements at current (i) index and smallest RF # index.
        temp_measurement = measurements_list[i]
        measurements_list[i] = measurements_list[smallest_rf_number_index]
        measurements_list[smallest_rf_number_index] = temp_measurement

        temp_rf_number = rf_number_list[i]
        rf_number_list[i] = rf_number_list[smallest_rf_number_index]
        rf_number_list[smallest_rf_number_index] = temp_rf_number

    # Return sorted list.
    return measurements_list


# Take TDR measurement
# Uses a special CalState that uses full range of VNA.
# TDR CalState is designated to CalState_-1
# Expects Calstate in format -> "CalState_-1" on [INTERNAL]: of VNA.
def take_tdr_measurement(vna_session):
    # Prompts user for name of save file.
    save_file_name = get_save_file_name()

    print("Now beginning TDR measurements.\n")
    time.sleep(1)

    print("Now switching to NA mode...\n")

    time.sleep(1)

    # Set VNA to NA mode to take measurement.
    # Causes no error if VNA is already in NA mode.
    vna_session.set_vna_to_network_analyzer_mode()

    print("Now perparing to begin taking measurements...\n")

    # Change VNA's CalState to TDR CalState ("CalState_-1").
    vna_session.change_calstate(-1)

    time.sleep(3)

    # Tells VNA to take measurements.
    vna_session.take_measurements()

    time.sleep(3)

    # Tells VNA to save file to USBDISK.
    vna_session.save_s2p_data(str(save_file_name))

    time.sleep(3)

    print("TDR measurement complete! Returning to main menu.")


# Plots TDR measurement
# Function expects either a .s2p or .ntwk file type.
def plot_tdr_measurement(plot_settings):
    # Creates and readies a Tkinter object for GUI.
    root = Tk()
    root.withdraw()

    plt.ion()

    # Set TDR constants.
    z_0 = 50
    c = 299792458
    vf = 0.695
    vs = c * vf

    print("Select non-biased s2p file")

    # Prompts user to select non-biased TDR measurement file.
    # Updates Tkinter object.
    no_amp_file = askopenfilename()
    root.update()

    time.sleep(1)

    print("Select biased s2p file")

    # Prompts user to select biased TDR measurement file.
    # Updates Tkinter object.
    with_amp_file = askopenfilename()
    root.update()

    time.sleep(1)

    save_file_name = get_save_file_name()

    print("Please select save location for plots.\n")

    # Prompts user to select directory to save plot(s).
    save_directory = askdirectory()
    # Destroy Tkinter object.
    root.destroy()

    no_amp_network = rf.Network(no_amp_file)
    with_amp_network = rf.Network(with_amp_file)

    no_amp_t = no_amp_network.frequency.t
    with_amp_t = with_amp_network.frequency.t

    no_amp_d = no_amp_t * vs / 2
    with_amp_d = with_amp_t * vs / 2

    no_amp_gamma1 = np.real(no_amp_network.s11.s_time[:, 0, 0])
    with_amp_gamma1 = np.real(with_amp_network.s11.s_time[:, 0, 0])
    no_amp_gamma2 = np.real(no_amp_network.s22.s_time[:, 0, 0])
    with_amp_gamma2 = np.real(with_amp_network.s22.s_time[:, 0, 0])

    no_amp_z_1 = z_0 * (1 + no_amp_gamma1) / (1 - no_amp_gamma1)
    with_amp_z_1 = z_0 * (1 + with_amp_gamma1) / (1 - with_amp_gamma1)
    no_amp_z_2 = z_0 * (1 + no_amp_gamma2) / (1 - no_amp_gamma2)
    with_amp_z_2 = z_0 * (1 + with_amp_gamma2) / (1 - with_amp_gamma2)

    plt.figure()
    plt.plot(no_amp_d, no_amp_z_1, label='No Amplifier Biased')
    plt.plot(with_amp_d, with_amp_z_1, label='With Amplifier Biased')
    plt.xlim([-0.25, 3.75 / 2])
    plt.xlabel('Distance [m]', fontsize=16)
    plt.ylabel('Impedance [Ohm]', fontsize=16)
    plt.title('RF Line 2, Port 1/RF In TDR', fontsize=16)
    plt.legend()

    plt.savefig(save_directory + "/" + save_file_name + "Port_1_RF_IN")

    plt.figure()
    plt.plot(no_amp_d, no_amp_z_2, label='No Amplifier Biased')
    plt.plot(with_amp_d, with_amp_z_2, label='With Amplifier Biased')
    plt.xlim([-0.25, 3.75 / 2])
    plt.xlabel('Distance [m]', fontsize=16)
    plt.ylabel('Impedance [Ohm]', fontsize=16)
    plt.title('RF Line 2, Port 2/RF Out TDR', fontsize=16)
    plt.legend()

    plt.savefig(save_directory + "/" + save_file_name + "Port_2_RF_OUT")


def configure_plot_settings(plot_settings):
    configure_plot_menu_success = False

    auto_scale_on = plot_settings[0]
    plot_dimensions = plot_settings[1]
    x_axis_range = plot_settings[2]
    y_axis_range = plot_settings[3]

    while not configure_plot_menu_success:

        print("\n1. Show current plot settings")
        if not auto_scale_on:
            print("2. Turn on plot auto-scaling")
        else:
            print("2. Turn off plot auto-scaling")
        print("3. Configure plot dimensions")
        print("4. Configure plot range")
        print("0. Exit\n")

        configure_plot_menu_response = input("Choose an operation: ")

        if configure_plot_menu_response == "1":
            print("\nPlot auto-scale on? -> " + str(auto_scale_on))
            print("Plot dimensions -> " + str(plot_dimensions))
            print("Plot x-axis range -> " + str(x_axis_range))
            print("Plot y-axis range -> " + str(y_axis_range))

        elif configure_plot_menu_response == "2":
            auto_scale_on = not auto_scale_on

            if auto_scale_on:
                print("\nPlot auto-scaling turned on.")

            else:
                print("\nPlot auto-scaling turned off.")

        elif configure_plot_menu_response == "3":
            plot_dimensions = configure_plot_dimensions(plot_dimensions)
            print("\nCurrent plot dimensions set to: " + str(plot_dimensions))

        elif configure_plot_menu_response == "4":
            if auto_scale_on:
                print("\nPlease disable plot auto-scaling to configure plot range.")

            else:
                axis_menu_success = False

                while not axis_menu_success:
                    print("\n1. x-axis")
                    print("2. y-axis")
                    print("0. Cancel\n")

                    axis_menu_response = input("Choose an axis: ")

                    if axis_menu_response == "1":
                        x_axis_range = configure_axis_range(x_axis_range)
                        print("\nPlot x-axis range set to: " + str(x_axis_range))

                    elif axis_menu_response == "2":
                        y_axis_range = configure_axis_range(y_axis_range)
                        print("\nPlot y-axis range set to: " + str(y_axis_range))

                    elif axis_menu_response == "0":
                        axis_menu_success = True

                    else:
                        print("\nInvalid response. Please try again.")



        elif configure_plot_menu_response == "0":
            new_plot_settings = [auto_scale_on, plot_dimensions, x_axis_range, y_axis_range]
            print(new_plot_settings)
            return new_plot_settings

        else:
            print("\nInvalid response. Please try again.")


def configure_plot_dimensions(old_plot_dimensions):
    configure_plot_size_success = False

    while not configure_plot_size_success:

        new_plot_x_dimension = input("\nEnter x-dimension for plot: ")
        new_plot_y_dimension = input("\nEnter y-dimension for plot: ")

        try:
            new_plot_x_dimension = int(float(new_plot_x_dimension))
            new_plot_y_dimension = int(float(new_plot_y_dimension))

            if new_plot_x_dimension > 0 and new_plot_y_dimension > 0:
                new_plot_dimensions = (new_plot_x_dimension, new_plot_y_dimension)

                return new_plot_dimensions

            else:
                print("\nInvalid dimensions. Dimensions must be greater than 0.")
                return old_plot_dimensions

        except ValueError:
            print("\nInvalid response. Please enter a number.")
            return old_plot_dimensions


def configure_axis_range(old_axis_range):
    configure_axis_range_success = False

    while not configure_axis_range_success:
        new_axis_minimum = input("\nEnter axis minimum: ")
        new_axis_maximum = input("\nEnter axis maximum: ")

        try:
            new_axis_minimum = int(float(new_axis_minimum))
            new_axis_maximum = int(float(new_axis_maximum))

            if new_axis_minimum < new_axis_maximum:
                new_axis_range = (new_axis_minimum, new_axis_maximum)
                return new_axis_range

            else:
                print("\nInvalid axis range. Axis minimum must be less than axis maximum.")
                return old_axis_range

        except ValueError:
            print(" \nInvalid response. Please only enter numbers.")
            return old_axis_range


def configure_email_alerts(email_alerts_address_list):
    configure_email_alerts_menu_success = False
    print("\nEmail alerts are sent when high resolution S parameter measurements finish.")

    while not configure_email_alerts_menu_success:

        if len(email_alerts_address_list) != 0:
            print("\n-> Email alerts configured to send alerts to: " + ", ".join(email_alerts_address_list) + ".")

        else:
            print("\n-> There are currently no recipients for email alerts.")

        print("\n1. Add email address")
        print("2. Add phone number (text message)")
        print("3. Remove recipient")
        print("4. Send test email alert")
        print("0. Exit\n")

        configure_email_alerts_menu_response = input("Choose an operation: ")

        if configure_email_alerts_menu_response == "1":
            email_alerts_address_list = add_email_address(email_alerts_address_list)

        elif configure_email_alerts_menu_response == "2":
            email_alerts_address_list = add_phone_number(email_alerts_address_list)

        elif configure_email_alerts_menu_response == "3":
            email_alerts_address_list = remove_recipient(email_alerts_address_list)

        elif configure_email_alerts_menu_response == "4":
            if len(email_alerts_address_list) == 0:
                print("\nPlease enter at least one email alert recipient.")
            else:
                print("")
                send_email_alert(email_alerts_address_list)

        elif configure_email_alerts_menu_response == "0":
            return email_alerts_address_list

        else:
            print("\nInvalid response. Please try again.")


def add_email_address(email_alerts_address_list):
    email_address = input("\nEnter email address: ")
    email_alerts_address_list.append(email_address)

    return email_alerts_address_list


def add_phone_number(email_alerts_address_list):
    at_t_suffix = "@txt.att.net"
    t_mobile_suffix = "@tmomail.net"
    virgin_mobile_suffix = "@vmobl.com"
    sprint_suffix = "@messaging.sprintpcs.com"
    verizon_suffix = "@vtext.com"

    phone_number = ""
    phone_number_suffix = None

    print("\n1. AT&T")
    print("2. T Mobile")
    print("3. Virgin Mobile")
    print("4. Sprint")
    print("5. Verizon")
    print("0. Cancel\n")

    carrier_menu_success = False

    while not carrier_menu_success:
        carrier_menu_response = input("Choose phone carrier: ")

        if carrier_menu_response == "1":
            phone_number_suffix = at_t_suffix
            carrier_menu_success = True

        elif carrier_menu_response == "2":
            phone_number_suffix = t_mobile_suffix
            carrier_menu_success = True

        elif carrier_menu_response == "3":
            phone_number_suffix = virgin_mobile_suffix
            carrier_menu_success = True

        elif carrier_menu_response == "4":
            phone_number_suffix = sprint_suffix
            carrier_menu_success = True

        elif carrier_menu_response == "5":
            phone_number_suffix = verizon_suffix
            carrier_menu_success = True

        elif carrier_menu_response == "0":
            return email_alerts_address_list

        else:
            print("\nInvalid response. Please try again.")

    phone_number_success = False

    while not phone_number_success:
        phone_number = input("\nEnter phone number (No spaces or -): ")

        if phone_number.find(" ") != -1 or phone_number.find("-") != -1:
            print("\nInvalid response. Please try again.\n")

        else:
            phone_number_success = True

    sms_address = phone_number + phone_number_suffix
    email_alerts_address_list.append(sms_address)

    return email_alerts_address_list


def remove_recipient(email_alerts_address_list):
    remove_recipient_success = False

    while not remove_recipient_success:
        if len(email_alerts_address_list) == 0:
            print("\nThere are no recipients to remove.")
            return email_alerts_address_list

        for i in range(0, len(email_alerts_address_list)):
            if i == 0:
                print("")
            print(str(i + 1) + ". " + email_alerts_address_list[i])

        print("0. Cancel\n")

        remove_recipient_menu_response = input("Choose a recipient to remove: ")

        try:
            remove_recipient_menu_response = int(remove_recipient_menu_response)

            if remove_recipient_menu_response == 0:
                return email_alerts_address_list

            else:
                if 0 < remove_recipient_menu_response <= len(email_alerts_address_list):
                    print("\nRecipient \"" + email_alerts_address_list.pop(remove_recipient_menu_response - 1)
                          + "\" has been removed from recipient list.")
                else:
                    print("\nInvalid response. Please try again.")

        except ValueError:
            print("\nInvalid response. Please try again.")


def send_email_alert(email_alerts_address_list):
    if len(email_alerts_address_list) == 0:
        return

    print("Sending email alert...\n")

    server = smtplib.SMTP('smtp.gmail.com', 25)
    server.connect('smtp.gmail.com', 25)
    server.starttls()

    username = 'sona.alerts@gmail.com'
    password = 'B-Modes2.73'

    server.login(username, password)

    sender_name = "SONA Alerts"
    to_address_list = email_alerts_address_list
    cc_address_list = []

    subject = "This is a test!"
    message = "This is a test!"

    header = 'From: %s\n' % sender_name
    header += 'To: %s\n' % ','.join(to_address_list)
    header += 'Cc: %s\n' % ','.join(cc_address_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server.sendmail(sender_name, to_address_list, message)

    print("Email alert sent!")


# Prompts user to enter name for save file.
def get_save_file_name():
    save_file_name = input("Please enter name for save file:")
    return save_file_name


main()

# Thank you for using SONA_Assitant!
