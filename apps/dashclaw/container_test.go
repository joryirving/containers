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
	testhelpers.TestFileExists(t, ctx, image, "/app/package.json", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/next.config.js", nil)
}
