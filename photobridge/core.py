import csv
import os
import sqlite3
from typing import List

from photobridge import helpers, apple_scripts

# Define allowed image and video extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".cr2", ".nef"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"}

# Database settings
DB_NAME = "photobridge.db"
DB_TABLE_NAME = "photobridge"


def get_media_in_path(path: str) -> tuple[bool, List[str]] | tuple[bool, str]:
    """
    Returns a list of all media in the given canonical path.

    :param path: the canonical path to search for files.

    :returns:

            -success (:py:class:`bool`) - True if files from path are successfully retrieved

            -data (:py:class:`str` | :py:class`list`) - error message on failure, or list of all media in path.
    """
    if not os.path.exists(path):
        return False, f"The path '{path}' does not exist."
    if not os.path.isdir(path):
        return False, f"The path '{path}' is not a directory."

    # Get a list of all media in the directory
    media_files = []
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS:
                media_files.append(file_path)

    return True, media_files


def sync_files_with_database(file_list: List[str], db_name: str = DB_NAME, table_name: str = DB_TABLE_NAME) -> tuple[bool, List[str]] | tuple[bool, str]:
    """
    Synchronises the given list of file names with an SQLite database table.

    :param file_list: file names to check against the database.
    :param db_name: name of the SQLite database file.
    :param table_name: name of the table to store file names.

    :returns:

            -success (:py:class:`bool`) - True if files are successfully synchronised with database.

            -data (:py:class:`str` | :py:class`list`) - error message on failure, or list of all new files added.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(helpers.data_location() / db_name)
        cursor = conn.cursor()

        # Ensure the table exists
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL
            )
            """)

        # Retrieve existing filenames from the database
        cursor.execute(f"SELECT filename FROM {table_name}")
        existing_files = set(row[0] for row in cursor.fetchall())

        # Identify files not in the database
        new_files = [file for file in file_list if file not in existing_files]

        # Add new files to the database
        for file in new_files:
            cursor.execute(f"INSERT INTO {table_name} (filename) VALUES (?)", (file,))

        # Commit changes and close the connection
        conn.commit()
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if 'conn' in locals():
            # noinspection PyUnboundLocalVariable
            conn.close()

    return True, new_files


def seed_database(db_name: str = DB_NAME, table_name: str = DB_TABLE_NAME) -> tuple[bool, str]:
    """
    Seeds the SQLite database with the specified table if it doesn't already exist.

    :param db_name: name of the SQLite database file.
    :param table_name: name of the table to be created and seeded.

    :returns:

            -success (:py:class:`bool`) - True if the database is successfully seeded.

            -data (:py:class:`str`) - error message on failure, or success message.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(helpers.data_location() / db_name)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL
        )
        """)

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        return True, "Database seeding succeeded."
    except sqlite3.Error as e:
        return False, str(e)


def create_photobridge_album() -> tuple[bool, str]:
    """
    Ensures the PhotoBridge album exists in Photos.

    :returns:

            -success (:py:class:`bool`) - True if album already exists or is created successfully.

            -data (:py:class:`str`) - error message on failure, or success message.
    """

    # Get list of albums from Photos
    get_albums_script = apple_scripts.get_albums_script
    return_code, stdout, stderr = helpers.run_applescript(get_albums_script)
    if return_code != 0:
        return False, stderr

    # Check if PhotoBridge album exists
    current_albums = list(csv.reader([stdout.strip()]))[0]
    if 'PhotoBridge' in current_albums:
        return True, 'PhotoBridge album already exists.'

    # Create PhotoBridge album
    create_photobridge_album_script = apple_scripts.create_photobridge_album_script
    return_code, stdout, stderr = helpers.run_applescript(create_photobridge_album_script)
    if return_code != 0:
        return False, stderr

    return True, 'PhotoBridge album created.'

def create_import_list(list_of_files: List[str]) -> tuple[bool, str]:
    """
    Export a list of files to be imported into Photos, as a plain text file.

    :param list_of_files: list of files to stage for importing into Photos

    :returns:

            -success (:py:class:`bool`) - True if import list is successfully created.

            -data (:py:class:`str`) - error message on failure, or success message.
    """
    try:
        temp_file_name = helpers.temp_folder() / "import_list.csv"
        with open(temp_file_name, 'w') as fp:
            fp.write("\n".join(list_of_files))
    except (IOError, OSError) as e:
        return False, str(e)
    return True, "Photo import list created."


def import_photos() -> tuple[bool, str]:
    """
    Import the photos previously staged into Photos.

    :returns:

            -success (:py:class:`bool`) - True if photos are successfully synchronised.

            -data (:py:class:`str`) - error message on failure, or success message.
    """
    import_list = helpers.temp_folder() / "import_list.csv"
    import_photos_script = apple_scripts.import_photos_script
    return_code, stdout, stderr = helpers.run_applescript(import_photos_script, import_list)
    if return_code != 0:
        return False, stderr
    return True, 'Photos imported.'
