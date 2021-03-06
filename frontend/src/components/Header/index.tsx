import { Intent } from "@blueprintjs/core";
import Link from "next/link";
import React, { FC } from "react";
import { ROUTES } from "src/common/constants/routes";
import { get } from "src/common/featureFlags";
import { FEATURES } from "src/common/featureFlags/features";
import { BOOLEAN } from "src/common/localStorage/set";
import { useUserInfo } from "src/common/queries/auth";
import { HomepageLink } from "../common/HomepageLink";
import AuthButtons from "./components/AuthButtons";
import { MainWrapper, MyCollectionsButton, Right, Wrapper } from "./style";

const Header: FC = () => {
  // (thuang): FEATURES.AUTH and FEATURES.CREATE_COLLECTION are being deprecated
  const isAuth = get(FEATURES.AUTH) === BOOLEAN.TRUE;
  const isCurator = get(FEATURES.CURATOR) === BOOLEAN.TRUE;
  const isCreateCollection = get(FEATURES.CREATE_COLLECTION) === BOOLEAN.TRUE;

  const { data: userInfo } = useUserInfo(isAuth || isCurator);

  const isMyCollectionsShown =
    userInfo?.name && (isCreateCollection || isCurator);

  return (
    <Wrapper>
      <MainWrapper>
        <HomepageLink />
        <Right>
          {isMyCollectionsShown && (
            <Link href={ROUTES.MY_COLLECTIONS} passHref>
              <a href="passHref">
                <MyCollectionsButton intent={Intent.PRIMARY} minimal>
                  My Collections
                </MyCollectionsButton>
              </a>
            </Link>
          )}
          <AuthButtons />
        </Right>
      </MainWrapper>
    </Wrapper>
  );
};

export default Header;
