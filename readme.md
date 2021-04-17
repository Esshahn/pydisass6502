# pyDisAss6502 

A simple 6502 machine language disassembler written in Python.

This disassembler is in a very early phase but already quite functional.
The main disadvantage of this disassembler compared to UI based programs is the lack of an interactive interface to define which sections are code and which are data.

## Usage

```
python3 disass.py -i filename [-o filename] [-e filename] [-nc]
```

`-i filename` or `--input filename`  
Binary file to load, e.g. `game.prg` that you want to disassemble

`-o outputfile` or `--output filename` (optional)  
Name of the genereated assembly code to be saved, e.g. `output.asm`. If no name is provided, the suffix `.asm` will be added to the input filename, e.g. `game.prg.asm`.

`-e filename` or `--entrypoints filename` (optional)  
If used, user defined entrypoints will be parsed specifically as code or data sections. This is extremely helpful if you know that a specific section is clearly code and not data, see below. Check the example `entrypoints.json` for reference.

`-nc` or `--nocomments` (optional, no params)  
If used, the address descriptions from the file `c64-mapping.json` will *NOT BE* be inserted as comments into the output file.

## Examples

```
python3 disass.py --input flt.prg -nocomments
```

Imports the file `flt.prg`, parses it without comments and writes the output assembly code as `flt.prg.asm` into the same directory.


```
python3 disass.py -i source/flt.prg -o code/flt.asm -e entrypoints.json 
```

Imports the file `flt.org` located in the `source` folder, parses it with comments and using custom entrypoints defined in `entrypoints.json` and writes the output assembly code as `flt.asm` into the `code` folder.

## JSON files

`lib/opcodes.json`  
A description of all 256 opcodes that are available for the 6502 processor, including illegal opcodes. You can add more keys to the list if you know what you're doing, otherwise this one is better be left as is.

`lib/c64-mapping.json`  
A list of significant addresses for the C64, e.g. `D020` for the border color. Can be extended to your personal liking. Also more mappings for other 6502 based computers (C16, C116, Plus/4, C128, VC20) could be added as separate files. In addition, language translations could be added. Happily taking Pull Requests.

`entrypoints.json`  
List of addresses that should be marked as code or data section and override any other setting. Valuable if you know that a data section is code, or to peek into data sections and check if they are code. You can and should modify this file whenevery you disassemble a file.

## Execute pydisass from anywhere

You might want to make pydisass available from any location in your terminal by just typing 

```
disass -i flt.prg
```

To achieve this, follow these steps (at least on a Mac, feel free to add the correct way for Windows and Linux):

1. Set the right location of your `python` installation in `disass.py`  
Do this by changing the first line of the script, which reads `#!/usr/local/bin/python3`

2. Change execution rights of the script  
Open your terminal, locate the folder `disass.py` is in and type into the terminal `chmod +x disass.py`

3. Add the location of the file to your `PATH` environment  
Open your terminal and enter `cd`. Next, enter `sudo nano .profile`. This opens a text editor. In there, add the following line:

```
export PATH=$PATH:/Users/usernmae/pathto/folder
```

Make sure to adapt this line to your settings by replacing the `username` with your username and the `pathto/folder` with the right path to the location of the pydisass folder.

4. Rename `disass.py` to `disass` (optional)  
If you like it nice and short, you can drop the `.py` suffix as well

After restarting your terminal, you should be able to execute the disassembler from anywhere.



For more information check out the article I wrote about it: 
https://www.awsm.de/blog/pydisass/


## ToDo

* external config file for multiple ass dialects
* cleanup code formatting
* improve data formatting
