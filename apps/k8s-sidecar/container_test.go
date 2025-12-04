package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/k8s-sidecar:rolling")
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "/app/sidecar.py", "--help")
}
