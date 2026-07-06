package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/llmkube-coder-python:rolling")
	testhelpers.TestFileExists(t, image, "/foreman-agent", nil)
	// The agent binary and the Python toolchain the coder self-gate uses.
	testhelpers.TestCommandSucceeds(t, image, nil, "foreman-agent", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "python3", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "git", "--version")
	// Representative Python linter.
	testhelpers.TestCommandSucceeds(t, image, nil, "ruff", "--version")
}
