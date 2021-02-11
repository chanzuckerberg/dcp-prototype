from flask import make_response, jsonify, g

from ....common.corpora_orm import CollectionVisibility
from ....common.entities import Dataset, Collection
from ....common.utils.exceptions import (
    NotFoundHTTPException,
    ServerErrorHTTPException,
    ForbiddenHTTPException,
)


def post_dataset_asset(dataset_uuid: str, asset_uuid: str):
    db_session = g.db_session
    # retrieve the dataset
    dataset = Dataset.get(db_session, dataset_uuid)
    if not dataset:
        raise NotFoundHTTPException(f"'dataset/{dataset_uuid}' not found.")

    # retrieve the artifact
    asset = dataset.get_asset(asset_uuid)
    if not asset:
        raise NotFoundHTTPException(f"'dataset/{dataset_uuid}/asset/{asset_uuid}' not found.")

    # Retrieve S3 metadata
    file_size = asset.get_file_size()
    if not file_size:
        raise ServerErrorHTTPException()

    # Generate pre-signed URL
    presigned_url = asset.generate_file_url()
    if not presigned_url:
        raise ServerErrorHTTPException()

    return make_response(
        jsonify(
            dataset_id=dataset_uuid,
            file_name=asset.filename,
            file_size=file_size,
            presigned_url=presigned_url,
        ),
        200,
    )


def get_status(dataset_uuid: str, user: str):
    db_session = g.db_session
    dataset = Dataset.get(db_session, dataset_uuid)
    if not dataset:
        raise ForbiddenHTTPException()
    if not Collection.if_owner(db_session, dataset.collection.id, dataset.collection.visibility, user):
        raise ForbiddenHTTPException()
    status = dataset.processing_status.to_dict(remove_none=True)
    for remove in ["dataset", "created_at", "updated_at"]:
        status.pop(remove)
    return make_response(jsonify(status), 200)


def delete_dataset(dataset_uuid: str, user: str):
    """
    Deletes an existing dataset or cancels an in progress upload.
    """
    db_session = g.db_session
    dataset = Dataset.get(dataset_uuid, include_tombstones=True)
    if not dataset:
        raise ForbiddenHTTPException()
    if not Collection.if_owner(db_session, dataset.collection.id, dataset.collection.visibility, user):
        raise ForbiddenHTTPException()
    if dataset.collection_visibility == CollectionVisibility.PUBLIC:
        return make_response(jsonify("Can not delete a public dataset"), 405)
    if dataset.tombstone is False:
        dataset.dataset_and_asset_deletion()
    return "", 202
