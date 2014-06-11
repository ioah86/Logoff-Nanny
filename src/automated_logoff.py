"""
This program serves the following purpose:
The user starts his/her session on the computer, and he/she has
exactly half an hour of time on it on weekdays, and an hour on weekends.
As one assumes correctly, this applies to kids who have a limited computer
time.

It has the following functionalities:
  - Logging off the user after a certain amount of time for each day
    by distinguishing weekdays from weekends.
  - Displaying the remaining time inside the notification area

The user can change the timings in the respective files that are generated.

The program has only been tested on an Ubuntu 12.04 system.
@author: Albert Heinle
@contact: albert.heinle@googlemail.com
"""

##################################################
# IMPORTS
##################################################
import os
import datetime
from time import sleep
import gobject
import gtk
import appindicator
import glib
from thread import start_new_thread

##################################################
# Constants of the program
##################################################

#This variable sets the interval how fast (in minutes) the remaining
#Time is being refreshed. It should be an integer number
REFRESH_INTERVAL = 1

#This variable sets the time that the user has on weekdays at the
#computer
TIME_WEEKDAYS = 30

#This variable sets the time that the user has on the weekend at the
#computer (in minutes, type should be integer)
TIME_WEEKENDS = 30

#This variable is the name of the folder where our time-files are
#saved
FOLDER_NAME_TIMEFILES = ".timeSpec"

#This variable is the path, where we would expect to find the file.
PATH_FOLDER_TIMEFILES = os.path.expanduser("~")


##################################################
# File Handling
##################################################

def createFileForTheDay():
    """
    This function creates, if not yet existent, the file of the day
    where we keep track how much time is left on the computer.
    If the file already exists, this function does nothing.
    If the file does not exist, then this function creates it and
    sets the respective time limit for the day in it.
    """
    fileNameOfTheDay = datetime.datetime.now().strftime("%Y_%m_%d.txt")
    if not os.path.exists(os.path.join(PATH_FOLDER_TIMEFILES,\
                                       FOLDER_NAME_TIMEFILES)):
        """
        In this case, this program is run for the first time, as the Folder
        for the timing files does not exist yet.
        """
        os.makedirs(os.path.join(PATH_FOLDER_TIMEFILES,FOLDER_NAME_TIMEFILES))
    if not os.path.exists(os.path.join(PATH_FOLDER_TIMEFILES,\
                                       FOLDER_NAME_TIMEFILES,fileNameOfTheDay)):
        f = open(os.path.join(PATH_FOLDER_TIMEFILES,\
                              FOLDER_NAME_TIMEFILES,fileNameOfTheDay),'w')
        day = datetime.datetime.now().strftime("%A")
        if (day == "Saturday" or day == "Sunday"):
            f.write(str(TIME_WEEKENDS))
        else:
            f.write(str(TIME_WEEKDAYS))
        f.close()

def decreaseOneMinuteFromTime():
    """
    This function will open the file, where the remaining time for the day is
    saved, extract the value in it, decrease it by one and write the updated
    value back to the file.
    The return statement is the remaining time stored in the file, i.e. the
    updated value.
    GENERAL ASSUMPTIONS:
     - The file with the number for the day is already created. Never use this
       function without.
    """
    fileNameOfTheDay = datetime.datetime.now().strftime("%Y_%m_%d.txt")
    timeRemaining = getTimeRemaining()
    if timeRemaining <= 0:
        #In this case, the time was already up
        return 0
    timeRemaining = timeRemaining - 1
    f = open(os.path.join(PATH_FOLDER_TIMEFILES,\
                              FOLDER_NAME_TIMEFILES,fileNameOfTheDay),'w')
    f.write(str(timeRemaining))
    f.close()
    return timeRemaining

def getTimeRemaining():
    """
    Simply opens the file, where the remaining time for the day is storend,
    and returns the value written in it.
    GENERAL ASSUMPTIONS:
     - The file with the number for the day is already created. Never use this
       function without.
    """
    fileNameOfTheDay = datetime.datetime.now().strftime("%Y_%m_%d.txt")
    f = open(os.path.join(PATH_FOLDER_TIMEFILES,\
                              FOLDER_NAME_TIMEFILES,fileNameOfTheDay),'r')
    timeRemaining = int(f.readline().strip())
    f.close()
    return timeRemaining

##################################################
# GUI/Appindicator stuff
##################################################

def showRemainingTime(item):
    md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_CLOSE, "Remaining Time: "+str(getTimeRemaining()))
    md.run()
    md.destroy()

def startAppIndicator():
    ind = appindicator.Indicator ("example-simple-client",
                              "",
                              appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_label("TIME")
    ind.set_status (appindicator.STATUS_ACTIVE)
    menu = gtk.Menu()
    menu_items = gtk.MenuItem("Show Time Remaining")
    menu.append(menu_items)
    menu_items.show()
    ind.set_menu(menu)
    menu_items.connect('activate', showRemainingTime)
    gtk.main()


##################################################
# The main program stuff
##################################################

if __name__ == '__main__':
    """
    The main program.
    If not yet existent, we create the file for the day.
    Every minute, we will decrease the time remaining,
    until we reach zero. If we do that, we will terminate
    our program.
    """
    createFileForTheDay()
    #start_new_thread(startAppIndicator,())
    while getTimeRemaining()>0:
        sleep(REFRESH_INTERVAL*60)
        decreaseOneMinuteFromTime()
    os.system("gnome-session-quit --logout --no-prompt")
