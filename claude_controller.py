import subprocess
import shutil
from pathlib import Path
import json
from prompts import Prompt, PromptDict
from analyze import compare_configs

### THIS SCRIPT MUST BE RUN FROM THE Agc_claude DIRECTORY, OTHERWISE FILE PATHS WILL NOT WORK PROPERLY ###

# Global info
jsonl_filename = "../runs_archive.jsonl"
prompt_prefix = """
FILE EDIT POLICY (must follow):
- Do not write, edit, delete, or rename any files.
- If changes are needed, output a unified diff only.
- The diff must include file paths and enough context lines to apply cleanly.
- Do not include any explanation inside the diff block.
- If information is missing to generate a correct diff, ask one concise question.
"""

            
# METHODS
# MUST be run from Agc_claude directory


# Ask user to type idenitifier and query
def getIDQuery(directory: PromptDict):
    # First ask user if they would like to manally enter prompt or import from a .txt file
    method = input("Would you like to (1) manually enter a query or (2) import a query from a .txt file? (Enter 1 or 2): ")
    if method == "1":
        identifier = input("Enter a unique identifier: ")
        # Add check to see if directory already has this identifier, if yes ask for a different one
        while directory.findPrompt(identifier) is not None:
            print("Identifier already exists in directory. Please enter a different one.")
            identifier = input("Enter a unique identifier: ")
        user_query = input("Enter query for Claude:\n>")
        return identifier, user_query
    elif method == "2":
        filepath = '../queries/' + input("Enter the file path of the .txt file containing the query (relative to queries directory, without .txt): ") + '.txt'
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                user_query = f.read()
            identifier = filepath.split("/")[-1].split(".")[0] # use the filename without .txt and directory name
            return identifier, user_query
        except FileNotFoundError:
            print("File not found.")
            return None, None
    else:
        print("Invalid input.")
        return None, None

# Give the query to Claude and get output and error logs, save as Prompt object
def promptClaude(identifier: str, query: str):
    process = subprocess.run(
        ["claude", "-p", query + "\n"],
        capture_output=True,
        text=True
    )
    print("returncode:", process.returncode)
    print("stdout:\n", process.stdout)
    print("stderr:\n", process.stderr)
    
    prompt = Prompt(identifier, query, process.stdout, process.stderr, process.returncode, (process.returncode == 0))
    print("Saved prompt object")
    return prompt

# Extract the unified diff from the output log of a prompt, if it exists, else return None
def extractDiff(prompt: Prompt):
    output = prompt.output
    diff_start = output.find("```diff") # look for the start of the diff block, which should be denoted by ```diff
    if diff_start == -1: # if no diff block is found, return None
        return None
    diff_end = output.find("```", diff_start + 6) # look for the end of the diff block, which should be denoted by ``` and should come after the start of the diff block
    if diff_end == -1: # if no end of diff block is found, meaning the diff block is not closed properly, return None
        return None
    diff = output[diff_start + 7:diff_end].strip() # extract the diff from the output log, removing the ```diff and ``` markers, and stripping any leading or trailing whitespace
    return diff

# Implement the unified diff to the given files, pass it as a prompt to Claude to implement the changes.
# CURRENTLY DOES NOT WORK
def implementDiff(diff: str):
    pre_prompt = """
    The following unified diff describes changes that need to be made to the given file(s).
    Please implement the changes described in the diff.
    You have permission to edit the specified files as needed to implement these changes.  Do not edit any other files. \n
    """
    # Get list of files to be modified
    files_to_modify = set()
    for line in diff.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            filename = line[6:] # get the file path from the diff line, which should come after the "+++ " or "--- " marker and the "a/" or "b/" marker
            filepath = "Claude_Sandbox/" + filename
            files_to_modify.add(filepath)
    # Append list of allowed files to edit to the pre-prompt 
    pre_prompt += "You have permission to edit the following files: " + ", ".join(files_to_modify) + "\n\n"
    # Now pass the pre_prompt and the diff as a prompt to Claude
    full_prompt = pre_prompt + "Here is the unified diff:\n```diff\n" + diff + "\n```\n"
    process = subprocess.run(
        ["claude", "-p", full_prompt],
        capture_output=True,
        text=True
    )
    print("returncode:", process.returncode)
    print("stdout:\n", process.stdout)
    print("stderr:\n", process.stderr)

