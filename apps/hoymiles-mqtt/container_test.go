package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/hoymiles-mqtt:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "python3", "-m", "hoymiles_mqtt", "--help")
}
