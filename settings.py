import os

creator_name = 'Quietbird'

# Change to the location where you install your Mods at.
if os.name == 'posix':
    os_home_prefix = os.environ['HOME']
else:
    os_home_prefix = '~'
mods_folder = os.path.join(os_home_prefix,
                           'Games', 'origin', 'drive_c', 'users', 'YOUR_WINE_PROFILE',
                           'My Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
# Change to the location where you have installed The Sims 4 at,
# this would be the folder that contains the GameVersion.txt file
if os.name == 'posix':
    game_folder = os.path.join(os_home_prefix,
                               'Games', 'origin', 'drive_c', 'Program Files (x86)', 'Origin Games', 'The Sims 4')
else:
    game_folder = os.path.join('E:', os.sep, 'Program Files (x86)', 'Origin Games', 'The Sims 4')

# Set to either 'unpyc3' or 'py37dec' (py37dec is default; if it fails to decompile some files, change this to 'unpyc3')
compiler_name = 'py37dec'

# If you want to decompile the EA Python Scripts:
# 1. Change include_ea_decompile to True
# 2. Create a folder in your project with the name EA. i.e. <Project>/EA
# 2. Run the decompile_all.py script
# 3. It will decompile the EA scripts and put them inside of the folder: <Project>/EA/...
# 4. Inside of the <Project>/EA folder, you should see four folders (base, core, generated, simulation)
# 5. Highlight all four of those folders and right click them. Then do Mark Directory as... Sources Root
# 6. Delete the <Project>/EA/core/enum.py file because it
# causes issues when attempting to compile the scripts of your own mod.
include_ea_decompile = False

# If you want to decompile scripts from another authors mod
# 1. Create a folder in your project with the name decompiled. i.e. <Project>/decompiled
# 1. Put the script files (.pyc) of the mod you wish to decompile, inside of the "decompiled" folder.
# (Every ts4script file is a zip file and can be opened like one!)
# 2. Change include_decompile_dir to True
# 3. Run the decompile_all.py script
# 4. It will decompile the custom scripts and put them inside of the folder: <Project>/decompiled/...
include_decompile_dir = True
if include_ea_decompile:
    compiler_name = 'unpyc3'
    include_decompile_dir = False

decompile_src = './decompiled'
decompile_destination = './decompiled'
