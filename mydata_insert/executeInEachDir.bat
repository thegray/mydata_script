@echo off
for /d %%D in (*) DO (
    pushd %%D
    python insertMp4InCurDir.py
    popd
)