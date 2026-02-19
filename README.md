# <img src="./Icons/easyText.svg"> easyText
Python Workbench for Textshapes in FreeCAD

## Python Workbench for Textshapes 

This is a Python workbench for FreeCAD, designed to test an alternative method of text creation that is easier for the user.

easyText generates the text string requested by the user using QT /QPainterPath and then generates FreeCAD Wires from it (and possibly FreeCAD Shapes based on them).

This approach allows the use of Qt's font management system, which provides access to all installed fonts of the operating system without needing to know the physical location of the font's TTF file.

## Technical implementation of easyText shapes

### easyTextString 
This is a simple conversion of the paths provided by QPainterPath into wires. This is the faster method, and formatting options such as strikethrough, underlining, and strikethrough are also available. The individual elements of the PainterPath are represented as a compound.

### easyTextGlyph 
The text is again created as a compound based on the paths provided by QPainterPath. However, the compound consists of subshapes, each corresponding to a letter and itself composed of one or more wires. This allows for the creation of further features based on individual letters.

## Important Notes  
The Workbench is experimental and should not be used for serious projects.
  
## Installation
Extract the downloaded ZIP file into the FreeCAD User Mod directory as "easyText". After the next start of FreeCAD, "easyText" should appear in the list of workbenches.

## Documentation
The easyText workbench documentation can be found on the [Github wiki](https://github.com/LisaErl/easyText/wiki).
  
## License
GNU Lesser General Public License v3.0
