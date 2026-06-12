package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/irqbalance:rolling")
	testhelpers.TestFileExists(t, image, "/usr/sbin/irqbalance", nil)
}
