#![allow(unused_imports)]
use std::fs;
use std::arch::asm;
use std::ptr;

use sysinfo::{ProcessExt, SystemExt};
#[cfg(target_os = "windows")]
use winreg::{enums::HKEY_LOCAL_MACHINE, RegKey};
#[cfg(target_os = "windows")]
use winapi::{
    shared::minwindef::FILETIME,
    shared::ntdef::ULARGE_INTEGER,
    um::{minwinbase::SYSTEMTIME, sysinfoapi::GetLocalTime, timezoneapi::SystemTimeToFileTime},
};

const PATH_BANNED: [&str; 4] = [
    "C:\\windows\\System32\\Drivers\\Vmmouse.sys",
    "C:\\windows\\System32\\Drivers\\vm3dgl.dll",
    "C:\\windows\\System32\\vmdum.dll",
    "C:\\windows\\System32\\Drivers\\VBoxGuest.sys",
];

const PROC_BANNED_VM: [&str; 6] = [
    "Vmtoolsd.exe",
    "Vmwaretrat.exe",
    "Vmwareuser.exe",
    "Vmwareuser.exe",
    "vm_process.exe",
    "VmRemoteGuest.exe",
];

pub fn antidbg() -> bool {
    // --- Low Level Antivm check ---

    // === PEB & Time check ===

    #[cfg(target_os = "windows")]
    {
        let qw_native_elapsed = 1000;
        let timedbg: bool;

        let bv = unsafe {
            let mut st_start: SYSTEMTIME = std::mem::zeroed();
            let mut st_end: SYSTEMTIME = std::mem::zeroed();

            let mut ft_start: FILETIME = std::mem::zeroed();
            let mut ft_end: FILETIME = std::mem::zeroed();

            let peb: usize;
            let bv: usize;

            GetLocalTime(&mut st_start);

            #[cfg(target_arch = "x86_64")]
            asm!("mov {}, gs:[60h]", out(reg) peb);

            #[cfg(target_arch = "x86")]
            asm!("mov {}, fs:[30h]", out(reg) peb);

            asm!("movzx {}, byte ptr [{} + 2h]", out(reg) bv, in(reg) peb);

            if bv != 0 {
                ptr::write((peb + 2) as *mut u8, 0u8);
            }

            GetLocalTime(&mut st_end);

            if SystemTimeToFileTime(&st_start, &mut ft_start) == 0
                || SystemTimeToFileTime(&st_end, &mut ft_end) == 0
            {
                timedbg = false;
            } else {
                let ui_start = u64::from(ft_start.dwLowDateTime)
                    | ((u64::from(ft_start.dwHighDateTime)) << 32);
                let ui_end =
                    u64::from(ft_end.dwLowDateTime) | ((u64::from(ft_end.dwHighDateTime)) << 32);

                timedbg = (ui_end - ui_start) > qw_native_elapsed;
            }

            bv
        };

        if bv != 0 || timedbg {
            return true;
        }
    }

    false
}

pub fn antivm() -> bool {
    // --- WinReg check ---

    #[cfg(target_os = "windows")]
    {
        let hklm = RegKey::predef(HKEY_LOCAL_MACHINE);
        if hklm.open_subkey(lc!("Software\\Wine")).is_ok() {
            return true;
        }
    }

    // --- Process check ---

    let mut system = sysinfo::System::new_all();
    system.refresh_processes();

    for (_pid, proc) in system.processes().iter() {
        if PROC_BANNED_VM.iter().any(|v| v == &proc.name()) {
            return true;
        }
    }

    // --- Path check ---

    for path in PATH_BANNED.iter() {
        if fs::metadata(path).is_ok() {
            return true;
        }
    }
    false
}

pub fn antisnb() -> bool {
    #[allow(unused_assignments)]
    let mut tsc: u64 = 0;
    let mut acc: u64 = 0;

    // ? 200 CPU cycles
    for _ in 0..100 {
        unsafe {
            // --- Start cycles---
            tsc = core::arch::x86_64::_rdtsc() as u64;

            let _out = core::arch::x86_64::__cpuid_count(0, 0).edx;
            acc += (core::arch::x86_64::_rdtsc() as u64) - tsc;
        }
    }

    if (acc / 100) > 300 {
        return true;
    }

    return false;
}
