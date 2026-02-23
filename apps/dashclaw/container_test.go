package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")
	
	// Check critical files exist
	testhelpers.TestFileExists(t, ctx, image, "/app/package.json", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/.env", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/next.config.js", nil)
	
	// Verify container runs
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "echo", "container started")
}
