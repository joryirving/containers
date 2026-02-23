package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")
	// Just verify container can start - don't check HTTP response
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "echo", "container started")
}
