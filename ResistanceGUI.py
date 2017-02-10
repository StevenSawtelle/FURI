from tkinter import Tk, Label, Button, Entry, N, E, S, W, Frame, StringVar
import visa
import csv
import sys

supply = None
headerRowCreated = False

class MeasurementsModel:
    #initialize model
    def __init__(self, vc):
        #vc is controller for communication with ResistanceViewController
        self.vc = vc
        #listOfMeasurements will hold list of lists, with each list
        #   being a resistance measurement and its data
        self.listOfMeasurements = [['ID', 'Tip', 'Correction', 'Thickness', 'Resistance']]
        #start counting from the first mean
        self.countOfRes = 1

    def getListOfMeasureMents(self):
        #returns list containing four user-inputted values to test for
        return self.listOfMeasurements

    def getSpecificMeasurement(self, num):
        return self.listOfMeasurements[num]

    def addToList(self, lis):
        #add lis to the end of list 'l'
        temp = self.listOfMeasurements
        temp.append(lis)
        self.listOfMeasurements = temp
        #self.listWasChanged()

    def listWasChanged(self):
        self.vc.listWasChangedDelegate()

    def clearList(self):
        #clears list of previous measurements
        self.listOfMeasurements.clear()

    def updateCountOfRes(self):
        #change number that is used to define what mean is being set
        self.countOfRes += 1
        #loop [1, 5]
        if(self.countOfRes==6):
            self.countOfRes=1

class ResistanceViewController:
    #initialize primary view controller
    def __init__(self, parent):
        #needed for view
        self.parent = parent
        #model for controller to communicate with
        self.model = MeasurementsModel(self)
        #view for controller to communicate with
        self.view = ResistanceView(self)
        #get list of all resources connected to device
        rm = visa.ResourceManager()
        #print resources, for debugging
        print(rm.list_resources())
        #interact with supply, which is a global object
        global supply
        try:
            #try to connect to resource connected
            supply = rm.open_resource('USB0::0x0957::0x4D18::MY54220089::INSTR')
        except visa.VisaIOError:
            #if error is detected, let user know and kill program
            print("No object found, please connect device")
            sys.exit(1)
        #this can measure voltage, not needed for this program now. left for example
        #print(supply.query("MEASure:VOLTage:DC?"))


    def measurePressed(self):
        #take in value from entry fields and proceed with taking measurements
        try:
            #get resistance from probes connected to device
            res = supply.query("MEASure:RESistance?")
            #print this for debugging
            print(self.model.countOfRes)
            #set appropriate numbered mean text to the resistance just received
            self.view.setMeanText(self.model.countOfRes, res)
            #temporary list to store needed values that can be passed all together to model's main list
            tempResList = []
            #add id, tip, correction, thickness, resistance
            tempResList.append(self.view.getIdText())
            tempResList.append(self.view.getTipText())
            tempResList.append(self.view.getCorrectionText())
            tempResList.append(self.view.getThicknessText())
            tempResList.append(res)
            #print this list for debugging
            print(tempResList)
            #add this list to model's main list (of lists)
            self.model.addToList(tempResList)
            #print model's main list for debugging
            print(self.model.listOfMeasurements)
            #make sure next resistance gets set to appropriate mean number
            self.model.updateCountOfRes()
        except visa.VisaIOError:
            #if unable to query, there is an issue with connecting to device
            print("Error connecting to device, please recheck connection and restart")
            #sys.exit(1)

    def exportPressed(self):
        #use list of user-inputted measurements to export data
        self.write_to_csv(self.model.listOfMeasurements)

    def write_to_csv(self, l):
        #open csv file to be written to. creates if nonexistant and overrides otherwise
        with open('resistancedata.csv', 'w', newline='') as csvfile:
            #make an object that allows for writing
            csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            #l should be one list, the main list from model
            for i in l:
                #write all contents of each list to csv file
                csvwriter.writerow(i)
                #print these elements for debugging
                print(i)

    def listWasChangedDelegate(self):
        #gets called when list is changed in model
        #nothing particularly needed here, simply prints the list to see what was changed
        print(self.model.getListOfMeasureMents())


