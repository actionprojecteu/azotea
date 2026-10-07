# To install just on a per-project basis
# 1. Activate your virtual environemnt
# 2. uv add --dev rust-just
# 3. Use just within the activated environment

#drive_uuid := "77688511-78c5-4de3-9108-b631ff823ef4"
drive_uuid := "8425-155D"

user :=  file_stem(home_dir())
def_drive := join("/media", user, drive_uuid)
project := file_stem(justfile_dir())
local_env := join(justfile_dir(), ".env")


# list all recipes
default:
    just --list

init:
    uv sync

# Install tools globally
tools:
    uv tool install twine
    uv tool install ruff

# Build the package
build:
    rm -fr dist/*
    uv build



# Backup .env to storage unit
env-bak drive=def_drive: (check_mnt drive) (env-backup join(drive, "env", project))

# Restore .env from storage unit
env-rst drive=def_drive: (check_mnt drive) (env-restore join(drive, "env", project))

# -------------------------
# AZOTEA Database and tools
# -------------------------

# Starts a new SQLite database export migration cycle
anew verbose="":
    #!/usr/bin/env bash
    set -exuo pipefail
    rm -fr azotea.db
    uv run azoschema --console --log-file azotea.log {{ verbose }}
    uv run azopopulate --console --trace --log-file azotea.log {{ verbose }} all --batch-size 25000


# =======================================================================



[private]
check_mnt mnt:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ ! -d  {{ mnt }} ]]; then
        echo "Drive not mounted: {{ mnt }}"
        exit 1
    fi

[private]
env-backup bak_dir:
    #!/usr/bin/env bash
    set -exuo pipefail
    if [[ ! -f  {{ local_env }} ]]; then
        echo "Can't backup: {{ local_env }} doesn't exists"
        exit 1
    fi
    mkdir -p {{ bak_dir }}
    cp {{ local_env }} {{ bak_dir }}
    cp azotea.db {{ bak_dir }}
    cp *.ecsv {{ bak_dir }}
    cp *.txt {{ bak_dir }}


[private]
env-restore bak_dir:
    #!/usr/bin/env bash
    set -euxo pipefail
    if [[ ! -f  {{ bak_dir }}/.env ]]; then
        echo "Can't restore: {{ bak_dir }}/.env doesn't exists"
        exit 1
    fi
    cp {{ bak_dir }}/.env {{ local_env }}
    cp {{ bak_dir }}/azotea.db .
    cp {{ bak_dir }}/*.ecsv .
    cp {{ bak_dir }}/*.txt .
