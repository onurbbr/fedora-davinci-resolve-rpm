Name:           davinci-resolve
Version:        20.3.3
Release:        1%{?dist}
Summary:        Professional video editing, color correction, visual effects and audio post-production.
License:        Proprietary
URL:            [https://www.blackmagicdesign.com/products/davinciresolve](https://www.blackmagicdesign.com/products/davinciresolve)
Source0:        DaVinci_Resolve_%{version}_Linux.run
AutoReqProv:    no

Requires:       apr, apr-util, alsa-plugins-pulseaudio, libnsl, libxcrypt-compat, libcxx, patchelf

%description
Revolutionary new tools for editing, visual effects, color correction and professional audio post production, all in a single application!

%prep
chmod u+x %{SOURCE0}
%{SOURCE0} --appimage-extract

# Rename the extracted directory to 'resolve'
mv %{_builddir}/squashfs-root %{_builddir}/resolve

# Fix permission to all files and dirs (Part 1)
chmod -R u+rwX,go+rX,go-w %{_builddir}/resolve

# Extract dvpanel framework libraries to resolve's library folder
pushd "%{_builddir}/resolve/share/panels"
tar -zxvf dvpanel-framework-linux-x86_64.tgz
rm dvpanel-framework-linux-x86_64.tgz
chmod -R u+rwX,go+rX,go-w "%{_builddir}/resolve/share/panels/lib"
mv *.so "%{_builddir}/resolve/libs"
mv lib/* "%{_builddir}/resolve/libs"
popd

# Remove unnecessary installer
rm -rf %{_builddir}/resolve/installer* %{_builddir}/resolve/AppRun*

# Fix permissions for directories (Part 2)
find %{_builddir}/resolve -type d -exec chmod 0755 {} \;

# Fix permissions for files (Part 3)
find %{_builddir}/resolve -type f -exec chmod 0644 {} \;

# Grant executable bit only to ELF binaries and shell scripts
{ set +x; } 2>/dev/null
find %{_builddir}/resolve -type f | while read file; do
  if file "$file" 2>/dev/null | grep -qE 'ELF|shell script'; then
    chmod 0755 "$file"
  fi
done
{ set -x; } 2>/dev/null

# Patch all ELF binaries: fix/clean broken RPATHs automatically
{ set +x; } 2>/dev/null
find %{_builddir}/resolve -type f | while read file; do
  file "$file" 2>/dev/null | grep -q 'ELF' || continue
  current_rpath=$(patchelf --print-rpath "$file" 2>/dev/null) || continue

  # If runpath is empty, remove it entirely (0x0010)
  if [ -z "$current_rpath" ]; then
    patchelf --force-rpath --remove-rpath "$file" 2>/dev/null || true
    continue
  fi

  # Evaluate each path entry individually
  new_rpath=$(echo "$current_rpath" | tr ':' '\n' | while read entry; do
    case "$entry" in
      '$ORIGIN'*)
        # $ORIGIN-based: valid, keep — strip trailing slash
        echo "${entry%/}"
        ;;
      /opt/resolve*)
        # Target install path: valid, keep — strip trailing slash
        echo "${entry%/}"
        ;;
      ./*|./|.)
        # Insecure relative path (0x0004): replace with $ORIGIN
        echo '$ORIGIN'
        ;;
      *)
        # Anything else (build server paths, etc.) → discard
        ;;
    esac
  done | sort -u | tr '\n' ':' | sed 's/:$//')

  # If no valid entries remain, fall back to $ORIGIN
  [ -z "$new_rpath" ] && new_rpath='$ORIGIN'

  # Force RPATH over RUNPATH to ensure $ORIGIN resolution works correctly
  patchelf --force-rpath --set-rpath "$new_rpath" "$file" 2>/dev/null || true
done
{ set -x; } 2>/dev/null

# Use system libraries (some of resolve's libraries are broken)
rm -f %{_builddir}/resolve/libs/libglib*
rm -f %{_builddir}/resolve/libs/libgio*
rm -f %{_builddir}/resolve/libs/libgmodule*
rm -f %{_builddir}/resolve/libs/libaprutil-1.so.0
ln -s /usr/lib64/libaprutil-1.so.0 %{_builddir}/resolve/libs/libaprutil-1.so.0

# Modify .desktop files and icon, apply category fixes for plasma
echo "StartupWMClass=resolve" | tee -a %{_builddir}/resolve/share/DaVinciResolve.desktop
echo "Categories=Qt;KDE;Graphics;2DGraphics;RasterGraphics;" | tee -a %{_builddir}/resolve/share/DaVinciResolve.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/DaVinciControlPanelsSetup.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/DaVinciResolveCaptureLogs.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/blackmagicraw-player.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/blackmagicraw-speedtest.desktop
echo 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="096e", MODE="0666"' > %{_builddir}/resolve/share/etc/udev/rules.d/99-DavinciPanel.rules

# Set resolve's location to desktop files
find %{_builddir}/resolve -type f \( -name "*.desktop" -o -name "*.directory" -o -name "*.menu" \) -exec sed -i "s|RESOLVE_INSTALL_LOCATION|/opt/resolve|g" {} +

# Fix Exec path to use system-wide binary
sed -i "s|^Exec=/opt/resolve/bin/resolve|Exec=resolve|g" %{_builddir}/resolve/share/DaVinciResolve.desktop

# Fixing icon problems
mv -f %{_builddir}/resolve/graphics/DV_Resolve.png %{_builddir}/resolve/graphics/davinci-resolve.png
mv -f %{_builddir}/resolve/graphics/DV_ResolveProj.png %{_builddir}/resolve/graphics/davinci-panels.png
mv -f %{_builddir}/resolve/graphics/blackmagicraw-player_256x256_apps.png %{_builddir}/resolve/graphics/blackmagicraw-player.png
mv -f %{_builddir}/resolve/graphics/blackmagicraw-speedtest_256x256_apps.png %{_builddir}/resolve/graphics/blackmagicraw-speedtest.png
find %{_builddir}/resolve -type f -name "DaVinciResolve.desktop" -exec sed -i "s|/opt/resolve/graphics/DV_Resolve.png|davinci-resolve|g" {} +
find %{_builddir}/resolve -type f -name "DaVinciControlPanelsSetup.desktop" -exec sed -i "s|/opt/resolve/graphics/DV_Panels.png|davinci-panels|g" {} +

%install
mkdir -p -m 0755 %{buildroot}/opt/resolve/{configs,DolbyVision,easyDCP,Fairlight,GPUCache,logs,Media,"Resolve Disk Database",.crashreport,.license,.LUT}
cp -rf %{_builddir}/resolve/* %{buildroot}/opt/resolve/

# Distribute files
install -Dm0644 %{buildroot}/opt/resolve/share/default-config.dat -t %{buildroot}/opt/resolve/configs
install -Dm0644 %{buildroot}/opt/resolve/share/log-conf.xml -t %{buildroot}/opt/resolve/configs
install -Dm0644 %{buildroot}/opt/resolve/share/default_cm_config.bin -t %{buildroot}/opt/resolve/DolbyVision

# Desktop entries
install -Dm0644 %{buildroot}/opt/resolve/share/DaVinciResolve.desktop -t %{buildroot}/usr/share/applications
install -Dm0644 %{buildroot}/opt/resolve/share/DaVinciControlPanelsSetup.desktop -t %{buildroot}/usr/share/applications
install -Dm0644 %{buildroot}/opt/resolve/share/DaVinciResolveCaptureLogs.desktop -t %{buildroot}/usr/share/applications
install -Dm0644 %{buildroot}/opt/resolve/share/blackmagicraw-player.desktop -t %{buildroot}/usr/share/applications
install -Dm0644 %{buildroot}/opt/resolve/share/blackmagicraw-speedtest.desktop -t %{buildroot}/usr/share/applications

# Mime types and application icons
install -Dm0644 %{buildroot}/opt/resolve/graphics/davinci-resolve.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/graphics/davinci-panels.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/graphics/blackmagicraw-player.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/graphics/blackmagicraw-speedtest.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/share/resolve.xml -t %{buildroot}/usr/share/mime/packages

# Udev rules
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-BlackmagicDevices.rules -t %{buildroot}/%{_udevrulesdir}
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-ResolveKeyboardHID.rules -t %{buildroot}/%{_udevrulesdir}
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-DavinciPanel.rules -t %{buildroot}/%{_udevrulesdir}

# Symlinks for system-wide binary access
install -d %{buildroot}/usr/bin
ln -sf /opt/resolve/bin/resolve %{buildroot}/usr/bin/resolve

%files
/opt/resolve
/opt/resolve/*
%{_bindir}/resolve
%{_datadir}/applications/DaVinciResolve.desktop
%{_datadir}/applications/DaVinciControlPanelsSetup.desktop
%{_datadir}/applications/DaVinciResolveCaptureLogs.desktop
%{_datadir}/applications/blackmagicraw-player.desktop
%{_datadir}/applications/blackmagicraw-speedtest.desktop
%{_datadir}/icons/hicolor/64x64/apps/davinci-resolve.png
%{_datadir}/icons/hicolor/64x64/apps/davinci-panels.png
%{_datadir}/icons/hicolor/64x64/apps/blackmagicraw-player.png
%{_datadir}/icons/hicolor/64x64/apps/blackmagicraw-speedtest.png
%{_datadir}/icons/hicolor/64x64/apps/
%{_datadir}/icons/hicolor/64x64/apps/
%{_datadir}/mime/packages/resolve.xml
%{_udevrulesdir}/99-BlackmagicDevices.rules
%{_udevrulesdir}/99-ResolveKeyboardHID.rules
%{_udevrulesdir}/99-DavinciPanel.rules

%changelog
* Sat May 30 2026 Onur BÜBER <onurbuber@engineer.com>
- Upgraded DaVinci Resolve to 20.3.3
- Keep bundled libc++ to avoid symbol mismatch Segfault (Thanks to StephR74)
- Replaced shebang-related permission fixes with smart executable detection (ELF/shell script only)
- Added automatic RPATH/RUNPATH cleanup via patchelf to fix check-rpaths errors without QA_RPATHS bypass
  - Removes empty runpaths (0x0010)
  - Replaces insecure relative paths like './' with $ORIGIN (0x0004)
  - Discards leftover build server absolute paths (0x0002, 0x0020)
  - Preserves valid $ORIGIN-based and /opt/resolve paths
  - Forces RPATH over RUNPATH to ensure $ORIGIN resolution works correctly on Fedora
- Added /usr/bin/resolve symlink for system-wide binary access
- Fixed Exec path in DaVinciResolve.desktop to use system-wide binary
