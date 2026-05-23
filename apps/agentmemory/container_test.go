package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/agentmemory:rolling")
	testhelpers.TestHTTPEndpoint(t, ctx, image, testhelpers.HTTPTestConfig{
		Port:       "3111",
		Path:       "/agentmemory/livez",
		StatusCode: 200,
	}, nil)
}