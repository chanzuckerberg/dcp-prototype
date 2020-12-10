import logging
import threading
import queue
import requests

from ..common.corpora_orm import DbDatasetProcessingStatus, UploadStatus
from ..common.entities import Dataset
from ..common.utils.db_utils import db_session_manager
from ..common.utils.math_utils import MB

logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, file_size: int):
        self.file_size: int = file_size
        self._progress: int = 0
        self.progress_lock: threading.Lock = threading.Lock()  # prevent concurrent access of _progress
        self.stop_updater: threading.Event = threading.Event()  # Stops the update_progress thread
        self.stop_uploader: threading.Event = threading.Event()  # Stops the uploader threads
        self.error: queue.Queue = queue.Queue(maxsize=1)  # Track errors

    def progress(self):
        with self.progress_lock:
            return self._progress / self.file_size

    def update(self, progress):
        with self.progress_lock:
            self._progress += progress


def uploader(url: str, local_path: str, tracker: ProgressTracker, chunk_size: int):
    """
    Upload the file pointed at by the URL to the local path.

    :param url: The URL of the file to be uploaded.
    :param local_path: The local name of the file be uploaded
    :param tracker: Tracks information about the progress of the upload.
    :return:
    """
    try:
        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            with open(local_path, "wb") as fp:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if tracker.stop_uploader.isSet():
                        logger.debug("Upload ended early!")
                        return
                    elif chunk:
                        fp.write(chunk)
                        chunk_size = len(chunk)
                        tracker.update(chunk_size)
                        logger.debug(f"chunk size: {chunk_size}")
    except requests.HTTPError as ex:
        tracker.error.put(ex)
    finally:
        tracker.stop_updater.set()


def processing_status_updater(uuid: str, updates: dict):
    with db_session_manager() as manager:
        manager.session.query(DbDatasetProcessingStatus).filter(DbDatasetProcessingStatus.id == uuid).update(updates)
        manager.session.commit()


def updater(upload_uuid: str, tracker: ProgressTracker, frequency: float = 3):
    """
    Update the progress of an upload to the database using the tracker.

    :param upload_uuid: The uuid of the upload_progress row.
    :param tracker: Tracks information about the progress of the upload.
    :param frequency: The frequency in which the database is updated
    :return:
    """

    def _update():
        progress = tracker.progress()
        if progress > 1:
            tracker.stop_uploader.set()
            processing_status = {
                DbDatasetProcessingStatus.upload_progress: progress,
                DbDatasetProcessingStatus.upload_message: "The file size, does not match the size of the upload.",
                DbDatasetProcessingStatus.upload_status: UploadStatus.FAILED,
            }
        elif progress == 1 and tracker.stop_updater.isSet():
            processing_status = {
                DbDatasetProcessingStatus.upload_progress: progress,
                DbDatasetProcessingStatus.upload_status: UploadStatus.UPLOADED,
            }
        else:
            processing_status = {DbDatasetProcessingStatus.upload_progress: progress}
        processing_status_updater(upload_uuid, processing_status)

    try:
        while not tracker.stop_updater.wait(frequency):
            _update()
        _update()  # Make sure the progress is update once the upload is complete
    finally:
        tracker.stop_uploader.set()


def upload(dataset_uuid: str, url: str, local_path: str, file_size: int, chunk_size: int = 10 * MB, update_frequency=3):
    """
    Upload a file from a url and update the processing_status upload fields in the database

    :param dataset_uuid: The uuid of the dataset the upload will be associated with.
    :param url: The URL of the file to be uploaded.
    :param local_path: The local name of the file be uploaded
    :param file_size: The size of the file in bytes.
    :param chunk_size: The size of downloaded data to copy to memory before saving to disk.
    """
    with db_session_manager() as mananger:
        processing_status = Dataset.get(dataset_uuid).processing_status
        processing_status.upload_status = UploadStatus.UPLOADING
        processing_status.upload_progress = 0
        mananger.commit()
        upload_uuid = processing_status.id
    progress_tracker = ProgressTracker(file_size)
    progress_thread = threading.Thread(
        target=updater,
        kwargs=dict(upload_uuid=upload_uuid, tracker=progress_tracker, frequency=update_frequency),
    )
    progress_thread.start()
    upload_thread = threading.Thread(
        target=uploader, kwargs=dict(url=url, local_path=local_path, tracker=progress_tracker, chunk_size=chunk_size)
    )
    upload_thread.start()
    upload_thread.join()
    progress_thread.join()
    try:
        error = progress_tracker.error.get(block=False)
    except queue.Empty:
        pass
    else:
        processing_status = {
            DbDatasetProcessingStatus.upload_status: UploadStatus.FAILED,
            DbDatasetProcessingStatus.upload_message: str(error),
        }
        processing_status_updater(upload_uuid, processing_status)
