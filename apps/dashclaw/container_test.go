package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")
	
	// Check built files exist (these are copied to final image)
	testhelpers.TestFileExists(t, ctx, image, "/app/.next/BUILD_ID", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/public", nil)
	
	// Verify container can start
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "ls", "/app/.next")
}
