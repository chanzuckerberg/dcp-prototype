import React, { FC } from "react";
import questionMarkSvg from "src/components/ProjectList/components/Heading/questionMark.svg";
import { Info, Name, QuestionMark, View, Wrapper } from "./style";

const TOOLTIP_MESSAGE = `cellxgene augments datasets with a minimal set of metadata fields designed to enable comparisons across datasets. In cases where these columns conflict with author's metadata, the author's columns are prefixed by "original_"`;

const Heading: FC = () => {
  return (
    <Wrapper>
      <Name>Name of dataset</Name>
      <View>
        View dataset in cellxgene
        <span title={TOOLTIP_MESSAGE}>
          <QuestionMark src={questionMarkSvg} alt="question mark" />
        </span>
      </View>
      <Info>More information</Info>
    </Wrapper>
  );
};

export default Heading;
