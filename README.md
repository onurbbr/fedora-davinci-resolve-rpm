# Building DaVinci Resolve RPM Package on Fedora

This guide provides a step-by-step process to build and install an RPM package for DaVinci Resolve on Fedora.

## Step 1: Install required dependencies

First, you need to install the necessary dependencies for building the RPM package. Open your terminal and run the following command:

```bash
sudo dnf install rpm-build apr-util apr-util.i686 libcxx libcxx.i686 patchelf libxcrypt-compat
```

## Step 2: Clone the repository
```bash
git clone -b master https://github.com/onurbbr/fedora-davinci-resolve-rpm.git ~/rpmbuild
```

## Step 3: Create some folders for building
```bash
cd ~/rpmbuild
mkdir BUILD BUILDROOT RPMS SOURCES SRPMS
```

## Step 4: Download and copy the DaVinci Resolve file
Download and extract the DaVinci Resolve .zip file (version 18.6.6 is used here). Then copy the .run file to the SOURCES directory in the cloned repository
```bash
cp ~/Downloads/DaVinci_Resolve_18.6.6_Linux.run ~/rpmbuild/SOURCES
```

## Step 5: Check the location of the files before starting the build process.
The file locations need to be as follows:
![Resim](Screenshot_20240812_153034.png)


## Step 6: Start the packaging process
Finally, start the RPM packaging process by running the following command:
```bash
QA_RPATHS=$(( 0x0001|0x0002|0x0004|0x0008|0x0010|0x0020 )) rpmbuild -bb ~/rpmbuild/SPECS/davinci-resolve.spec
```
It may take 10 to 15 minutes depending on your system (My system has 6 cores and 12 threads).

## Step 7: Install the generated rpm file
The generated rpm file is located under:
```bash
~/rpmbuild/RPMS/x86_64
```
You can install it like this:
```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/davinci-resolve-18.6.6-1.fc40.x86_64.rpm
```

# Warnings:
1- Since I could not fully understand Fedora's rpath control, I bypassed Fedora's rpath control with QA_PATHS and did the rpath operations manually with patchelf. So, ignore the warnings that appear on the screen during the package compilation, no problem.

2- If you think there is a new version, you can let me know from the "Issues" section, or you can manually find the file with the spec extension and change the version information and file name manually.

3- If you encounter an error while compiling, please create a "New Issue" from the "Issues" section along with your log file.

# Notes:
1- There is no problem in installing, updating and uninstalling the program.

2- The reason I created it as Native is that it is easy to install, update and uninstall. I used this method because I was tired of updating manually.

