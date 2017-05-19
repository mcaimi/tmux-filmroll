# **tmux-filmroll** #

This is a small integration plugin for TMUX that transfers photos from an external source (such as an SD Card from a DSLR) to a work path on your laptop, 
in order to be further processed (with Darktable or similar software).

Photos are sorted by creation time, and saved in a directory tree in the destination folder with this structure:

    DESTINATION PATH
      \
      YEAR
        \
        MONTH
          \
          DAY
            \
            <file type: RAW or JPEG>

Furthermore, JPEG and RAW files are kept apart from each other. 
Photo creation times are read from the EXIF metatata headers if present, otherwise the last modification time from the stat() syscall is used as timestamp.

The plugin consists of:

 1. a bash script bound to the 'f' key in tmux that fires up the plugin
 2. a python script that does all the transferring work


## Configuration ##

After installing the plugin you only need to set the source and destination path parameters in tmux.conf:

    # filmroll source path (SD card mount point, Compact Flash, ecc..)
    set -g @filmroll_source_path '/run/media/user/CANON/'
    # filmroll destination path
    set -g @filmroll_destination_path '/home/user/photoarchive/'


## Installation ##

To install the plugin, use tmux-plugins/tpm:

    set -g @plugins 'mcaimi/tmux-filmroll'

you also need both python3 and exiv2 packages installed.

