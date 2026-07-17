name: Build Android APK

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout Cloud Repository
      uses: actions/checkout@v4

    # 1. الخطوة الأهم: إجبار السيرفر على استخدام جافا 17 المتوافق مع API 33
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    # 2. تثبيت كل المكتبات المساعدة لنظام أندرويد لمنع خطأ gradlew
    - name: Install System Dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y build-essential git ffmpeg graphviz ccache cloc libffi-dev libssl-dev libgmp-dev libmpfr-dev libmpc-dev libtool automake autoconf unzip putclip sample-icons libjpeg-dev

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install Buildozer and Cython
      run: |
        pip install --upgrade pip
        pip install --upgrade buildozer cython

    # 3. قبول التراخيص وبدء البناء وتطهير الذاكرة المؤقتة القديمة
    - name: Build Android App with Buildozer
      run: |
        buildozer android clean
        buildozer android debug

    # 4. استخراج ملف الـ APK النهائي لتستطيع تحميله وتجربته
    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: Vodafone-Charge-APK
        path: bin/*.apk
