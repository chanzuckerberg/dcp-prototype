import csv
import typing
from sqlalchemy.exc import SQLAlchemyError

from ..corpora_orm import DbGeneset, DbGenesetDatasetLink
from .entity import Entity
from ..utils.exceptions import CorporaException


class Geneset(Entity):
    table = DbGeneset

    @classmethod
    def create(cls, session, name: str, description: str, genes: list, dataset_ids: list = [], **kwargs):
        gene_set = DbGeneset(name=name, description=description, genes=genes, **kwargs)
        session.add(gene_set)
        session.commit()
        if dataset_ids:
            for dataset_id in dataset_ids:
                GenesetDatasetLink.create(session, geneset_id=gene_set.id, dataset_id=dataset_id)
        return cls(gene_set)

    @classmethod
    def retrieve_all_genesets_for_a_collection(cls, session, collection_id):
        genesets = session.query(cls.table).filter(cls.table.collection_id == collection_id).all()
        reshaped_genesets = []
        for geneset in genesets:
            reshaped_genesets.append(
                geneset.to_dict(
                    remove_attr=[
                        "genes",
                        "created_at",
                        "updated_at",
                        "collection",
                        "collection_id",
                        "collection_visibility",
                    ]
                )
            )
        return reshaped_genesets

    @classmethod
    def generate_tidy_csv(cls, session, geneset_ids: list, s3_uri: str):
        headers = "GENE_SET_NAME,GENE_SET_DESCRIPTION,GENE_SYMBOL,GENE_DESCRIPTION,"
        n = 1
        for x in something:
            headers += f"PROVENANCE{n}, PROVENANCE{n}_DESCRIPTION"
            n+=1
        # w = csv.writer(sys.stderr)
        for id in geneset_ids:
            geneset = Geneset.get(session, id)
            geneset_row = geneset.geneset_to_csv_row()
            if len(geneset.genes)
        with open('mycsvfile.csv', 'wb') as f:
            w = csv.writer(f)
            w.writerow(somedict.keys())
            w.writerow(somedict.values())



    def geneset_to_csv_row(self):
        return ""


class GenesetDatasetLink(Entity):
    table = DbGenesetDatasetLink

    @classmethod
    def create(cls, session, geneset_id: str, dataset_id: str):
        link = DbGenesetDatasetLink(geneset_id=geneset_id, dataset_id=dataset_id)
        session.add(link)
        session.commit()
        return cls(link)

    @classmethod
    def get(cls, session, geneset_id: str, dataset_id: str):
        link = (
            session.query(cls.table)
            .filter(cls.table.geneset_id == geneset_id, cls.table.dataset_id == dataset_id)
            .one_or_none()
        )
        if link:
            return cls(link)
        else:
            return None

    @classmethod
    def update_links_for_a_dataset(
        cls, session, dataset_id: str, add: typing.Optional[list] = None, remove: typing.Optional[list] = None
    ):
        for gene_set_id in remove:
            link = cls.get(session=session, dataset_id=dataset_id, geneset_id=gene_set_id)
            if link is None:
                session.rollback()
                raise CorporaException()
            session.delete(link)
        try:
            for geneset_id in add:
                session.add(DbGenesetDatasetLink(geneset_id=geneset_id, dataset_id=dataset_id))
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise CorporaException
