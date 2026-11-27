import ctypes
import os


def require_b390():
    os.environ["VK_DRIVER_FILES"] = "/usr/share/vulkan/icd.d/intel_icd.json"
    os.environ["VK_ICD_FILENAMES"] = os.environ["VK_DRIVER_FILES"]
    lib = ctypes.CDLL("libvulkan.so.1")

    class ApplicationInfo(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint32), ("next", ctypes.c_void_p),
                    ("name", ctypes.c_char_p), ("version", ctypes.c_uint32),
                    ("engine", ctypes.c_char_p), ("engine_version", ctypes.c_uint32),
                    ("api_version", ctypes.c_uint32)]

    class InstanceInfo(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint32), ("next", ctypes.c_void_p),
                    ("flags", ctypes.c_uint32), ("app", ctypes.POINTER(ApplicationInfo)),
                    ("layer_count", ctypes.c_uint32), ("layers", ctypes.c_void_p),
                    ("extension_count", ctypes.c_uint32), ("extensions", ctypes.c_void_p)]

    lib.vkCreateInstance.argtypes = [ctypes.POINTER(InstanceInfo), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    lib.vkEnumeratePhysicalDevices.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_void_p)]
    lib.vkGetPhysicalDeviceProperties.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.vkDestroyInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    app = ApplicationInfo(0, None, b"bluetts", 0, None, 0, 1 << 22)
    info = InstanceInfo(1, None, 0, ctypes.pointer(app), 0, None, 0, None)
    instance = ctypes.c_void_p()
    status = lib.vkCreateInstance(ctypes.byref(info), None, ctypes.byref(instance))
    if status != 0:
        raise RuntimeError(f"Vulkan initialization failed: {status}")
    try:
        count = ctypes.c_uint32()
        status = lib.vkEnumeratePhysicalDevices(instance, ctypes.byref(count), None)
        if status != 0 or count.value != 1:
            raise RuntimeError(f"Expected one Intel Vulkan adapter, got {count.value} (status {status})")
        devices = (ctypes.c_void_p * count.value)()
        status = lib.vkEnumeratePhysicalDevices(instance, ctypes.byref(count), devices)
        if status != 0 or count.value != 1:
            raise RuntimeError(f"Vulkan adapter enumeration failed: {status}")
        properties = ctypes.create_string_buffer(4096)
        lib.vkGetPhysicalDeviceProperties(devices[0], properties)
        fields = ctypes.cast(properties, ctypes.POINTER(ctypes.c_uint32 * 5)).contents
        vendor, device, device_type = fields[2], fields[3], fields[4]
        if (vendor, device, device_type) != (0x8086, 0xB080, 1):
            raise RuntimeError(f"Expected Intel B390 integrated GPU, got {vendor:#x}:{device:#x} type {device_type}")
    finally:
        lib.vkDestroyInstance(instance, None)
