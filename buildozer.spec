[app]
title = Vodafone Charge
package.name = vodafonecharge
package.domain = org.mostafa
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna
orientation = portrait
osx.kivy_version = 2.3.0
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True
android.ndk = 25b
android.logcat_filters = *:S python:D
p4a.branch = master

[buildozer]
log_level = 3
warn_on_root = 0

