import logging
import time

import anndata
import s3fs
from numpy import ndarray
from pandas import DataFrame
from scipy.sparse import spmatrix

from .utils.corpora_constants import CorporaConstants
from .utils.math_utils import sizeof_formatted


class DatasetValidator:
    """ Validates a dataset file that has been uploaded by a submitted to ensure that the correct required metadata
    has been inputted in the expected locations of the file (based on file type) and ensures that no PII exists in
    the dataset file."""

    def __init__(self, s3_uri):
        self.s3_uri = s3_uri
        self.s3_path = s3_uri.replace("s3://", "")
        self.s3_file_system = s3fs.S3FileSystem()

    def validate_dataset_file(self, loom_x_layer_name=None):
        """
        Reads in file object and triages for specific file type validation.
        """

        file_object = self.s3_file_system.open(self.s3_path, "rb")
        file_object_size = file_object.info().get("Size")
        logging.info(f"Validating file {self.s3_uri} with size {sizeof_formatted(file_object_size)}")

        if self.s3_path.endswith(CorporaConstants.H5AD_FILE_TYPE):
            self.validate_h5ad_dataset(file_object)

        elif self.s3_path.endswith(CorporaConstants.LOOM_FILE_TYPE):
            self.validate_loom_dataset(file_object, loom_x_layer_name)

        else:
            logging.warning(f"Unknown type of dataset with path {self.s3_path}!")

        file_object.close()

    def validate_h5ad_dataset(self, file_object):
        """
        Reads the H5AD file contents into an AnnData object. Each attribute of the AnnData object will then be
        checked to ensure it contains the appropriate metadata.
        """

        start_time = time.time()
        logging.info("Reading H5AD file into anndata object...")
        anndata_object = anndata.read_h5ad(file_object)
        logging.info(f"Finished reading anndata object in {time.time() - start_time:.3f} seconds.")

        self.validate_anndata_object(anndata_object)

    def validate_loom_dataset(self, file_object, loom_x_layer_name=None):
        """
        Reads the Loom file contents into an AnnData object. Each attribute of the AnnData object will then be
        checked to ensure it contains the appropriate metadata.
        """

        start_time = time.time()
        logging.info("Reading Loom file into anndata object...")
        if loom_x_layer_name:
            anndata_object = anndata.read_loom(file_object, X_name=loom_x_layer_name)
        else:
            anndata_object = anndata.read_loom(file_object)
        logging.info(f"Finished reading anndata object in {time.time() - start_time:.3f} seconds.")

        self.validate_anndata_object(anndata_object)

    def validate_anndata_object(self, anndata_object: anndata.AnnData):
        start_time = time.time()
        logging.info("Beginning validation of anndata object...")
        self.verify_layers(anndata_object)
        self.verify_obs(anndata_object)
        self.verify_vars(anndata_object)
        self.verify_uns(anndata_object)
        logging.info(f"Finished completing validation in {time.time() - start_time:.3f} seconds.")

    def verify_layers(self, data_object: anndata.AnnData):
        """
        Verifies that the dataset contains at least the raw data and if other layers are provided, that they each
        contain an appropriate description.
        """

        # Check to make sure X data exists
        has_data = True
        if isinstance(data_object.X, DataFrame):
            has_data = data_object.X.data.any()
        elif isinstance(data_object.X, ndarray):
            has_data = data_object.X.any()
        elif isinstance(data_object.X, spmatrix):
            has_data = (data_object.X.count_nonzero() == data_object.X.nnz) or data_object.X.nnz == 0
        else:
            logging.warning(
                f"Could not check X data layer to ensure that it exists. The type is " f"{type(data_object.X)}!"
            )

        if not has_data:
            logging.warning("No data in the X layer can be found in the dataset or all observations are zeros!")

        # Ensure that the layer_descriptions metadata key exists in the `uns` field of the anndata object.
        if (CorporaConstants.LAYER_DESCRIPTIONS not in data_object.uns_keys()) or (
            not data_object.uns.get(CorporaConstants.LAYER_DESCRIPTIONS)
        ):
            logging.warning("Required layers descriptions are missing from uns field to describe data layers!")
        else:
            # Check to ensure that there are descriptions for each layer
            for layer_name in data_object.layers.keys():
                if layer_name not in data_object.uns.get(CorporaConstants.LAYER_DESCRIPTIONS).keys():
                    logging.warning(f"Missing layer description for layer {layer_name}!")

            # Check to make sure that X has a layer description and if the anndata populate the `raw` field,
            # that a raw data layer description also exists.
            if (
                CorporaConstants.X_DATA_LAYER_NAME
                not in data_object.uns.get(CorporaConstants.LAYER_DESCRIPTIONS).keys()
            ):
                logging.warning(f"Missing layer description for layer {CorporaConstants.X_DATA_LAYER_NAME}!")
            if data_object.raw:
                if (
                    CorporaConstants.RAW_DATA_LAYER_NAME
                    not in data_object.uns.get(CorporaConstants.LAYER_DESCRIPTIONS).keys()
                ):
                    logging.warning(f"Missing layer description for layer {CorporaConstants.RAW_DATA_LAYER_NAME}!")

    def verify_obs(self, data_object: anndata.AnnData):
        """
        Validates the observation attribute of an AnnData object. Checks to ensure that all observation IDs are
        unique and that the observation metadata fields as described by the Corpora Schema exist. If the validation
        fails in any way, the errors are outputted rather than the validation aborted.
        """

        observation_keys = data_object.obs_keys()

        # Check to ensure that all IDs are unique
        if data_object.obs.index.duplicated().any():
            logging.warning("Each observation is not unique!")

        for metadata_field in (
            CorporaConstants.REQUIRED_OBSERVATION_METADATA_FIELDS
            + CorporaConstants.REQUIRED_OBSERVATION_ONTOLOGY_METADATA_FIELDS
        ):
            if metadata_field not in observation_keys:
                self.log_error_message(metadata_field, "obs", type(data_object).__name__)

    def verify_vars(self, data_object: anndata.AnnData):
        """
        Validates the variable attribute of the AnnData object to ensure that all variable IDs are unique.
        """

        if data_object.var.index.duplicated().any():
            logging.warning("Each variable is not unique!")

    def verify_uns(self, data_object: anndata.AnnData):
        """
        Validate the unstructured attribute of the AnnData object to ensure that it contains the appropriate
        dataset-level and project-level metadata and outputs which metadata fields are missing. Note that no
        exception is thrown when metadata is found to be missing and rather an informative message is outputted instead.
        """

        unstructured_metadata_keys = data_object.uns_keys()

        for metadata_field in (
            CorporaConstants.REQUIRED_DATASET_METADATA_FIELDS
            + CorporaConstants.REQUIRED_DATASET_PRESENTATION_METADATA_FIELDS
        ):
            if metadata_field not in unstructured_metadata_keys:
                self.log_error_message(metadata_field, "uns", type(data_object).__name__)

    def log_error_message(self, metadata_field_name, expected_location, dataset_type):
        """
        Pretty-printer of missing metadata fields errors.
        """

        is_ontology = " ontology " if "ONTOLOGY" in metadata_field_name else " "
        logging.warning(
            f"ERROR: Missing{is_ontology}metadata field {metadata_field_name} from {expected_location} in "
            f"{dataset_type} file!"
        )
