# pyDisass6502 


A simple 6502 machine language disassembler written in Python.

This disassembler is in a very early phase but already quite functional.
The main disadvantage of this disassembler compared to UI based programs
is the lack of an interactive interface to define which sections are code and which are data.

However it provides coverage statistics in a convenient format for manual iteration and annotation
of the image.  One real use case is reverse engineering the
[Atari Eastern Front 1941 cartridge image](https://github.com/patricksurry/eastern-front-1941).

For more information check out the article I wrote about it: https://www.awsm.de/blog/pydisass/

## Usage

```
python3 disass.py -i filename [-o filename] [-e filename] [-c filename] [-m filename] [-s startaddress] [-nc] [-nx]
```

`-i filename` or `--input filename`  
Binary file to load, e.g. `game.prg` that you want to disassemble

`-o outputfile` or `--output filename` (optional)  
Name of the genereated assembly code to be saved, e.g. `output.asm`. If no name is provided, the suffix `.asm` will be added to the input filename, e.g. `game.prg.asm`.

`-e filename` or `--entrypoints filename` (optional)  
If used, user defined entrypoints will be parsed specifically as code or data sections. This is extremely helpful if you know that a specific section is clearly code and not data, see below. Check the example `entrypoints.json` for reference.

`-c filename` or `--counts filename` (optional)
If specified, coverage statistics will be reported for code, data and hex constants in the disassembly.
These are provided in the same format as the entrypoints file so you can cut and paste after adding meaningful names
and/or comments.

`-m filename` or `--mapping filename` (optional)
If specificd, use the specified system mapping file to add annotations for external entrypoints or data elements. By default a C64 mapping from `lib/c64-mapping.json` is used.
An Atari mapping is also available in `lib/atari-mapping.json`.

`-s startaddress` or `--startaddress startaddress` (optional)
Assume the memory image is loaded at `startaddress`.
By default, the first two bytes `llhh` of the input file are assumed to represent the start address of the image,
and are discarded from the disassembly.  Other platforms use different conventions.
This option can also be provided in the `--entrypoints` file.

`-nc` or `--nocomments` (optional, no params)  
If used, no system mapping (e.g. `c64-mapping.json`) will be used to insert external symbols and comments.

`-nx` or `--nohexdump` (optional, no params)
By default the disassembly will include a comment on each line showing the current program counter
(offset based on the start address) along with the bytes represented on that line.
For code lines the raw bytes are shown, for data lines the ascii equivalent is shown since the raw bytes
are shown in the disassembly itself.


## Examples

```
python3 disass.py --input flt.prg --nocomments
```

Imports the file `flt.prg`, parses it without comments and writes the output assembly code as `flt.prg.asm` into the same directory.


```
python3 disass.py -i source/flt.prg -o code/flt.asm -e entrypoints.json 
```

Imports the file `flt.org` located in the `source` folder, parses it with comments and uses custom entrypoints defined in `entrypoints.json` and writes the output assembly code as `flt.asm` into the `code` folder.


```
cd example
python3 mkdemo.py
python3 ../disass.py -i demo.bin -o demo.asm -c demo.stats
```

Creates a binary image `demo.bin` corresponding to the final [blog post example](https://www.awsm.de/blog/pydisass/)
and then disassembles back to something close to the original.  The `demo.stats` report gives coverage
information on the code and data entrypoints:

```
[
    {"addr": "0823", "symbol": "__A__", "mode": "data", "loc": "internal", "count": 1},
    {"addr": "082f", "symbol": "__B__", "mode": "code", "loc": "internal", "count": 1}
]

```

which can be used to build a mapping file like `demo.map.json` adding symbols and comments via:

```
python3 ../disass.py -i demo.bin -o demo.asm -c demo.stats -e demo.map.json
```

## JSON files

`lib/opcodes.json`  
A description of all 256 opcodes that are available for the 6502 processor, including illegal opcodes. You can add more keys to the list if you know what you're doing, otherwise this one is better be left as is.

`lib/c64-mapping.json`  
A list of significant addresses for the C64, like `D020` for the border color. Can be extended to your personal liking. Also more mappings for other 6502 based computers (C16, C116, Plus/4, C128, VC20) could be added as separate files. In addition, language translations could be added. Happily taking Pull Requests.

`lib/atari-mapping.json`
A similar mapping file for the Atari platform.

`entrypoints.json`  
The optional `startaddress` gives the hex address for the offset of the input file in memory.
The `entrypoints` key contains a list of addresses that should be marked as code or data section and override any other setting.  Valuable if you know that a data section is code, or to peek into data sections and check if they are code. You can and should modify this file whenever you disassemble a file. Each records is a symbol object containing:

- `addr`: the memory location `hhll` for this annotation
- `symbol`: optional symbolic name for this memory location
- `mode`: interpret this location as either `data` or `code`
- `loc`: optionally specify either an `internal` or `external` reference (otherwise inferred by `addr`)
- `comm`: optional comment to show at this location, and wherever this symbol is referenced

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
export PATH=$PATH:/Users/username/pathto/folder
```

Make sure to adapt this line to your settings by replacing the `username` with your username and the `pathto/folder` with the right path to the location of the pydisass folder.

4. Rename `disass.py` to `disass` (optional)  
If you like it nice and short, you can drop the `.py` suffix as well

After restarting your terminal, you should be able to execute the disassembler from anywhere.





## ToDo

* external config file for multiple ass dialects
* cleanup code formatting
* improve data formatting
