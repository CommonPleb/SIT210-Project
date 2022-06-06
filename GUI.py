from tabnanny import check
import tkinter
from tkinter import messagebox
from socket import *

# Specifies the DNS server IP and port numbers
ServerIP = "127.0.0.1"
ServerPort = 9999

# Creates a UDP socket for the client to use
ClientSocket = socket(AF_INET, SOCK_DGRAM)

# Creates initial variables
HOURLY = 1
DAILY = 2
SELECTED = 1

def SwapActive():
    if changed.get() == HOURLY:
        dailyTextBox["state"], hourlyTextBox["state"] = "disable", "normal"
        dailyTextBox["bg"], hourlyTextBox["bg"] = "grey", "white"
        dailyLabel1["fg"], dailyLabel2["fg"], hourlyLabel1["fg"], hourlyLabel2["fg"] = "grey", "grey", "black", "black"
    else:
        dailyTextBox["state"], hourlyTextBox["state"] = "normal", "disable"
        dailyTextBox["bg"], hourlyTextBox["bg"] = "white", "grey"
        dailyLabel1["fg"], dailyLabel2["fg"], hourlyLabel1["fg"], hourlyLabel2["fg"] = "black", "black", "grey", "grey"

def nightSwitch():
    if night.get() == 0:
        nightStartTextBox["state"], nightEndTextBox["state"] = "disable", "disable"
        nightStartTextBox["bg"], nightEndTextBox["bg"] = "grey", "grey"
        nightStartLabel["fg"], nightEndLabel["fg"] = "grey", "grey"
    elif night.get() == SELECTED:
        nightStartTextBox["state"], nightEndTextBox["state"] = "normal", "normal"
        nightStartTextBox["bg"], nightEndTextBox["bg"] = "white", "white"
        nightStartLabel["fg"], nightEndLabel["fg"] = "black", "black"

def ShowError():
    messagebox.showerror("Error", "Invalid Input")


def CheckAndSend(input):
    try:
        if 0 <= int(input) < 24:
            toSend = "{};{};{};{}".format(changed.get(), input, weightThresholdTextBox.get("1.0", "end-1c"), night.get())
            ClientSocket.sendto(toSend.encode(), (ServerIP, ServerPort))
        else:
            ShowError()
    except:
        ShowError()


def CheckAndSendNight(input1, input2, input3):
    try:
        if 0 <= int(input1) < 24 and 0 <= int(input2) < 24 and 0 <= int(input3)< 24:
            toSend = "{};{};{};{};{};{}".format(changed.get(), input1, weightThresholdTextBox.get("1.0", "end-1c"), night.get(), str(input2), str(input3))
            ClientSocket.sendto(toSend.encode(), (ServerIP, ServerPort))
        else:
            ShowError()
    except:
        ShowError()


def sendToServer():
    try:
        if changed.get() == HOURLY:
            if night.get() == SELECTED:
                CheckAndSendNight(hourlyTextBox.get("1.0", "end-1c"), nightStartTextBox.get("1.0", "end-1c"), nightEndTextBox.get("1.0", "end-1c"))
            else:
                CheckAndSend(hourlyTextBox.get("1.0", "end-1c"))
        else:
            if night.get() == SELECTED:
                CheckAndSendNight(dailyTextBox.get("1.0", "end-1c"), nightStartTextBox.get("1.0", "end-1c"), nightEndTextBox.get("1.0", "end-1c"))
            else:
                CheckAndSend(dailyTextBox.get("1.0", "end-1c"))
    except:
        ShowError()


def dailyToggle():
    SwapActive()


def hourlyToggle():
    SwapActive()

window = tkinter.Tk()
window.title("RGB LED Switch")
window["pady"]=8
window["padx"]=5

# Creation of the GUI elements
changed = tkinter.IntVar()
night = tkinter.IntVar()

dailyRadioButton = tkinter.Radiobutton(window, text="Daily", command=dailyToggle, height=1, width=20, variable=changed, value=DAILY)
dailyTextBox = tkinter.Text(window, height=1, width=20)
dailyLabel1 = tkinter.Label(window, height=1, width=25, text="What hour of the day do")
dailyLabel2 = tkinter.Label(window, height=1, width=25, text="you want to feed your pet?")
hourlyRadioButton = tkinter.Radiobutton(window, text="Hourly", command=hourlyToggle, height=1, width=20, variable=changed, value=HOURLY)
hourlyTextBox = tkinter.Text(window, height=1, width=20, state="disable", bg="grey")
hourlyLabel1 = tkinter.Label(window, height=1, width=25, text="After how many hours do", fg="grey")
hourlyLabel2 = tkinter.Label(window, height=1, width=25, text="you want to feed your pet?", fg="grey")
weightThresholdTextBox = tkinter.Text(window, height=1, width=20)
weightLabel1 = tkinter.Label(window, height=1, width=20, text="How much food would")
weightLabel2 = tkinter.Label(window, height=1, width=20, text="you like in the bowl?")
nightCheckBox = tkinter.Checkbutton(window, height=1, width=20, text="Enable night mode", command=nightSwitch, variable=night)
nightStartLabel = tkinter.Label(window, height=1, width=20, text="Starting hour for night time:")
nightStartTextBox = tkinter.Text(window, height=1, width=20)
nightEndLabel = tkinter.Label(window, height=1, width=20, text="Ending hour for night time:")
nightEndTextBox = tkinter.Text(window, height=1, width=20)
submitButton = tkinter.Button(window, text="Submit", command=sendToServer, height=1, width=8)

# Spacing for the GUI elements
dailyRadioButton.select()
nightCheckBox.select()
hourlyItems = [hourlyRadioButton, hourlyLabel1, hourlyLabel2, hourlyTextBox]
dailyItems = [dailyRadioButton, dailyLabel1, dailyLabel2, dailyTextBox]
centreItems = [weightLabel1, weightLabel2, weightThresholdTextBox, nightCheckBox]
leftItems = [nightStartLabel, nightStartTextBox]
rightItems = [nightEndLabel, nightEndTextBox]

i = 0
for item in hourlyItems:
    item.grid(row=i, column=3)
    i += 1

i = 0
for item in dailyItems:
    item.grid(row=i, column=1)
    i += 1

for item in centreItems:
    item.grid(row=i, column=2)
    i += 1

j = i
for item in leftItems:
    item.grid(row=i, column=1)
    i += 1

i = j
for item in rightItems:
    item.grid(row=i, column=3)
    i += 1

submitButton.grid(row=i, column=2)

window.protocol("WM_DELETE_WINDOW")

window.mainloop()
ClientSocket.close()

# References
# xxmbabanexx, 2013. How to get the input from the Tkinter Text Widget?. [online] Stack Overflow. Available at: <https://stackoverflow.com/questions/14824163/how-to-get-the-input-from-the-tkinter-text-widget> [Accessed 30 May 2022].
# Kumar, B., 2020. Python Tkinter Radiobutton - How To Use. [online] Python Guides. Available at: <https://pythonguides.com/python-tkinter-radiobutton/> [Accessed 30 May 2022].
