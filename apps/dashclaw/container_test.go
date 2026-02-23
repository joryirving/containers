package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")
	
	// These files SHOULD exist in the final image
	// Test fails = container is broken (missing files)
	testhelpers.TestFileExists(t, ctx, image, "/app/package.json", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/.env", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/next.config.js", nil)
}
