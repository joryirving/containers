package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/irqbalance:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/sbin/irqbalance", nil)
}
