# SPDX-License-Identifier: GPL-3.0-or-later
# Preview: docker build --target build -t hdm-style . && docker run --rm -p 8765:8765 hdm-style
# Files:   docker build --build-arg BASE_URL=https://example.org --output dist .

FROM rust:1.100-trixie AS tools
RUN cargo install --locked spreet@0.14.0 build_pbf_glyphs@1.5.1

FROM python:3.15-slim-trixie AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=tools /usr/local/cargo/bin/spreet /usr/local/cargo/bin/build_pbf_glyphs /usr/local/bin/
WORKDIR /app
COPY . .
ARG BASE_URL=http://localhost:8765
RUN ./build.sh "$BASE_URL"
EXPOSE 8765
CMD ["python3", "-m", "http.server", "-d", "dist", "8765"]

FROM scratch AS dist
COPY --from=build /app/dist /
