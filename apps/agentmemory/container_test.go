package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/agentmemory:rolling")
	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{
		Port:       "3111",
		Path:       "/agentmemory/livez",
		StatusCode: 200,
	}, nil)
}
