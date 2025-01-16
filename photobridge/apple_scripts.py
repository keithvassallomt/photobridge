#: Get list of photo albums from Photos
get_albums_script = """tell application "Photos"
set albumList to name of albums
return albumList
end tell
"""

#: Create the PhotoBridge album in Photos
create_photobridge_album_script = """tell application "Photos"
make new album named "PhotoBridge"
end tell
"""

#: Import the list of staged files into Photos
import_photos_script = """on run argv
set importFilePath to item 1 of argv

-- Load list of files from staging
set fileContent to read POSIX file importFilePath
set AppleScript's text item delimiters to linefeed
set fileLines to text items of fileContent
set fileList to {}
repeat with aLine in fileLines
    set end of fileList to POSIX file aLine
end repeat

-- Import new files
set filteredFileList to {}
tell application "Photos"
    set pbAlbum to album "PhotoBridge"
    set albumPictureNames to filename of media items of pbAlbum
    repeat with anAlias in fileList
        tell application "Finder" to set pictureName to name of file anAlias
        if not (pictureName is in albumPictureNames) then set end of filteredFileList to contents of anAlias
    end repeat
    if filteredFileList is not {} then import filteredFileList into pbAlbum with skip check duplicates
end tell
end run
"""