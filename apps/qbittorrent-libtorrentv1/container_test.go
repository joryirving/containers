package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/qbittorrent:rolling")
	testhelpers.TestHTTPEndpoint(t, ctx, image, testhelpers.HTTPTestConfig{Port: "8080"}, nil)
}
