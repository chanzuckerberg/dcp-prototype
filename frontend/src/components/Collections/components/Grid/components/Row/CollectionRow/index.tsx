import { Button, Intent, Tag } from "@blueprintjs/core";
import loadable from "@loadable/component";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { FC } from "react";
import { ROUTES } from "src/common/constants/routes";
import {
  ACCESS_TYPE,
  COLLECTION_LINK_TYPE,
  VISIBILITY_TYPE,
} from "src/common/entities";
import {
  useCollection,
  useCreateRevision,
} from "src/common/queries/collections";
import { aggregateDatasetsMetadata } from "../../../common/utils";
import {
  LeftAlignedDetailsCell,
  RightAlignedDetailsCell,
  StyledCell,
  StyledRow,
  TagContainer,
} from "../common/style";
import { CollectionTitleText } from "./style";

interface Props {
  id: string;
  accessType?: ACCESS_TYPE;
  visibility: VISIBILITY_TYPE;
  hasRevision?: boolean;
}

const AsyncPopover = loadable(
  () =>
    /*webpackChunkName: 'CollectionRow/components/Popover' */ import(
      "src/components/Collections/components/Grid/components/Popover"
    )
);

const conditionalPopover = (values: string[]) => {
  if (!values || values.length === 0) {
    return <LeftAlignedDetailsCell>-</LeftAlignedDetailsCell>;
  }

  return <AsyncPopover values={values} />;
};

type DOI = {
  doi: string;
  link: string;
};

const CollectionRow: FC<Props> = (props) => {
  const { data: collection } = useCollection({
    id: props.id,
    visibility: props.visibility,
  });
  const router = useRouter();
  const navigateToRevision = () => {
    router.push(ROUTES.PRIVATE_COLLECTION.replace(":id", id));
  };
  const [mutate] = useCreateRevision(navigateToRevision);

  const handleRevisionClick = () => {
    if (!props.hasRevision) {
      mutate(id);
    } else {
      navigateToRevision();
    }
  };

  if (!collection) return null;

  // If there is an explicity accessType only show collections with that accessType
  if (props.accessType && collection.access_type !== props.accessType) {
    return null;
  }

  const { id, links, visibility, name, datasets } = collection;

  // todo(1109): port path grabbing over to collection
  const dois: Array<DOI> = links.reduce((acc, link) => {
    if (link.link_type !== COLLECTION_LINK_TYPE.DOI) return acc;

    const url = new URL(link.link_url);

    acc.push({ doi: url.pathname.substring(1), link: link.link_url });

    return acc;
  }, [] as DOI[]);

  const isPrivate = visibility === VISIBILITY_TYPE.PRIVATE;

  const {
    tissue,
    assay,
    disease,
    organism,
    cell_count,
  } = aggregateDatasetsMetadata(datasets);

  return (
    <StyledRow>
      <StyledCell>
        <Link
          href={`/collections/${id}${isPrivate ? "/private" : ""}`}
          passHref
        >
          <CollectionTitleText data-test-id="collection-link" href="passHref">
            {name}
          </CollectionTitleText>
        </Link>

        {props.accessType === ACCESS_TYPE.WRITE && (
          <TagContainer>
            <Tag
              minimal
              intent={isPrivate ? Intent.PRIMARY : Intent.SUCCESS}
              data-test-id="visibility-tag"
            >
              {isPrivate ? "Private" : "Published"}
            </Tag>
            {props.hasRevision && (
              <Tag minimal intent={Intent.PRIMARY}>
                Revision Pending
              </Tag>
            )}
          </TagContainer>
        )}
      </StyledCell>
      {conditionalPopover(tissue)}
      {conditionalPopover(assay)}
      {conditionalPopover(disease)}
      {conditionalPopover(organism)}
      <RightAlignedDetailsCell>{cell_count || "-"}</RightAlignedDetailsCell>
      {typeof props.hasRevision !== "undefined" && !isPrivate && (
        <RevisionCell
          hasRevision={props.hasRevision}
          handleRevisionClick={handleRevisionClick}
        />
      )}
    </StyledRow>
  );
};

const RevisionCell = ({
  hasRevision,
  handleRevisionClick,
}: {
  hasRevision?: boolean;
  handleRevisionClick: () => void;
}) => {
  return (
    <RightAlignedDetailsCell>
      <Button intent={Intent.PRIMARY} minimal onClick={handleRevisionClick}>
        {hasRevision ? "Continue" : "Start Revision"}
      </Button>
    </RightAlignedDetailsCell>
  );
};

export default CollectionRow;
