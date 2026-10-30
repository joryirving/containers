package main

import (
    "testing"

    "github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
    image := testhelpers.GetTestImage("ghcr.io/joryirving/courier-opencode:rolling")

    testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/bin/opencode", "--version")
    testhelpers.TestCommandSucceeds(t, image, nil, "/usr/bin/test", "-f", "/home/courier/.agents/skills/simple-english/SKILL.md")
}
