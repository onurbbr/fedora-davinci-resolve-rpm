Name:           davinci-resolve
Version:        18.6.6
Release:        1%{?dist}
Summary:        Revolutionary new tools for editing, visual effects, color correction and professional audio post production, all in a single application!
License:        Proprietary
URL:            https://www.blackmagicdesign.com/products/davinciresolve
Source0:        DaVinci_Resolve_18.6.6_Linux.run
AutoReqProv:    no

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
chmod -R u+rwX,go+rX,go-w "%{_builddir}/resolve/share/panels/lib"
mv *.so "%{_builddir}/resolve/libs"
mv lib/* "%{_builddir}/resolve/libs"
popd

# Remove unnecessary installer
rm -rf %{_builddir}/resolve/installer %{_builddir}/resolve/installer* %{_builddir}/resolve/AppRun %{_builddir}/resolve/AppRun*

# Fix permissions for directories (Part 2)
find %{_builddir}/resolve -type d -exec chmod 0755 {} \;

# Fix permissions for files (Part 3) and patch ELF files
find %{_builddir}/resolve -type f -exec chmod 0755 {} \; -exec sh -c '
for file in "$@"; do
  if [ -f "$file" ] && [ "$(od -t x1 -N 4 "$file")" = *"7f 45 4c 46"* ]; then
    patchelf --set-rpath '/opt/resolve/libs:/opt/resolve/libs/plugins/sqldrivers:/opt/resolve/libs/plugins/xcbglintegrations:/opt/resolve/libs/plugins/imageformats:/opt/resolve/libs/plugins/platforms:/opt/resolve/libs/Fusion:/opt/resolve/plugins:/opt/resolve/bin:/opt/resolve/BlackmagicRAWSpeedTest/BlackmagicRawAPI:/opt/resolve/BlackmagicRAWSpeedTest/plugins/platforms:/opt/resolve/BlackmagicRAWSpeedTest/plugins/imageformats:/opt/resolve/BlackmagicRAWSpeedTest/plugins/mediaservice:/opt/resolve/BlackmagicRAWSpeedTest/plugins/audio:/opt/resolve/BlackmagicRAWSpeedTest/plugins/xcbglintegrations:/opt/resolve/BlackmagicRAWSpeedTest/plugins/bearer:/opt/resolve/BlackmagicRAWPlayer/BlackmagicRawAPI:/opt/resolve/BlackmagicRAWPlayer/plugins/mediaservice:/opt/resolve/BlackmagicRAWPlayer/plugins/imageformats:/opt/resolve/BlackmagicRAWPlayer/plugins/audio:/opt/resolve/BlackmagicRAWPlayer/plugins/platforms:/opt/resolve/BlackmagicRAWPlayer/plugins/xcbglintegrations:/opt/resolve/BlackmagicRAWPlayer/plugins/bearer:/opt/resolve/Onboarding/plugins/xcbglintegrations:/opt/resolve/Onboarding/plugins/qtwebengine:/opt/resolve/Onboarding/plugins/platforms:/opt/resolve/Onboarding/plugins/imageformats:/opt/resolve/DaVinci\ Control\ Panels\ Setup/plugins/platforms:/opt/resolve/DaVinci\ Control\ Panels\ Setup/plugins/imageformats:/opt/resolve/DaVinci\ Control\ Panels\ Setup/plugins/bearer:/opt/resolve/DaVinci\ Control\ Panels\ Setup/AdminUtility/PlugIns/DaVinciKeyboards:/opt/resolve/DaVinci\ Control\ Panels\ Setup/AdminUtility/PlugIns/DaVinciPanels:$ORIGIN' '$file'
  fi
done' sh {} +

# Use system libraries (some of resolve's libraries are broken)
rm -f %{_builddir}/resolve/libs/libglib*
rm -f %{_builddir}/resolve/libs/libgio*
rm -f %{_builddir}/resolve/libs/libgmodule*
rm -f %{_builddir}/resolve/libs/libc++.so.1
rm -f %{_builddir}/resolve/libs/libaprutil-1.so.0
ln -s /usr/lib/libc++.so.1.0 %{_builddir}/resolve/libs/libc++.so.1
ln -s /usr/lib/libaprutil-1.so.0 %{_builddir}/resolve/libs/libaprutil-1.so.0

# Modify .desktop files and icon, apply category fixes for plasma
sed -i 's|Icon=blackmagicraw-player|Icon=RESOLVE_INSTALL_LOCATION/graphics/blackmagicraw-player_256x256_apps.png|g' %{_builddir}/resolve/share/blackmagicraw-player.desktop
sed -i 's|Icon=blackmagicraw-speedtest|Icon=RESOLVE_INSTALL_LOCATION/graphics/blackmagicraw-speedtest_256x256_apps.png|g' %{_builddir}/resolve/share/blackmagicraw-speedtest.desktop
echo "StartupWMClass=resolve" | tee -a %{_builddir}/resolve/share/DaVinciResolve.desktop
echo "Categories=Qt;KDE;Graphics;2DGraphics;RasterGraphics;" | tee -a %{_builddir}/resolve/share/DaVinciResolve.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/DaVinciControlPanelsSetup.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/DaVinciResolveCaptureLogs.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/blackmagicraw-player.desktop
echo "Categories=Qt;KDE;Utility;" | tee -a %{_builddir}/resolve/share/blackmagicraw-speedtest.desktop
echo 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTRS{idVendor}=="096e", MODE="0666"' > %{_builddir}/resolve/share/etc/udev/rules.d/99-DavinciPanel.rules

# Set resolve's location to desktop files
find %{_builddir}/resolve -type f \( -name "*.desktop" -o -name "*.directory" -o -name "*.menu" \) -exec sed -i "s|RESOLVE_INSTALL_LOCATION|/opt/resolve|g" {} +

# Fixing ambiguous python shebangs (rpm-macros has a problem with this. I had to fix it manually)
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/9_export_timeline.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/7_add_subclips_to_timeline.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/10_handle_media_pool_clip_markers.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/3_grade_and_render_all_timelines.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/6_get_current_media_thumbnail.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/2_compositions_from_timeline_clips.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/1_sorted_timeline_from_folder.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/5_get_project_information.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/4_display_project_and_folder_tree.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/11_add_subclips_to_mediapool.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/8_slack_notification_by_render_job.py
sed -i 's|/usr/bin/env python|/usr/bin/env python3|' %{_builddir}/resolve/Developer/Scripting/Examples/python_get_resolve.py

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

# Desktop system configurations
install -Dm0644 %{buildroot}/opt/resolve/graphics/DV_Resolve.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/graphics/DV_ResolveProj.png -t %{buildroot}/usr/share/icons/hicolor/64x64/apps
install -Dm0644 %{buildroot}/opt/resolve/share/resolve.xml -t %{buildroot}/usr/share/mime/packages

# Udev rules
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-BlackmagicDevices.rules -t %{buildroot}/%{_udevrulesdir}
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-ResolveKeyboardHID.rules -t %{buildroot}/%{_udevrulesdir}
install -Dm0644 %{buildroot}/opt/resolve/share/etc/udev/rules.d/99-DavinciPanel.rules -t %{buildroot}/%{_udevrulesdir}

%files
/opt/resolve
/opt/resolve/*
%{_datadir}/applications/DaVinciResolve.desktop
%{_datadir}/applications/DaVinciControlPanelsSetup.desktop
%{_datadir}/applications/DaVinciResolveCaptureLogs.desktop
%{_datadir}/applications/blackmagicraw-player.desktop
%{_datadir}/applications/blackmagicraw-speedtest.desktop
%{_datadir}/icons/hicolor/64x64/apps/DV_Resolve.png
%{_datadir}/icons/hicolor/64x64/apps/DV_ResolveProj.png
%{_datadir}/mime/packages/resolve.xml
%{_udevrulesdir}/99-BlackmagicDevices.rules
%{_udevrulesdir}/99-ResolveKeyboardHID.rules
%{_udevrulesdir}/99-DavinciPanel.rules

%changelog
* Mon Aug 12 2024 Onur BÜBER <onurbuber6778@gmail.com>
- First Fedora release (Created from Arch AUR repo)
- Updated permissions and patchelf rpath handling
- Fixed BlackmagicRaw applications icon issue
