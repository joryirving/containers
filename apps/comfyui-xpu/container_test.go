package main

import (
	"os"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

// Everything here runs without a GPU: the image's XPU paths need /dev/dri and
// a Panther Lake device, which CI does not have, so device acceptance is done
// on the target host after deployment (see README). These checks pin the
// packaging contract: the ptl-h wheel set, the manifest constraints, and the
// entrypoint wiring. Importing torch without a device is safe and proven by
// intel/llm-scaler's own build (it runs `python -c "import torch"` in a
// device-less build stage).
func Test(t *testing.T) {
	if os.Getenv("TEST_IMAGE") == "" {
		t.Skip("TEST_IMAGE is set by the CI image test workflow")
	}
	image := testhelpers.GetTestImage("ghcr.io/joryirving/comfyui-xpu:rolling")

	// Rootless per repo standard: the image user is nobody (65534).
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test \"$(id -u)\" = 65534 && test \"$(id -g)\" = 65534")

	// The runtime dirs the nobody user must write to are owned by it, and the
	// shipped model-path config is in place.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -d /data/input && test -d /data/output && test -d /data/user && test -d /models/host && test -w /data/output && test -r /llm/configs/comfyui_host_models.yaml")

	// Entrypoint present, executable, and it performs the omix_torch_runtime
	// setvars + Torch LD_LIBRARY_PATH reorder.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -x /llm/entrypoints/start_comfyui.sh && grep -q 'oneapi/setvars.sh' /llm/entrypoints/start_comfyui.sh && grep -q 'site-packages/torch/lib' /llm/entrypoints/start_comfyui.sh")

	// The entrypoint wires the shipped model-path config, the /data
	// directories, and the pinned manager into ComfyUI's CLI.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "grep -q -- '--extra-model-paths-config /llm/configs/comfyui_host_models.yaml' /llm/entrypoints/start_comfyui.sh && grep -q -- '--input-directory /data/input' /llm/entrypoints/start_comfyui.sh && grep -q -- '--output-directory /data/output' /llm/entrypoints/start_comfyui.sh && grep -q -- '--user-directory /data/user' /llm/entrypoints/start_comfyui.sh && grep -q -- '--enable-manager' /llm/entrypoints/start_comfyui.sh && grep -q -- '--disable-smart-memory' /llm/entrypoints/start_comfyui.sh && grep -q -- '--cache-none' /llm/entrypoints/start_comfyui.sh && grep -q 'COMFYUI_UNLOAD_WEIGHTS' /llm/entrypoints/start_comfyui.sh")

	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", `grep -q 'OMNI_COMFYUI_RESERVE_VRAM_GB:-4' /llm/entrypoints/start_comfyui.sh && grep -q -- '--enable-dynamic-vram' /llm/entrypoints/start_comfyui.sh && grep -q -- '--allocator-preload-path' /llm/entrypoints/start_comfyui.sh && grep -q 'LD_PRELOAD=' /llm/entrypoints/start_comfyui.sh`)
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/bash", "-c", `set -eo pipefail; export OMNI_COMFYUI_RESERVE_VRAM_GB=bad; if /llm/entrypoints/start_comfyui.sh > /tmp/reserve-test.log 2>&1; then exit 1; fi; grep -q 'must be a nonnegative number' /tmp/reserve-test.log`)
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/bash", "-c", `set -eo pipefail; export CLI_ARGS='--enable-dynamic-vram --disable-dynamic-vram'; if /llm/entrypoints/start_comfyui.sh > /tmp/dynamic-test.log 2>&1; then exit 1; fi; grep -q 'choose only one DynamicVRAM' /tmp/dynamic-test.log`)
	// Resolve and inspect the native hook without initializing an XPU device.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/bash", "-c", `set -eo pipefail; hook=$(python /llm/ComfyUI/custom_nodes/ComfyUI-OmniXPU/runtime_bootstrap.py --allocator-preload-path); test -r "$hook"; for symbol in xpu_ur_hook_is_interposed xpu_ur_hook_enable xpu_ur_hook_disable xpu_ur_hook_get_stats; do nm -D "$hook" | grep -q " $symbol$"; done`)
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "grep -q '__version__ = \"0.45.0\"' /llm/ComfyUI/comfyui_version.py")

	// Every pinned distribution, read from metadata only (no torch import).
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m; v = m.version; assert v('torch') == '2.14.0+xpu'; assert v('torchvision') == '0.29.0+xpu'; assert v('torchaudio') == '2.11.0+xpu'; assert v('comfyui-frontend-package') == '1.58.5'; assert v('comfyui-workflow-templates') == '0.11.105'; assert v('comfyui-manager') == '4.2.2'; assert v('comfy-kitchen') == '0.2.41'; assert v('comfy-aimdo') == '0.6.0'; assert v('comfy-kitchen-xpu-runtime') == '0.2.41'; assert v('comfy-aimdo-xpu-runtime') == '0.6.0'; assert v('omni-xpu-kernel')")

	// The ptl-h AOT lock must survive packaging: the kernel wheel version
	// carries the target, and the kitchen provider wheel records the runtime
	// target/torch pairing it was built against. A wrong XPU_TARGET build ARG
	// would otherwise ship silently.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m; v = m.version('omni-xpu-kernel'); assert 'ptl' in v, v")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m, json; d = m.distribution('comfy-kitchen-xpu-runtime'); j = json.load(open(d.locate_file('comfy_kitchen_xpu_runtime/provider.json'))); assert j['runtime']['xpu_targets'] == ['ptl-h'], j['runtime']; assert j['runtime']['torch_version'].startswith('2.14.0'), j['runtime']")

	// The provider wheels must own no canonical comfy_kitchen/comfy_aimdo files
	// (they are sidecar providers); a canonical overwrite would break upgrades.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "-c", "import importlib.metadata as m; files = [str(f) for f in (m.files('comfy-kitchen-xpu-runtime') or [])]; assert files, 'no recorded files'; assert not [f for f in files if f.split('/')[0] in ('comfy_kitchen', 'comfy_aimdo')], [f for f in files if f.split('/')[0] in ('comfy_kitchen', 'comfy_aimdo')]")

	// Runtime constraint manifest: the six pinned runtime distributions, with
	// the Torch identity, gating any later pip install through PIP_CONSTRAINT.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test \"$(wc -l < /llm/manifests/omni-runtime-constraints.txt)\" -eq 6 && grep -qx 'torch==2.14.0+xpu' /llm/manifests/omni-runtime-constraints.txt")

	// Dependency snapshot and provider wheel digests (the latter is verifiable
	// against the wheels the image keeps under /wheels/providers).
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "grep -q 'comfyui_frontend_package==1.58.5' /llm/manifests/comfyui-python-freeze.txt && test ! -d /wheels")

	// onednn identity: the venv's libdnnl is the patched 3.11.2 source build,
	// not the PyPI distribution's DSO.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test \"$(readlink -f /opt/venv/lib/libdnnl.so.3)\" = /opt/venv/lib/libdnnl.so.3.11 && grep -q '^patch_sha256=0a7afff4134f115b4bc53f46301ca3d62b1c11dc02e32c64635c469769fcdaeb$' /llm/manifests/onednn-runtime.env")

	// Custom nodes shipped: the Omni adapter and every pinned third-party
	// node directory.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test -d /llm/ComfyUI/custom_nodes/ComfyUI-OmniXPU")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "for d in ComfyUI-GGUF-XPU ComfyUI-KJNodes comfyui-videohelpersuite comfyui_controlnet_aux ComfyUI_essentials; do test -d \"/llm/ComfyUI/custom_nodes/$d\" || exit 1; done")

	// Smoke: the server entrypoint runs under the image user. Note this only
	// exercises arg parsing (argparse exits on --help before torch imports);
	// device acceptance is a host-validation item.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/venv/bin/python", "/llm/ComfyUI/main.py", "--help")
}
