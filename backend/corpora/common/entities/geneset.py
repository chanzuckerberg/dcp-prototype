from backend.corpora.common.corpora_orm import DbGeneset, DbGenesetDatasetLink
from backend.corpora.common.entities.entity import Entity


class Geneset(Entity):
    table = DbGeneset

    @classmethod
    def create(cls, session, name: str, description: str, gene_symbols: object, dataset_ids: list = [], **kwargs):
        gene_set = DbGeneset(name=name, description=description, gene_symbols=gene_symbols, **kwargs)
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
            reshaped_genesets.append(geneset.to_dict(remove_attr="gene_symbols"))
        return reshaped_genesets



class GenesetDatasetLink(Entity):
    table = DbGenesetDatasetLink

    @classmethod
    def create(cls, session, geneset_id: str, dataset_id: str):
        link = DbGenesetDatasetLink(geneset_id=geneset_id, dataset_id=dataset_id)
        session.add(link)
        session.commit()
        return cls(link)
