# Multi-Diagnostic Toolkit
![alt text](https://i.imgur.com/G1OBNnY.png)

The Multi-Diagnostic Toolkit Project (MDP) is a small but powerful tool to transform and display data produced by the University of Washington's Advanced Propulsion Laboratory. The MDP's purpose is simplify tedious signal processing of large datasets produced by The Advanced Propulsion Laboratory's instrumentation. 

## How to use

Open MDP by either running the executable* file, or by running `$ python mdp.py` in the terminal. The second option requires Python 3 and The MDP's library dependencies. Installing the [Anaconda Python Platform](https://www.anaconda.com/download/) is recommended.

The main interface features a dropdown menu to choose what type of data MDP will interpret and display.  

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
###
