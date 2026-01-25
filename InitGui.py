# -*- coding: utf-8 -*-

__title__ = "easyText"
__author__ = "Lisa Erlingheuser"
__doc__ = "Workbench easyText"
__version__ = "0.0.1"


class easyTextWorkbench(Workbench):
    def __init__(self):
        import os
        import easyText
        self.__class__.MenuText = "easyText"
        self.__class__.ToolTip = "Textstrings based on Qt"
        self.__class__.Icon = os.path.join(easyText.get_module_path(), "Icons", "easyText.svg")

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        # import here all the needed files that create your FreeCAD commands
        import easyTextString
        import easyTextGlyphs
        import easyTextAlongPath
        import easyTextRevolve
        
        self.list = ["easyTextString", "easyTextGlyphs", "easyTextAlongPath", "easyTextRevolve"] # A list of command names created in the line above
        self.appendToolbar("easyTextWorkbench", self.list) # creates a new toolbar with your commands
        self.appendMenu("easyTextWorkbench", self.list) # creates a new menu

    def Activated(self):
        "This function is executed when the workbench is activated"
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu(self.__class__.MenuText, self.list) # add commands to the context menu

    def GetClassName(self): 
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"
    
       
Gui.addWorkbench(easyTextWorkbench())

