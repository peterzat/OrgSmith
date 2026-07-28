# The OrgSmith generation environment: Python + WeasyPrint's native stack
# (Pango/Cairo) + LibreOffice for legacy .doc/.xls/.ppt conversion. `python -m
# orgsmith doctor` reports green inside this image. CI does NOT use it: the
# committed fixtures validate pure-Python with no LibreOffice, no network, no
# model, no key. This image is for GENERATING orgs (the model touchpoints run
# in the harness, not here).
FROM python:3.12-slim-bookworm

# WeasyPrint needs Pango/Cairo/GDK-PixBuf and fonts at render time; LibreOffice
# (headless) converts modern office files to their pre-2007 legacy binaries for
# recipes with legacy_ratio > 0. --no-install-recommends keeps the image lean.
RUN apt-get update && apt-get install --no-install-recommends -y \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libharfbuzz0b \
        libffi8 \
        shared-mime-info \
        fontconfig \
        fonts-dejavu-core \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /orgsmith
# Install dependencies first (pyproject + lock) for a cacheable layer, then the
# package. The lock reproduces the exact tested version set; drop it from the
# COPY to float within the pyproject >= bounds instead.
COPY pyproject.toml requirements.lock README.md ./
COPY orgsmith ./orgsmith
RUN pip install --no-cache-dir -r requirements.lock && pip install --no-cache-dir .

# The committed fleet and recipes are mounted or copied in at run time, not
# baked into the image, so the image stays a pure generation environment.
CMD ["python", "-m", "orgsmith", "doctor"]
