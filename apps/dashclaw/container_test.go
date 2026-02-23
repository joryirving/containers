package main

import (
	"context"
	"os"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:2.0.0")
	
	// Check critical files exist
	testhelpers.TestFilesExist(t, ctx, image, []string{
		"/app/package.json",
		"/app/.env",
		"/app/.env.example",
		"/app/next.config.js",
	})
	
	// Verify container runs
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "echo", "container started")
}
