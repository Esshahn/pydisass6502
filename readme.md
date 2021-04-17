# pyDisAss6502 

A simple 6502 machine language disassembler written in Python.

This disassembler is in a very early phase but already quite functional.
The main disadvantage of this disassembler compared to UI based programs is the lack of an interactive interface to define which sections are code and which are data.

## Usage

```
python3 disass.py -i filename [-o filename] [-e] [-nc]
```

`-i filename` or `--input filename`  
Binary file to load, e.g. `game.prg` that you want to disassemble

`-o outputfile` or `--output filename` (optional)
Name of the genereated assembly code to be saved, e.g. `output.asm`. If no name is provided, the suffix `.asm` will be added to the input filename, e.g. `game.prg.asm`.

`-e` or `--entrypoints` (optional, no params)  
If used, user defined entrypoints will be parsed specifically as code or data sections. This is extremely helpful if you know that a specific section is clearly code and not data, see below.

`nc` or `nocomments` (optional, no params)    
If used, the address descriptions from the file `c64-mapping.json` will *NOT BE* be inserted as comments into the output file.


## JSON files

`lib/opcodes.json`  
A description of all 256 opcodes that are available for the 6502 processor, including illegal opcodes. You can add more keys to the list if you know what you're doing, otherwise this one is better be left as is.

`lib/c64-mapping.json`  
A list of significant addresses for the C64, e.g. `D020` for the border color. Can be extended to your personal liking. Also more mappings for other 6502 based computers (C16, C116, Plus/4, C128, VC20) could be added as separate files. In addition, language translations could be added. Happily taking Pull Requests.

`entrypoints.json`  
List of addresses that should be marked as code or data section and override any other setting. Valuable if you know that a data section is code, or to peek into data sections and check if they are code. You can and should modify this file whenevery you disassemble a file.



For more information check out the article I wrote about it: 
https://www.awsm.de/blog/pydisass/


## ToDo

* external config file for multiple ass dialects
* cleanup code formatting
* improve data formatting
