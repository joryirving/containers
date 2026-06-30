package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/foreman-dispatch-bridge:rolling")

	// One-shot CronJob image with no server to probe and whose entrypoint
	// (_real_main) requires in-cluster config + dispatch env. Smoke-test that
	// the bridge package and its dependencies import cleanly in the built image;
	// importing does not execute the __main__ entrypoint.
	testhelpers.TestCommandSucceeds(t, image, nil, "python", "-c", "import bridge.main")
}
