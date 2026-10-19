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

# --------------------
# Workspace management
# --------------------

# install additional tools
tools:
    uv tool install uv-publish

# Creates virtual env
init:
    uv sync

# sets the packahe version and modifies pyproject.toml
version pkg version:
    uv version --package {{pkg}} {{version}}


# Build the package
build pkg:
    #!/usr/bin/env bash
    set -exuo pipefail
    pkg={{pkg}}
    rm -fr dist/${pkg}/*
    uv build --package "${pkg}" --out-dir dist/${pkg}

test-publish pkg:
    #!/usr/bin/env bash
    set -exuo pipefail
    pkg={{pkg}}
    module="${pkg//-/_}"
    uvx uv-publish --repository testpypi --verbose "dist/${pkg}/*"
    uv run --index "https://test.pypi.org/simple/" --with ${pkg} --no-project python -c "from ${module} import __version__; print(__version__)"

publish pkg:
    #!/usr/bin/env bash
    set -exuo pipefail
    pkg={{pkg}}
    module="${pkg//-/_}"
    uvx uv-publish ${pkg} --verbose "dist/${pkg}/*"
    uv run --with ${pkg} --no-project python -c "from ${module} import __version__; print(__version__)"


# -------------------------
# AZOTEA Database and tools
# -------------------------

# Starts a new SQLite database export migration cycle
anew package="packages/azotea-cli" verbose="":
    #!/usr/bin/env bash
    set -exuo pipefail
    package={{package}}
    rm -fr azotea.db
    uv run azoschema --console --trace {{ verbose }} all --batch-size 25000
    pushd "${package}"
    uv run alembic stamp head
    popd

# setup a new alembic tree in a project
alembic-setup package="packages/azotea-cli":
    #!/usr/bin/env bash
    set -exuo pipefail
    package={{package}}
    pushd "${package}"
    uv run alembic init alembic
    popd

# migrate a pre-existing azotea database to SQLAlchemy
alembic-old-db package="packages/azotea-cli" baseline="2d90c82cffb2":
    #!/usr/bin/env bash
    set -exuo pipefail
    package="{{package}}"
    baseline="{{baseline}}"
    pushd "${package}"
    uv run alembic stamp "${baseline}"
    popd

# compares python ORM with existing eschema and generate up/down scripts
alembic-diff message package="packages/azotea-cli":
    #!/usr/bin/env bash
    set -exuo pipefail
    package="{{package}}"
    message="{{message}}"
    pushd "${package}"
    uv run alembic revision --autogenerate -m "${message}"
    popd

# Apply pending Alembic migrations
alembic-upgrade package="packages/azotea-cli" revision="head":
    #!/usr/bin/env bash
    set -exuo pipefail
    package="{{package}}"
    revision="{{revision}}"
    pushd "${package}"
    uv run alembic upgrade "${revision}"
    popd

# -------------------------
# AZOTEA Database and tools
# -------------------------

exif-setup:
    #!/usr/bin/env bash
    set -exuo pipefail
    IMAGES=images/Carpeta1
    uv run azotool --console --trace consent view --agree
    uv run azotool --console --trace observer create --default --name Juan --surname "Gómez Pérez" \
            --affiliation "Agrupación Astronómica de Alcafrán" --acronym AA-ACFN
    uv run azotool --console --trace location create --default --randomize --site-name Alcafrán --location Alcafrán \
            --longitude -2.7335649 --latitude 40.4966031 --utc-offset 1
    uv run azotool --console --trace configure optics --focal-length 50 --f-number 3.5
    uv run azotool --console --trace camera create --default \
        --from-image ${IMAGES}/2020_12_1200_02_329999.CR2
    uv run azotool --console --trace roi create --default --width 500 --height 400 \
            --from-image ${IMAGES}/2020_12_1200_02_329999.CR2
    #uv run azotool --console configure publishing --username foo --password bar --url http://localhost:8080


exif-register log="":
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
         logfile=""
    fi
    uv run azotea --console  ${logfile} --trace batch --images-dir images --only-load --depth 8

exif-sky log="" :
        #!/usr/bin/env bash
        set -exuo pipefail
        log={{log}}
        if [ "${log}" != "" ]; then
            logfile="--log-file azotea.log"
        else
             logfile=""
        fi
        uv run azotea --console  ${logfile} --trace batch --images-dir images --only-sky --depth 8

exif-all: (anew) (exif-setup) (exif-register) (exif-sky) (export-all) (sky-summary)

# =======================================================================

# --------------------------------
# Indiviual provisonoing use cases
# --------------------------------

consent agree="":
    uv run azotool --console --log-level debug consent view {{agree}}

location1:
    uv run azotool --console --log-level debug location create \
        --site-name "Prado de la burra" --location Alcafran
location2:
    uv run azotool --console --log-level debug location create \
        --site-name "Prado de la burra" --location Alcafran --longitude -3.5 --latitude 40.5

observer1:
        uv run azotool --console --log-level debug observer create \
            --name Vieja --surname "del Visillo"  --acronym AAAFN --affiliation "Agrupacion Astronómica de Alcafran"
observer2:
        uv run azotool --console --log-level debug observer create \
            --name Vieja --surname "del Visillo"  --acronym AAACFN --affiliation "Agrupacion Astronómica de Alcafran"
observer3:
        uv run azotool --console --log-level debug observer create \
            --name Vieja --surname "del Visillo"  --acronym AAAFN --affiliation "Agrupacion Astronómica de Alcafran" --fix
optics:
    uv run azotool --console configure optics --focal-length 50 --f-number 3.5

camera1:
   uv run azotool --console --log-level debug  camera create --default --as-given \
       --model "Canon EOS 400D DIGITAL" --extension .CR2 --header-type EXIF \
       --bayer-pattern GBRG --width 5344 --height 3516 --bias 2048

camera2 :
    #!/usr/bin/env bash
    set -exuo pipefail
    IMAGES=images/Carpeta1
    uv run azotool --console   camera create --default \
        --from-image ${IMAGES}/2020_12_1200_02_329999.CR2


roi1:
     uv run azotool --console roi create --default --as-given \
        --x1 100 --x2 600 --y1 300 --y2 700

roi2:
    #!/usr/bin/env bash
    set -exuo pipefail
    IMAGES=images/Carpeta1
     uv run azotool --console  roi create --default --width 500 --height 400 \
        --from-image ${IMAGES}/2020_12_1200_02_329999.CR2

# =============
# Reports stuff
# =============

image-summary:
    uv run azotool --console --trace image summary

sky-summary:
     uv run azotool --console --trace sky summary

export-all:
     uv run azotool --console --trace sky export --all --csv-dir .

export-range:
     uv run azotool --console --trace sky export --range --from-date 2020-12-11 --to-date 2020-12-11 --csv-dir .

export-month:
     uv run azotool --console --trace sky export --latest-month --csv-dir .

export-night:
     uv run azotool --console --trace sky export --latest-night --csv-dir .

export-unpublished:
     uv run azotool --console --trace sky export --unpublished --csv-dir .

# =====================
# FITS IMAGE PROCESSING
# =====================

fits-anew:
    #!/usr/bin/env bash
    set -exuo pipefail
    src="images/FITS_copia"
    dst="images/FITS"
    cp -fr ${src}/* ${dst}

[private]
fits-setup dir image:
    #!/usr/bin/env bash
    set -exuo pipefail
    AZOTEA_HOME=$(pwd)
    IMAGES={{dir}}
    IMAGE={{image}}
    uv run azotool --console consent view  --agree
    uv run azotool --console  observer create --default --name Juan --surname "Gómez Pérez" \
        --affiliation "Agrupación Astronómica de Alcafrán" --acronym AA-ACFN
    uv run azotool  --console location create --default --site-name Alcafrán --location Alcafrán \
        --longitude -2.7335649 --latitude 40.4966031 --utc-offset 1
    uv run azotool --console configure optics --focal-length 50 --f-number 3.5
    uv run azotool --console --trace camera create --default \
        --from-image ${IMAGES}/${IMAGE}
    uv run azotool  --console --trace roi create --default --width 500 --height 400 \
        --from-image ${IMAGES}/${IMAGE}
    #uv run azotool --console configure publishing --username foo --password bar --url http://localhost:8080

[private]
fits-register dir log:
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    dir={{dir}}
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
         logfile=""
    fi
    uv run azotea --console --trace --log-level debug ${logfile} batch --images-dir ${dir} --only-load --depth 8

[private]
fits-sky dir log:
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    dir={{dir}}
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
         logfile=""
    fi
    uv run azotea --console --trace --log-level debug ${logfile} batch --images-dir ${dir} --only-sky --depth 8

[private]
fits-view dir="images/FITS" log="":
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    dir={{dir}}
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
        logfile=""
    fi
    uv run azofits --console --trace ${logfile} --images-dir ${dir} view

# ================================
# FITS / SHAPPCAP IMAGE PROCESSING
# ================================

sharpcap-edit log="" :
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    dir=images/FITS/sharpcap
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
        logfile=""
    fi
    uv run azofits --console --trace ${logfile} --images-dir ${dir} edit \
         --bias 100 --image-type LIGHT


sharpcap-setup: (sharpcap-edit) (fits-setup "images/FITS/sharpcap" "Capture_00008.fits")

sharpcap-register log="": (fits-register "images/FITS/sharpcap" log)

sharpcap-sky log="": (fits-sky "images/FITS/sharpcap" log)

sharpcap-view log="": (fits-view "images/FITS/sharpcap" log)

sharpcap-all: (anew) (fits-anew) (sharpcap-edit) (sharpcap-view) (sharpcap-setup) (sharpcap-register) (sharpcap-sky)  (export-all) (sky-summary)


# ===================================
# FITS / CAPTURAFITS IMAGE PROCESSING
# ===================================

capturafits-setup: (capturafits-edit) (fits-setup "images/FITS/capturafits" "20220101-180045.10000.fits")

capturafits-register log="": (fits-register "images/FITS/capturafits" log)

capturafits-sky log="": (fits-sky "images/FITS/capturafits" log)

capturafits-view log="": (fits-view "images/FITS/capturafits" log)

capturafits-edit log="":
    #!/usr/bin/env bash
    set -exuo pipefail
    log={{log}}
    dir=images/FITS/capturafits
    if [ "${log}" != "" ]; then
        logfile="--log-file azotea.log"
    else
        logfile=""
    fi
    uv run azofits --console --trace ${logfile} --images-dir ${dir} creator --set capturafits
    uv run azofits --console --trace ${logfile} --images-dir ${dir} edit \
         --camera "ZWO ASI224 MC" --bayer-pattern RGGB  --bias 100 --image-type LIGHT --gain 5

capturafits-all: (anew) (fits-anew) (capturafits-edit) (capturafits-view) (capturafits-setup) (capturafits-register) (capturafits-sky) (export-all)  (sky-summary)


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
