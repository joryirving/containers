package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/hoymiles-mqtt:rolling")
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "python3", "-m", "hoymiles_mqtt", "--help")
}
