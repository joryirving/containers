package container

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func TestOllamaIntel(t *testing.T) {
	container := &testhelpers.Container{
		Image:   "ollama-intel:latest",
		Command: []string{"ollama", "version"},
	}

	output := container.Run(t)

	if !output.Assert(t).Contains("ollama version") {
		t.Error("Expected ollama version output")
	}
}