class ResistanceView:
    def loadView(self):
        #primary setep of main GUI objects
        #Create and place objects simultaneously
        # Column 0, Entry Labels
        id_label = Label(self.frame, text="ID").grid(row=0, column=0)
        tip_label = Label(self.frame, text="Tip Spacing").grid(row=1, column=0)
        correction_label = Label(self.frame, text="Correction Factor").grid(row=2, column=0)
        thickness_label = Label(self.frame, text="Thickness").grid(row=3, column=0)

        # Column 1, Entry Fields
        id_entry = Entry(self.frame, textvariable=self.id_entry_text).grid(row=0, column=1)
        tip_entry = Entry(self.frame, textvariable=self.tip_entry_text).grid(row=1, column=1)
        correction_entry = Entry(self.frame, textvariable=self.correction_entry_text).grid(row=2, column=1)
        thickness_entry = Entry(self.frame, textvariable=self.thickness_entry_text).grid(row=3, column=1)

        # Column 2, Command Buttons
        take_button = Button(self.frame, text="Take Measurement", command=self.vc.measurePressed).grid(row=0, rowspan=3, column=2, sticky=N+S+E+W)
        export_button = Button(self.frame, text="Export Data", command=self.vc.exportPressed).grid(row=3, rowspan=2, column=2, sticky=N+S+E+W)

        # Column 3, Recorded Means of Last Measurement
        mean1 = Label(self.frame, textvariable=self.m1_label_text).grid(row=0, column=3)
        mean2 = Label(self.frame, textvariable=self.m2_label_text).grid(row=1, column=3)
        mean3 = Label(self.frame, textvariable=self.m3_label_text).grid(row=2, column=3)
        mean4 = Label(self.frame, textvariable=self.m4_label_text).grid(row=3, column=3)
        mean5 = Label(self.frame, textvariable=self.m5_label_text).grid(row=4, column=3)

        # Column 4, Average Means
        mean_label = Label(self.frame, text="Mean: 0").grid(row=0, rowspan=3, column=4)
        rmean_label = Label(self.frame, text="R_Mean: 0").grid(row=3, rowspan=2, column=4)

    #initialize view
    def __init__(self, vc):
        #basic setup
        self.frame = Frame()
        self.frame.grid(row=0, column=0)
        #create controller object to communicate with ResistanceViewController
        self.vc = vc
        #create default values of important labels/entries
        #tkinter uses StringVar
        self.correction_entry_text = StringVar()
        self.thickness_entry_text = StringVar()
        self.id_entry_text = StringVar()
        self.tip_entry_text = StringVar()
        #mean values will have default text
        self.m1_label_text = StringVar()
        self.m1_label_text.set('Mean 1: 0')
        self.m2_label_text = StringVar()
        self.m2_label_text.set('Mean 2: 0')
        self.m3_label_text = StringVar()
        self.m3_label_text.set('Mean 3: 0')
        self.m4_label_text = StringVar()
        self.m4_label_text.set('Mean 4: 0')
        self.m5_label_text = StringVar()
        self.m5_label_text.set('Mean 5: 0')
        #call load view to show program and continue forward
        self.loadView()

    def getIdText(self):
        #returns string of the text entered for ID
        return self.id_entry_text.get()

    def getTipText(self):
        #returns string of the text entered for tip
        return self.tip_entry_text.get()

    def getCorrectionText(self):
        #returns string of the text entered for correction
        return self.correction_entry_text.get()

    def getThicknessText(self):
        #returns string of the text entered for thickness
        return self.thickness_entry_text.get()

    def setMeanText(self, id, value):
        #update means in view based on which one is active
        #bastardized python switch on id for [1, 5]
        #set appropriate mean value as decided by id
        if(id==1):
            self.m1_label_text.set("Mean 1: " + value)
        if(id==2):
            self.m2_label_text.set("Mean 2: " + value)
        if(id==3):
            self.m3_label_text.set("Mean 3: " + value)
        if(id==4):
            self.m4_label_text.set("Mean 4: " + value)
        if(id==5):
            self.m5_label_text.set("Mean 5: " + value)

    def setM1Text(self, text):
        #sets text of mean 1 label
        self.m1_label_text.set('Mean 1: '+text)

    def setM2Text(self, text):
        #sets text of mean 2 label
        self.m2_label_text.set('Mean 2: '+text)

    def setM3Text(self, text):
        #sets text of mean 3 label
        self.m3_label_text.set('Mean 3: '+text)

    def setM4Text(self, text):
        #sets text of mean 4 label
        self.m4_label_text.set('Mean 4: '+text)

    def setM5Text(self, text):
        #sets text of mean 5 label
        self.m5_label_text.set('Mean 5: '+text)

def main():
    # start of program
    root = Tk()
    # set background color
    frame = Frame(root, bg='#0555ff')
    root.title("Resistance GUI")
    # main chunk of program
    app = ResistanceViewController(root)
    root.mainloop()

if __name__ == '__main__':
    main()