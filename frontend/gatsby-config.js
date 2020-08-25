module.exports = {
  // (thuang): Prod build will serve static assets from this directory
  // E.g., cellxgene.cziscience.com/dp/foo.js
  assetPrefix: "/dp",
  plugins: [
    "gatsby-plugin-typescript",
    "gatsby-plugin-react-helmet",
    "gatsby-plugin-root-import",
    "gatsby-plugin-styled-components",
    {
      resolve: "gatsby-plugin-asset-path",
    },
    {
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
      resolve: `gatsby-source-filesystem`,
    },
    `gatsby-plugin-theme-ui`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      options: {
        display: `minimal-ui`, // icon: `src/images/gatsby-icon.png`, // This path is relative to the root of the site.
        name: `gatsby-starter-default`,
        // eslint-disable-next-line @typescript-eslint/camelcase
        short_name: `starter`,
        // eslint-disable-next-line @typescript-eslint/camelcase
        start_url: `/`,
      },
      resolve: `gatsby-plugin-manifest`,
    },
  ],
  siteMetadata: {
    author: `Chan Zuckerberg Initiative`,
    description: `
    The cellxgene data portal is a repository of public, explorable single-cell datasets.
    If you have a public dataset which you would like hosted for visualization on this site, please drop us a note at cellxgene@chanzuckerberg.com.
    `,
    title: `cellxgene`,
  },
};
