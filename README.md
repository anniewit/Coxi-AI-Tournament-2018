# CAT 2018
game environment, comparison_agent and default_agent were provided by the organizers

Agent of my group: final_cateze.py (see ChaosCoxiClub directory)
Approach: train neural network (smart_cateze.py) with genetic algorithm (genetic_algorithm_multiple.py)

----------------------------------------------------------------------

Environment and Evaluation Scripts for the CAT 2018.

Usage requires python 2.7 as well as all the packages mentioned in requirements.txt. 

If you are operating in an Anaconda environment as recommended, it should suffice to do "pip install pygame" first. 

For the introduction slides, see "CAT 2018 - Getting You Started.pdf".


### Demo Script (demo.py)

Use this script to let two agents (defaul_agent.py, comparison_agent.py) fight against each other on a standard skirmish field.

### Example Agents (default_agent.py, comparison_agent.py)

The two example agents provided by us, the basis for your own agents. "default_agent.py" is the ingame dummy agent, "comparison_agent.py" is a slightly tweaked version of it.

### Replay Viewing Script (replayer.py)

Use this script to view existing pickled .replay files.

Usage: python replayer.py PATH [-g if rendered]
The PATH may be a file or a folder, if it is a folder then all replay files within the folder will be played.

### Casual Clash Evaluation Script (casual_clash_evaluation_script.py)

Evaluation script for the Casual Clash. Matches all agents in the folder casual_clash_files/agents against each other, with each match consisting of one game each in the three modes "Duel", "Skirmish" and "Battle". Stores statistics in casual_clash_files as .csv files. Stores pickled replays of each match in the folder casual_clash_files/replays as .replay files. 
