#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Test
#
# Created:     17/05/2018
# Copyright:   (c) Test 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import telnetlib
import time
import re
from baselib.loglib.log_lib import *
def apc_ctrl(outlet_num_list = [1], outlet_st_list=[1]):
    '''outlet_st: 1 ~ 8'''
    # check input
    change = []
    for outlet_num in outlet_num_list:
        if outlet_num >8 or outlet_num <1 :
            logerror("outlet_num must be 1 ~ 8 !!")
            return
    if len(outlet_st_list) != len(outlet_num_list):
        logwarn("err !! outlet_num_list is not eq outlet_st_list")

    # telnet
    tn = telnetlib.Telnet("192.168.1.88")
    #tn.read_until("User Name :")
    tn.write("apc\n\r")
    tn.write("apc\n\r")
    # OFF all of the outlet
    tn.write("1\n\r")
    tn.write("2\n\r")
    time.sleep(1)
    outlet_list = tn.read_very_eager() # flush
    tn.write("1\n\r") # get outlet list
    time.sleep(0.5)
    outlet_list = tn.read_very_eager()
    if re.search("Outlet Control/Configuration", outlet_list) == None:
        logerror("cant find Outlet \'Control/Configuration\'")
        return
    else:
        outlet_list = outlet_list.split("\n")
        outlet_list = outlet_list[4:12]
        for index,outlet in enumerate(outlet_list):
##            print outlet_list[index]
##            print outlet.split(" ")
            if re.search("ON",outlet.split(" ")[-1]):
                outlet_list[index] = 1
            elif re.search("OFF",outlet.split(" ")[-1]):
                outlet_list[index] = 0
            else:
                logerror("outlet state err!!")
                return
##            print outlet_list[index]
    onoff_st = 0
    for index,outlet_num in enumerate(outlet_num_list):
##        print outlet_num
##        print outlet_list
##        print outlet_st_list
        if outlet_list[outlet_num-1] != outlet_st_list[index]:
            onoff_st = 1
            tn.write("%d\n\r"%(outlet_num))
            tn.write("1\n\r")
            if outlet_st_list[index] == 0:
                tn.write("2\n\r")
                loginfo("outlet %d is OFF !"%(outlet_num))
            else:
                tn.write("1\n\r")
                loginfo("outlet %d is ON !"%(outlet_num))
            tn.write("yes\n\r")
            tn.write("\n\r")
            tn.write("\033\n\r")
            time.sleep(1)
            outlet_list_ck = tn.read_very_eager() # flush
            tn.write("\033\n\r")
            time.sleep(0.5)
            outlet_list_ck = tn.read_very_eager()
            change.append(True)
        else:
            if outlet_st_list[index] == 0:
                logdebug("outlet %d is already OFF !"%(outlet_num))
            else:
                logdebug("outlet %d is already ON !"%(outlet_num))
            change.append(False)
    if onoff_st == 1:
##        print outlet_list_ck
        # check
        if re.search("Outlet Control/Configuration", outlet_list_ck) == None:
            logerror("cant find Outlet \'Control/Configuration\'")
            return
        else:
            outlet_list_ck = outlet_list_ck.split("\n")
            outlet_list_ck = outlet_list_ck[4:12]
            for index,outlet in enumerate(outlet_list_ck):
##                print outlet_list_ck[index]
##                print outlet.split(" ")

                if re.search("ON",outlet.split(" ")[-1]):
                    outlet_list_ck[index] = 1
                elif re.search("OFF",outlet.split(" ")[-1]):
                    outlet_list_ck[index] = 0
                else:
                    logerror("outlet state err!!")
                    return
##                print outlet_list_ck[index]

        for index,outlet_num in enumerate(outlet_num_list):
            if outlet_list_ck[outlet_num-1] != outlet_st_list[index]:
                logerror("check err!!")
                return

    tn.write("\033\n\r")
    tn.write("\033\n\r")
    tn.write("\033\n\r")
    tn.write("4\n\r")
    return change
    # ON
#    for index,outlet in enumerate(outlet_list):
#        outlet_list[index] = outlet_list[index].split(" ")[3]
#        if re.search("ON", outlet_list[index]):
#            outlet_list[index] = 1
#        elif re.search("OFF", outlet_list[index]):
#            outlet_list[index] = 0
#        else:
#            print "read outlet state err "
#            return
#        print outlet_list[index]
#
#    if outlet_list[outlet_num-1]  != outlet_st:
#        tn.write("%d\n\r"%(outlet_st))
#        tn.write("1\n\r")
#        if outlet_st == 1:
#            tn.write("1\n\r") # ON
#        else:
#            tn.write("2\n\r") # OFF
#
#        tn.write("yesn\r")
#        tn.write("\n\r")
