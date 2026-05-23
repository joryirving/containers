package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/agentmemory:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/local/bin/agentmemory", nil)
}