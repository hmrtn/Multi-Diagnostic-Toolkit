![alt text](https://raw.githubusercontent.com/hansmrtn/Multi-Diagnostic-Plotter/master/assets/ic_aplotter.png)

# Multi-Diagnostic-Plotter

The Multi-Diagnostic Plotter (MDP) is a multi-functional plotter for the Advanced Propulsion Laboratory at the University of Washington. The program requires Python 3 and the interface framework relies on PyQt5. By default, all the data is filtered using a [Butterworth Filter](https://en.wikipedia.org/wiki/Butterworth_filter) algorithm. 


Feel free to use, modify, and reproduce the source.

## How to use

Steps
1. Download the source via git or zip
2. Delete the .gitignore files located in each subdirectory -- these are place holders and will interfere
3. Place the raw data -- from LabView as raw text -- into a properly titled folder in each subdirectory. 
    DLP is for Langmuir Analysis, RPA is for Retarding Potential analysis, NFP is for Nude Faraday analysis (not yet implemented).
4. Run the MDP.py

## Other Options

1. **To Change IVDF Time Slice**: In MDP.py, modify the constant called TIME_2_SLICE. The default is 400. Here you will see other options that can be changed as well.
2. **To display other or intermediate plots**: There is a function called plot_dict located in rplt.py. 

'''python
  
    def plot_dict(dict):
      plt.figure()
      for key in dict.keys():
          for value in dict[key]:
              plt.plot(value)
      plt.show()
 '''
 By calling this function and providing an the dictionary type argument, you can plot all the data in the dictionary a single plot.
