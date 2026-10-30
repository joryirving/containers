package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/opencode:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/bin/opencode", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/bin/git", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/bin/gh", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -f /opt/agent-skills/simple-english/SKILL.md && test -f /opt/agent-skills/simple-english/references/rule-catalog.md")
}
