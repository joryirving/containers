package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/strixhalo-llama-turboquant-rocm-6-4-4:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/bin/llama-server", nil)
}
