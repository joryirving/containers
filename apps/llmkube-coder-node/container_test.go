package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/llmkube-coder-node:rolling")
	testhelpers.TestFileExists(t, image, "/foreman-agent", nil)
	// The agent binary and the Node toolchain the coder self-gate uses.
	testhelpers.TestCommandSucceeds(t, image, nil, "foreman-agent", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "node", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "npm", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "git", "--version")
	// Representative Node linter.
	testhelpers.TestCommandSucceeds(t, image, nil, "eslint", "--version")
}
