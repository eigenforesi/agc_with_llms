**Cabinetry with Claude**

This repository contains code to use Claude to implement cabinetry in an analysis pipeline for the Analysis Grand Challenge.  The main file (and the file to run) is the claude_controller.py file, which allows the user to prompt Claude, view and save the output, and (soon!) implement the results.

**Overview**

Run the claude_controller.py file *from the Agc_claude directory* (this is important!).  You will see a main menu with options.  Since at first you will likely not have any prompts to work with, you may choose the option to prompt Claude with a query.  You will supply a unique identifier and type a query into the terminal.  Then Claude will think and generate an output.  If the prompt requests code to be written, Claude will output a unified diff.  There is another step where you can actually implement this unified diff, however for now it only works if you have already given Claude writing permissions for all relevant files.

The testing.py and test_nb.ipynb files in the Claude Sandbox are used for testing methods not necessarily relevant to the AGC.  This is good for initial tests, or trying out different concepts before applying them to the AGC.

After prompting Claude, your query and output (and any error log) will be added to prompt directory object.  At any point, you may export the prompt directory as a .jsonl file which will appear in the run_archives directory.  At any point, you may also load a set of prompts from a .jsonl file.  Beware that if you load a new directory or stop running the controller script, any prompts saved in the current prompt directory will be lost.  It is recommended to export the current prompt directory before quitting or loading a new directory.

**First Steps with Cabinetry**

There are three .txt files in the queries directory.  These will be refined in order to define the tasks of creating a config .yml file, creating a cabinetry workspace, and performing the fit.  A fourth file will be added telling Claude to view results of the fit.  For now these are not yet fully developed.

For now, you can attempt the create_workspace.txt prompt