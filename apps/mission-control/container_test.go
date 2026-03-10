package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/mission-control:rolling")

	testhelpers.TestFileExists(t, ctx, image, "/app/server.js", nil)
	testhelpers.TestFileExists(t, ctx, image, "/app/src/lib/schema.sql", nil)
}
