import visa

rm = visa.ResourceManager()
print (rm.list_resources())
supply = rm.open_resource('USB0::0x0957::0x4D18::MY54220089::INSTR')
#supply.write(":OUTPut:STATe 0")
#supply.write("SOURce:VOLTage:LEVel:IMMediate:AMPLitude 0")

print (supply.write(":READ?"))