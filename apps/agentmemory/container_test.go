package main

import (
	"testing"
	"time"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/agentmemory:rolling")
	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{
		Port:       "3111",
		Path:       "/agentmemory/livez",
		StatusCode: 200,
		// First boot fetches and starts the iii state/http workers before
		// the REST port answers; the compose startup timeout is 300s.
		Timeout: 5 * time.Minute,
	}, nil)
}
