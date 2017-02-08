from tkinter import Tk, Label, Button, Entry, N, E, S, W, Frame, StringVar
import visa
import csv

supply = None

class MeasurementsModel:
    #initialize model
    def __init__(self, vc):
        #vc is for communication with ResistanceViewController
        self.vc = vc
        self.l = []
        self.countOfRes = 1

    def write_csv(self, l):
        pass

    def supply_header_row(self):
        pass

    def supply_data_row(self):
        pass

    def getListOfMeasureMents(self):
        #returns list containing four user-inputted values to test for
        return self.l

    def getSpecificMeasurement(self, num):
        return self.l[num]

    def addToList(self, lis):
        #add lis to the end of list 'l'
        temp = self.l
        temp.append(lis)
        self.l = temp
        #self.listWasChanged()

    def listWasChanged(self):
        self.vc.listWasChangedDelegate()

    def clearList(self):
        #clears list of previous measurements
        self.l.clear()

    def updateCountOfRes(self):
        #change number that is used to define what mean is being set
        self.countOfRes += 1
        #loop [1, 5]
        if(self.countOfRes==6):
            self.countOfRes=1

class ResistanceViewController: #Conforms to ResistanceViewProtocol (it can act as a delegate for the view)
    #initialize primary view controller
    def __init__(self, parent):
        self.parent = parent
        self.model = MeasurementsModel(self)

        rm = visa.ResourceManager()
        print(rm.list_resources())
        global supply
        supply = rm.open_resource('USB0::0x0957::0x4D18::MY54220089::INSTR')
        print(supply.query("MEASure:VOLTage:DC?"))
        print(type(supply))
        self.view = ResistanceView(self)

    def measurePressed(self):
        #take in value from entry fields and proceed with taking measurements
        self.takeMeasurement()
        """
        self.model.clearList()
        self.model.addToList(self.view.id_entry_text)
        self.model.addToList(self.view.tip_entry_text)
        self.model.addToList(self.view.correction_entry_text)
        self.model.addToList(self.view.thickness_entry_text)"""

    def exportPressed(self):
        #use list of user-inputted measurements to export data
        self.write_to_csv(self.model.l)

    def takeMeasurement(self):
        try:
            res = supply.query("MEASure:RESistance?")
            print(self.model.countOfRes)
            self.view.setMeanText(self.model.countOfRes, res)
            #self.view.setM1Text(supply.query("MEASure:RESistance?"))
            temp = []
            #add id, tip, correction, thickness
            temp.append(self.view.getIdText())
            temp.append(self.view.getTipText())
            temp.append(self.view.getCorrectionText())
            temp.append(self.view.getThicknessText())
            temp.append(supply.query("MEASure:RESistance?"))
            print(temp)
            self.model.addToList(temp)
            print(self.model.l)
            self.model.updateCountOfRes()
        except visa.VisaIOError:
            print("Error connecting to device")
        #else:
         #   print("General error")

    def write_to_csv(self, l):
        with open('resistancedata.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for i in l:
                csvwriter.writerow(i)
                print(i)

    def listWasChangedDeleate(self):
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
        #communicate with ResistanceViewController
        self.vc = vc
        #create default values of important labels/entries
        self.correction_entry_text = StringVar()
        self.thickness_entry_text = StringVar()
        self.id_entry_text = StringVar()
        self.tip_entry_text = StringVar()
        self.m1_label_text = StringVar()
        self.m1_label_text.set('Mean 1: 1')
        self.m2_label_text = StringVar()
        self.m2_label_text.set('Mean 2: 2')
        self.m3_label_text = StringVar()
        self.m3_label_text.set('Mean 3: 3')
        self.m4_label_text = StringVar()
        self.m4_label_text.set('Mean 4: 4')
        self.m5_label_text = StringVar()
        self.m5_label_text.set('Mean 5: 5')
        #call load view to show program
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
        print(id)
        print(type(id))
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

if __name__ == '__main__':
    #start of program
    root = Tk()
    frame = Frame(root, bg='#0555ff')
    root.title("Resistance GUI")
    app = ResistanceViewController(root)
    root.mainloop()