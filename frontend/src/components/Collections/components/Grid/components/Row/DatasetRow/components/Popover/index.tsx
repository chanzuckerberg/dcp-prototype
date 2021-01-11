import loadable from "@loadable/component";
import React, { FC } from "react";
import { LeftAlignedDetailsCell } from "../../../common/style";
import { Skeleton } from "../common/Skeleton";

const AsyncPopover = loadable(
  () =>
    /*webpackChunkName: 'CollectionRow/components/Popover' */ import(
      "src/components/Collections/components/Grid/components/Popover"
    )
);

interface Props {
  values: string[];
  isLoading: boolean;
  isFailed: boolean;
}

const Popover: FC<Props> = ({ values, isLoading, isFailed }) => {
  if (isLoading) {
    return (
      <td>
        <Skeleton />
      </td>
    );
  }

  if (isFailed || !values || values.length === 0) {
    return <LeftAlignedDetailsCell>-</LeftAlignedDetailsCell>;
  }

  return <AsyncPopover values={values} />;
};

export default Popover;
