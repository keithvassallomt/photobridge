import logging
import os
import pathlib
import shutil
from datetime import datetime

from photobridge import core as pb
import argparse

db_path = 'photobridge.db'
table_name = 'photobridge'
logger: logging.Logger | None = None


def setup_logging() -> logging.Logger:
    """
    Sets up the logging system.

    :return: the logging helper for the CLI.
    """

    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'critical': logging.CRITICAL
    }
    log_level = log_levels['debug']

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s: %(message)s',
    )

    # Log file
    log_folder = pathlib.Path.home() / "Library" / "Logs" / "PhotoBridge"
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = datetime.now().strftime("PhotoBridge_%Y%m%d-%H%M%S") + '.log'
    if log_file:
        logging.getLogger().addHandler(logging.FileHandler(log_folder / log_file))

    return logging.getLogger()


def do_sync(args: argparse.Namespace) -> bool:
    """
    Start the synchronisation process via the CLI.

    :param args: the arguments received from the command line
    :return: True if the operation requested succeeds
    """
    global db_path

    # Seed database
    success, data = pb.seed_database(db_path, table_name)
    if not success:
        logger.critical(data)
        return False
    logger.debug(data)

    # Get files in folder
    success, data = pb.get_media_in_path(args.photos_folder)
    if not success:
        logger.critical(data)
        return False
    logger.debug("Successfully retrieved list of files in source photos folder.")
    files_in_folder = data

    if args.dry_run:
        db_path = "photobridge_dryrun.db"
        shutil.copy('photobridge.db', 'photobridge_dryrun.db')

    # Sync new files with database and get list of new files
    success, data = pb.sync_files_with_database(files_in_folder, db_path, table_name)
    if not success:
        logger.critical(data)
        return False
    logger.debug("List of new files in source photos folder was detected.")
    new_files = data

    if args.dry_run:
        if len(new_files) > 0:
            print("DRY RUN: The following files would have been imported: {}".format(", ".join(new_files)))
        else:
            print("DRY RUN: No new files would have been imported.")
        os.remove('photobridge_dryrun.db')
        return True

    if not args.save_current_state and not args.dry_run:
        if len(new_files) == 0:
            logger.info("No new files to import.")
            return True

        # Ensure the PhotoBridge album exists
        success, data = pb.create_photobridge_album()
        if not success:
            logger.critical(data)
            return False
        logger.debug(data)

        # Save list of new files to temporary folder
        success, data = pb.create_import_list(new_files)
        if not success:
            logger.critical(data)
            return False
        logger.debug(data)

        # Import the photos
        success, data = pb.import_photos()
        if not success:
            logger.critical(data)
            return False
        logger.info(data)

    return True


def process_args(args: argparse.Namespace) -> bool:
    """
    Parse the received command-line arguments to determine what to do.
    :param args: arguments received via the command line
    :return: True if the requested operation succeeds
    """
    if args.reset_database:
        if os.path.exists('photobridge.db'):
            try:
                os.remove('photobridge.db')
            except PermissionError as e:
                logger.critical('Unable to delete internal database: {}'.format(e))
                return False
            logger.info('Database has been reset.')
        else:
            logger.info('No database to reset.')

    if hasattr(args, "photos_folder"):
        do_sync(args)

    return True


def main() -> None:
    """
    Define command-line arguments acceptable and check argument logic
    :return: None
    """
    parser = argparse.ArgumentParser(
        prog="PhotoBridge",
        description="Synchronise your photos to iCloud Photo Library.",
    )

    parser.add_argument(
        "--photos-folder",
        type=pathlib.Path,
        default=argparse.SUPPRESS,
        help="set the location of the folder containing the photos you wish to synchronise.")

    parser.add_argument(
        "--reset-database",
        action="store_true",
        help='reset the internal database of known photos.'
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help='show the actions PhotoBridge would take, without actually doing anything.'
    )

    parser.add_argument(
        "--save-current-state",
        action="store_true",
        help='save the current list of photos in the source folder as "known", so they are not imported next time. No import occurs.'
    )

    global logger
    logger = setup_logging()

    args = parser.parse_args()
    if args.save_current_state and not hasattr(args, 'photos_folder'):
        parser.error("--save-current-state requires --photos-folder to be specified.")
    elif args.dry_run and not hasattr(args, 'photos_folder'):
        parser.error("--dry-run requires --photos-folder to be specified.")
    elif not args.save_current_state and not args.dry_run and not args.reset_database and not hasattr(args, 'photos_folder'):
        parser.error("no action specified.")

    process_args(args)


if __name__ == "__main__":
    main()