def displayMainMenu():
    print("Main menu options:")
    print("1. Load new prompt archive")
    print("2. Prompt Claude with query")
    print("3. View all prompts")
    print("4. [PLACEHOLDER] for analysis tools")
    print("5. Export current directory")
    print("6. Print specific prompt")
    print("7. Implement diff from specific prompt")
    print("Press 'q' to quit")
    print("\n")

# Main function, runs at the start of this python script
def main():
    print("Welcome to the Claude controller script.")
    print("Here you can pass a query to prompt Claude, as well as store and analyse the results.")
    print("JSONL Archive file: " + jsonl_filename)
    print("\n")
    
    directory = PromptDict()
    
    displayMainMenu()
    
    entry = input("Select a menu option: ")
    while entry != "q":
        selection = int(entry)
        while selection not in range(1, 10):
            selection = input("Invalid option.  Select again:")
        
        # Load new prompt archive from JSONL file into prompt directorys
        if selection == 1:
            print("WARNING !!  This will overwrite the current prompt directory; exporting it to a JSONL file first is recommended.")
            proceed = input("Are you sure you would like to proceed (y/n)? ")
            if proceed == "y":
                name = input("Which file would you like to import? (Enter filename without .jsonl) ")
                filepath = "../run_archives/" + name + ".jsonl"
                directory.loadFromJsonl(filepath)
                print("Successfully loaded prompts from " + filepath)
        
        # Query Claude and add prompt to directory
        if selection == 2:
            identifier, query = getIDQuery(directory)
            prompt = promptClaude(identifier, query)
            directory.addPrompt(prompt)
            print("Added prompt to directory")
            print("Directory now has " + str(directory.getSize()) + " prompt(s).")
        
        # Print full list of prompts
        if selection == 3:
            directory.printPrompts()

        # Analyze (right now only compare configs)
        if selection == 4:
            print("Analysis tools:")
            print("1. Compare generated config with original")

            analysis_choice = input("Select an analysis tool: ")

            # Compare generated config with original config
            if analysis_choice == "1":
                og_filepath = input("Enter the path to the original config file: ")
                promptid = input("Enter the prompt ID to analyze: ")
                prompt = directory.findPrompt(promptid)
                if prompt is not None:
                    print("Comparing ... ")
                    differences = compare_configs(og_filepath, prompt)
                    print("Comparison complete.", len(differences), " differences found:")
                    print("------------------")
                    for og_line, gen_line in differences:
                        print(f"Original: {og_line}")
                        print(f"Generated: {gen_line}")
                else:
                    print("Prompt with ID " + promptid + " not found in directory.")

        
        # Export prompt directory to JSONL file
        if selection == 5:
            name = input("Choose name for JSONL file (omit .jsonl in your entry):")
            filename = name + ".jsonl"
            filepath = "../run_archives/" + filename
            # Check if file already exists in run_archives, to avoid overwriting
            directory.exportToJsonl(filepath)
            print("Successfully exported current directory to " + filepath)
        
        # Prints a specific prompt the user specifies
        if selection == 6:
            promptid = input("Enter prompt ID to be printed: ")
            prompt = directory.findPrompt(promptid)
            if prompt is not None:
                prompt.printPrompt(q_size=1000, o_size=1000, e_size=1000)
            else:
                print("Prompt with ID " + promptid + " not found in directory.")

        # Implement diff from a specific prompt, if it exists
        if selection == 7:
            promptid = input("Enter prompt ID to extract diff from and implement: ")
            prompt = directory.findPrompt(promptid)
            if prompt is not None:
                diff = extractDiff(prompt)
                if diff is not None:
                    implementDiff(diff)
                else:
                    print("No unified diff found in output log of prompt with ID " + promptid)
            else:
                print("Prompt with ID " + promptid + " not found in directory.")
        
        # Show main menu again
        displayMainMenu()
        
        entry = input("Select a menu option: ")
    
if __name__ == "__main__":
    main()