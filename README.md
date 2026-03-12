# System Spec Inspector

System Spec Inspector is a lightweight desktop tool for quickly inspecting hardware specifications such as CPU, RAM, storage devices, and GPU memory on Windows systems.

The tool collects system information using WMI and presents it in a readable format.  
It is designed to operate reliably across different Windows environments by incorporating defensive handling and fallback logic.

---

## Purpose

Provide a quick and convenient way to inspect the basic hardware specifications of a Windows PC.

---

## Supported Environment

- Windows 7 / 10 / 11
- No administrator privileges required

---

## Technical Notes

- Python 3.7 (maintained for Windows 7 compatibility)
- PyQt5-based desktop interface
- WMI-based system specification collection
- Defensive handling and multiple fallback logic paths for reliability across different environments

---

## Version History

### v1.6
- Safe internal refactoring with behavior-preserving changes
- Reduced duplicated logic in UI/controller/formatter/collector modules
- Improved internal exception logging consistency in DXGI GPU collection

### v1.5
- Added PC type classification logic
- Improved onboard / replaceable RAM detection

### v1.4
- Improved UI stability across Windows 7/10/11 DPI scaling environments
- Added initial loading overlay for smoother startup experience
- Improved RAM brand detection using WMI/SMBIOS strings and PartNumber patterns
- Refactored RAM specification display logic
  - Added compression logic for duplicate modules (xN format)
  - Improved fallback handling for missing values
  - Distinguish between "module information unavailable" and "not installed"
  - Unified RAM capacity format (8.00GB → 8GB)

### v1.3
- Internal architecture refactoring
- Separated collector / formatter responsibilities following SOLID principles
- Reduced redundant WMI connections to improve data collection performance

### v1.2
- Added GPU VRAM detection using DXGI
- Refined total RAM display logic

### v1.1
- Bug fixes

### v1.0
- Initial release
- Basic hardware specification inspection (CPU, RAM, storage devices)
