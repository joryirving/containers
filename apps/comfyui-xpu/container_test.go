package main

import (
	"os"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

// Everything here runs without a GPU: the image's XPU paths need /dev/dri and
// a Panther Lake device, which CI does not have, so device acceptance is done
// on the target host after deployment. These checks pin the packaging
// contract: the ptl-h kernel wheel, the provider wheels, the manifest
// constraints, and the entrypoint wiring.
func Test(t *testing.T) {
	if os.Getenv("TEST_IMAGE") == "" {
		t.Skip("TEST_IMAGE is set by the CI image test workflow")
	}
	image := testhelpers.GetTestImage("ghcr.io/joryirving/comfyui-xpu:rolling")

	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "grep -qx 'ComfyUI 0.45.0' /llm/ComfyUI/comfyui_version.py || grep -q '__version__ = \"0.45.0\"' /llm/ComfyUI/comfyui_version.py")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m; assert m.version('comfy-kitchen') == '0.2.41', m.version('comfy-kitchen')")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import omni_xpu_kernel as k; assert k.__xpu_target__ == 'ptl-h', k.__xpu_target__; print(k.__version__)")
	// The wheel is AOT-locked to ptl-h; the loaded core target must agree with
	// the baked XPU_TARGET label even on a GPU-less runner.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import omni_xpu_kernel as k; assert k.core_aot_target() == 'ptl-h', k.core_aot_target()")
	// The provider wheels must own no canonical comfy_kitchen/comfy_aimdo files
	// (they are sidecar providers); a canonical overwrite would break upgrades.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m; files = [str(f) for f in (m.files('comfy-kitchen-xpu-runtime') or [])]; assert files, 'no recorded files'; assert not [f for f in files if f.split('/')[0] in ('comfy_kitchen', 'comfy_aimdo')], [f for f in files if f.split('/')[0] in ('comfy_kitchen', 'comfy_aimdo')]")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test \"$(wc -l < /llm/manifests/omni-runtime-constraints.txt)\" -eq 6")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -x /llm/entrypoints/start_comfyui.sh && grep -q 'oneapi/setvars.sh' /llm/entrypoints/start_comfyui.sh")
	// The entrypoint must wire the shipped model-path config, the /data
	// directories, and the pinned manager into ComfyUI's CLI.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "grep -q -- '--extra-model-paths-config /llm/configs/comfyui_host_models.yaml' /llm/entrypoints/start_comfyui.sh && grep -q -- '--input-directory /data/input' /llm/entrypoints/start_comfyui.sh && grep -q -- '--output-directory /data/output' /llm/entrypoints/start_comfyui.sh && grep -q -- '--user-directory /data/user' /llm/entrypoints/start_comfyui.sh && grep -q -- '--enable-manager' /llm/entrypoints/start_comfyui.sh")
	// onednn identity: the venv's libdnnl is the patched 3.11.2 source build,
	// not the PyPI distribution's DSO.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test \"$(readlink -f /opt/venv/lib/libdnnl.so.3)\" = /opt/venv/lib/libdnnl.so.3.11 && grep -q '^source_revision=' /llm/manifests/onednn-runtime.env")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -d /llm/ComfyUI/custom_nodes/ComfyUI-OmniXPU && cd /llm/ComfyUI/custom_nodes/ComfyUI-OmniXPU && git rev-parse HEAD >/dev/null")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -d /llm/ComfyUI/custom_nodes/ComfyUI-GGUF-XPU && test -d /llm/ComfyUI/custom_nodes/ComfyUI-KJNodes")
}
