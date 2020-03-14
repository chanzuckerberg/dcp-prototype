import React, { useState, useEffect } from "react"
import { useAuth0 } from "../contexts/auth0Context"
import Layout from "../components/layout"
import SEO from "../components/seo"
import searchStringAsObj from "../util/searchStringAsObj"
import ProjectOverview from "../components/projectOverview"
import { api_prefix } from "../globals"
import { Flex, Box, Heading } from "theme-ui"
import Authenticate from "../components/authenticate"

const SecondPage = props => {
  const [project, setProject] = useState(null)
  const [files, setFiles] = useState(null)
  const searchObj = searchStringAsObj(props.location.search.slice(1))
  const id = searchObj?.id
  const { loading, isAuthenticated, getTokenSilently } = useAuth0()

  useEffect(() => {
    if (id) {
      fetch(`${api_prefix}/projects/${id}`)
        .then(response => response.json()) // parse JSON from request
        .then(resultData => {
          setProject(resultData)
        })
    } else {
      return null
    }
  }, [id]) /* don't rerender if this hasn't changed */

  useEffect(() => {
    if (id && !loading && isAuthenticated) {
      // TODO send authorization token in requests to backend
      getTokenSilently().then(accessToken =>
        fetch(`${api_prefix}/projects/${id}/files`)
          .then(response => response.json()) // parse JSON from request
          .then(resultData => {
            setFiles(resultData)
          }))
    } else {
      return null
    }
  }, [id, isAuthenticated]) /* don't rerender if this hasn't changed */

  /*
    /projects/id
    /projects/id/files
    /files/id
  */

  return (
    <Layout>
      <SEO title="Projects"/>
      <Heading as="h1" sx={{ mb: 4 }}>
        Explore Project
      </Heading>
      <Flex>
        {!project ? (
          "Loading project..."
        ) : (
          <ProjectOverview project={project}/>
        )}
      </Flex>
      {!project ? null : (
        <Box>
          <Heading as="h3" sx={{ mb: 4 }}>
            Download files
          </Heading>
          {isAuthenticated ? (
            <Heading as="h4" sx={{ mb: 4 }}>
              ...
            </Heading>) : (
            <Flex>
              <Box sx={{ flex: '1 1 auto' }}>
                <Heading as="h4" sx={{ mb: 4 }}>
                  Log in or sign-up to view and download data.
                </Heading>
              </Box>
              <Box><Authenticate/></Box>
            </Flex>
          )}

        </Box>
      )}
    </Layout>
  )
}

export default SecondPage

// <Flex>{!files ? null : <FilesList files={files} />}</Flex>
