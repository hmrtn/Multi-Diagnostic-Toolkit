![alt text](https://raw.githubusercontent.com/hansmrtn/Multi-Diagnostic-Plotter/master/assets/ic_aplotter.png)
![alt text](https://i.imgur.com/sX4OC3z.png)
# Multi-Diagnostic Toolkit

The Multi-Diagnostic Toolkit Project (MDP) is a small but powerful tool to transform and display data produced by the University of Washington's Advanced Propulsion Labratory. The MDP's purpose is simplify tedious calculation and manipulation on large datasets of an oscilascope signal that displays in an interactive plot window. The program is designed for use with Advanced Propulsion Laboratory's instruments and data only and is not recommened for use elsewhere. The MDP is designed to be as modular as possible and written in Python 3. 

## How to use

Open MDP by either running the executable* file, or by running `$ python mdp.py` in the terminal. The second option requires Python 3 and The MDP's library dependecies. Installing the [Anaconda Python Platform](https://www.anaconda.com/download/) is recommended. 

The main interface features a dropdown menu to choose what type of data MDP will iterpret and display.  

## Features
- Current Signal compatibility:
    - Langmuir Probe
    - Retarding Energy Field Analyzer
    - Faraday Probe
    - Raw signal 
- Export plot image files
- Plot Ion velocity distribution functions
- Time-of-Flight Langmuir probe analysis
- Parameterized [Butterworth](https://en.wikipedia.org/wiki/Butterworth_filter) signal filter
- Export transformed data

### Known Bugs / Future Additions
- ~~Normalized IVDF trace~~ (v1.3.2)
- ~~Time of Flight not properly displaying time interval~~ (v1.3.2)
- ~~Unexpected crash upon directory error~~ (v1.3.2)
- No default directories on menu selection
- Ambiguous Subplot for REFA
- NFP Analysis UI
- Long directory title in plot window for single plots
- Ambigous UI Location -> Directory
###
