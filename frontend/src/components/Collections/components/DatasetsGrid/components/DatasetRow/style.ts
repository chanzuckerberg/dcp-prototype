import { Classes } from "@blueprintjs/core";
import { GRAY, PT_GRID_SIZE_PX } from "src/components/common/theme";
import styled from "styled-components";

export const UploadStatusContainer = styled.div`
  color: ${GRAY.A} !important;
  display: flex;
  flex-direction: row;
  & > .${Classes.SPINNER} {
    margin-right: ${PT_GRID_SIZE_PX}px;
  }
`;

export const DatasetTitleCell = styled.td`
  vertical-align: middle !important;
`;

export const TitleContainer = styled.div`
  display: flex;
  flex-direction: row;
  & > .${Classes.CHECKBOX} {
    margin: 0 ${PT_GRID_SIZE_PX}px 0 0;
  }
`;
