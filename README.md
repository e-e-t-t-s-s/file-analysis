# file-analysis
File content analysis, detection and classification

## RegexGenerator.py
Description: Generate Regular Expressions to match Positive set files while not matching Negative set files utilizing overlapping hexadecimal Unicode values.

Requirements:
- Python 3+

Input:
- -p/--positive - Directory containing files for the Positive set (what you want to detect)
- -n/--negative - Directory containing files for the Negative set (what you **dont** want to detect)
- -o/--output - Output file name, where the training report and results will be sent. Appends output if file exists already.
- -s/--scope - Number of characters included before AND after the key character. A higher number in scope will increase RAM usage! Defaults to 3
- -r/--rerun - After first run, decrement the scope and re-run until scope is zero
- -d/--detail - Increase report output details, shows per regStr per file scores, file total scores, and results from before AND after pruning
- -f/--force - Force proceed when scope is greater than 5


Outputs:
- Regular Expressions and Report text to disk
