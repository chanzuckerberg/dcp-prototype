export interface Project {
  // assays: string[];
  // biosample_categories: string[];
  // cell_count: number;
  // contributors: Contributor[];
  // cxg_enabled: boolean;
  // description: string;
  // diseases: string[];
  // id: string;
  // label: string;
  // organs: string[];
  // paired_end: string[];
  // publication_title: string;
  // species: string[];
  // name: string;
  // owner: {
  //   id: string;
  //   email: string;
  // };
  // status: string;
  // processing_state: string;
  // s3_bucket_key: string;
  // validation_state: string;
  // links: { url: string; type: string }[];
  // attestation: {
  //   needed: boolean;
  //   tc_uri: string;
  // };
  datasets: Dataset[];
  links: { name: string; url: string }[];
}

export interface Dataset {
  id: string;
  // assay: string;
  // assay_ontology: string;
  // tissue: string;
  // tissue_ontology: string;
  // disease_state: string;
  // disease_state_ontology: string;
  // sex: string;
  // ethnicity: string;
  // ethnicity_ontology: string;
  // organism: string;
  // organism_ontology: string;
  name: string;
  // source_data_location: string;
  // revision: number;
  // dataset_deployments: { id: string; environment: string; link: string }[];
  dataset_assets: DatasetAsset[];
  // contributors: Contributor[];
  // preprint_doi: DOI;
  // publication_doi: DOI;
}

export enum DATASET_ASSET_FORMAT {
  H5AD = "H5AD",
  RDS = "RDS",
  LOOM = "LOOM",
  CXG = "CXG",
}

export enum DATASET_ASSET_TYPE {
  REMIX = "REMIX",
  ORIGINAL = "ORIGINAL",
}

export interface DatasetAsset {
  id: string;
  format: DATASET_ASSET_FORMAT;
  file_name: string;
  type: DATASET_ASSET_TYPE;
  s3_uri: string;
}

// interface Contributor {
//   id: string;
//   name: string;
//   email: string;
//   institution: string;
// }

// interface DOI {
//   id: string;
//   title: string;
//   data: string;
//   journal: string;
// }

export interface User {
  picture: string;
}
