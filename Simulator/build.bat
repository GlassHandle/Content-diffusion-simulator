@echo off
rem Build the simulator (run from Simulator\).

g++ -std=c++17 -O2 -Wall -Wextra -Iinclude ^
    src/loaders.cpp src/engagement.cpp src/propagation.cpp ^
    src/montecarlo.cpp src/main.cpp ^
    -static -o simulator.exe
if %errorlevel% equ 0 (echo build OK: simulator.exe) else (echo BUILD FAILED & exit /b 1)
