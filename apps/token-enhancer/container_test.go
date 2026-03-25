package tokenenhancer

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func TestContainer(t *testing.T) {
	testhelpers.RunContainerTests(t, "token-enhancer")
}
