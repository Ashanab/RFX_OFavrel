# RFX_OFavrel

Houdini Start Folder:

This Repo is not really usefull. It's just simple folders, desktop files, Shelf_set, Vex presets, Scripts, Prefs files etc ...
They've been created to better fit the way I like to work in Houdini, and so that I have a way to do some versioning and sharing...
If it's some use for you well. That's cool.

Basically you just need to set your  $HOME/houdini16.*/houdini.env  so that this folder is included in $HOUDINI_PATH so that
the Hda, Destop, Script, etc are scanned at the startup of Houdini.

you can do this like so:



# Example:

# HOUDINI PATH
HOUDINIPATH =  Mydrive:\..\..\yourRepoFolderName;&



Let's say that you need to scan several folder..


# WITH SEVERAL FOLDER:
FOO = MyDrive:\..\..\..\..

HOUDINI_PATH =  Mydrive:\..\..\yourRepoFolderName;$FOO;&


