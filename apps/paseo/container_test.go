package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/paseo:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/bin/paseo", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/bin/opencode", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/bin/git", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/bin/rg", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/mise/shims/kubectl", "version", "--client")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/mise/shims/flux", "version", "--client")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/mise/shims/sops", "--version")
}
