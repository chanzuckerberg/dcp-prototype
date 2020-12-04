import os
import unittest
from unittest.mock import patch

import anndata
import numpy
import pandas

from backend.corpora.dataset_processing import process


class TestDatasetProcessing(unittest.TestCase):
    @patch.dict(
        os.environ, {"DROPBOX_URL": "xxx", "ARTIFACT_BUCKET": "yyy", "CELLXGENE_BUCKET": "zzz", "DATASET_ID": "aaa"}
    )
    def test_check_env_good(self):
        process.check_env()

    @patch.dict(os.environ, {"DROPBOX_URL": "xxx", "ARTIFACT_BUCKET": "yyy", "CELLXGENE_BUCKET": "zzz"})
    def test_check_env_bad(self):
        with self.assertRaises(EnvironmentError):
            process.check_env()

    @patch("scanpy.read_h5ad")
    def test_extract_metadata(self, mock_read_h5ad):

        df = pandas.DataFrame(
            numpy.random.randint(10, size=(50001, 5)) * 50, columns=list("ABCDE"), index=(str(i) for i in range(50001))
        )

        obs = pandas.DataFrame(
            numpy.hstack(
                [
                    numpy.random.choice(["lung", "liver"], size=(50001, 1)),
                    numpy.random.choice(["10x", "smartseq", "cite-seq"], size=(50001, 1)),
                    numpy.random.choice(["healthy"], size=(50001, 1)),
                    numpy.random.choice(["male", "female"], size=(50001, 1)),
                    numpy.random.choice(["solomon islander", "orcadian"], size=(50001, 1)),
                    numpy.random.choice(["adult", "baby", "tween"], size=(50001, 1)),
                ]
            ),
            columns=["tissue", "assay", "disease", "sex", "ethnicity", "development_stage"],
            index=(str(i) for i in range(50001)),
        )
        uns = {"organism": "Homo sapiens", "layer_descriptions": {"X": "raw"}}

        adata = anndata.AnnData(X=df, obs=obs, uns=uns)

        mock_read_h5ad.return_value = adata

        extracted_metadata = process.extract_metadata("dummy")

        self.assertEqual(extracted_metadata["organism"], "Homo sapiens")
        self.assertListEqual(sorted(extracted_metadata["tissue"]), sorted(["lung", "liver"]))
        self.assertListEqual(sorted(extracted_metadata["assay"]), sorted(["10x", "smartseq", "cite-seq"]))
        self.assertListEqual(sorted(extracted_metadata["disease"]), sorted(["healthy"]))
        self.assertListEqual(sorted(extracted_metadata["sex"]), sorted(["male", "female"]))
        self.assertListEqual(sorted(extracted_metadata["ethnicity"]), sorted(["solomon islander", "orcadian"]))
        self.assertListEqual(sorted(extracted_metadata["development_stage"]), sorted(["adult", "baby", "tween"]))
        self.assertEqual(extracted_metadata["cell_count"], 50001)
        self.assertAlmostEqual(extracted_metadata["mean_genes_per_cell"], numpy.count_nonzero(df) / 50001)
