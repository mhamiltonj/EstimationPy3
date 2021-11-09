'''
Created on Nov 7, 2013

@author: marco
'''
import matplotlib.pyplot as plt
from FmuUtils import Model, Strings

def main():
    
    # Initialize the FMU model empty
    m = Model.Model()
    
    # Assign an existing FMU to the model
    filePath = "../../../modelica/FmuExamples/Resources/FMUs/HeatExchanger.fmu"
    
    # ReInit the model with the new FMU
    m.ReInit(filePath, atol=1e-5, rtol=1e-6)
    
    # Show details
    print(m)
    
    # Show the inputs
    print("The names of the FMU inputs are: ", m.GetInputNames(), "\n")
    
    # Show the outputs
    print("The names of the FMU outputs are:", m.GetOutputNames(), "\n")
    
    # Set the CSV file associated to the input
    inputPath = "../../../modelica/FmuExamples/Resources/data/SimulationData_HeatExchanger.csv"
    input = m.GetInputByName("mFlow_cold")
    input.GetCsvReader().OpenCSV(inputPath)
    input.GetCsvReader().SetSelectedColumn("heatExchanger.mFlow_COLD")
        
    input = m.GetInputByName("mFlow_hot")
    input.GetCsvReader().OpenCSV(inputPath)
    input.GetCsvReader().SetSelectedColumn("heatExchanger.mFlow_HOT")
        
    input = m.GetInputByName("T_hot")
    input.GetCsvReader().OpenCSV(inputPath)
    input.GetCsvReader().SetSelectedColumn("heatExchanger.Thot_IN")
        
    input = m.GetInputByName("T_cold")
    input.GetCsvReader().OpenCSV(inputPath)
    input.GetCsvReader().SetSelectedColumn("heatExchanger.Tcold_IN")
    
    m.GetState()
    
    # Initialize the model for the simulation
    m.InitializeSimulator()
                        
    # Simulate
    time, results = m.Simulate()
    
    # Show the results
    showResults(time, results)

def showResults(time, results):
    
    fig1 = plt.figure()
    ax1  = fig1.add_subplot(211)
    ax1.plot(time,results["Thot_IN"],'r',label='$T_{Hot}^{IN}$',alpha=1.0)
    ax1.plot(time,results["Thot_OUT"],'r--',label='$T_{Hot}^{OUT}$',alpha=1.0)
    ax1.plot(time,results["Tcold_IN"],'b',label='$T_{Cold}^{IN}$',alpha=1.0)
    ax1.plot(time,results["Tcold_OUT"],'b--',label='$T_{Cold}^{OUT}$',alpha=1.0)
    ax1.plot(time,results["Tmetal"],'k',label='$T_{Metal}$',alpha=1.0)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Water temperatures ')
    ax1.set_xlim([time[0], time[-1]])
    legend = ax1.legend(loc='upper center',bbox_to_anchor=(0.5, 1.1), ncol=5, fancybox=True, shadow=True)
    legend.draggable()
    ax1.grid(False)
    
    ax2  = fig1.add_subplot(212)
    ax2.plot(time,results["mFlow_COLD"],'b',label='$\dot{m}_{COLD}$',alpha=1.0)
    ax2.plot(time,results["mFlow_HOT"],'r',label='$\dot{m}_{HOT}$',alpha=1.0)
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Water flows')
    ax2.set_xlim([time[0], time[-1]])
    legend = ax2.legend(loc='upper center',bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)
    legend.draggable()
    ax2.grid(False)
    
    plt.savefig('FirstOrder.pdf',dpi=300, bbox_inches='tight', transparent=True,pad_inches=0.1)
    plt.show()
   
if __name__ == '__main__':
    main()