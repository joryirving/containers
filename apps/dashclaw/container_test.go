package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")
	
	// Minimal env vars for container to start
	env := []string{
		"DATABASE_URL=postgresql://test:test@localhost:5432/test",
		"NEXTAUTH_SECRET=test-secret-min-32-chars-here",
		"ENCRYPTION_KEY=test-32-char-encryption-key",
	}
	
	testhelpers.TestHTTPEndpoint(t, ctx, image, testhelpers.HTTPTestConfig{Port: "3000"}, &testhelpers.ContainerConfig{
		Env: env,
	})
}

