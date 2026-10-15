# Official RunPod worker-template base; build in RunPod GitHub builder.
FROM runpod/base:0.6.3-cuda11.8.0
ARG BLENDER_VERSION=4.5.14
ARG BLENDER_SHA256=9ba871ff2ecd36526b77432745980b7e6664ecd0c7ca11c48849073dcfe06da3
RUN apt-get update && apt-get install -y --no-install-recommends curl xz-utils libxrender1 libxi6 libxfixes3 libxkbcommon0 libsm6 libgl1 libegl1 libgomp1 && rm -rf /var/lib/apt/lists/*
RUN curl -fL "https://download.blender.org/release/Blender4.5/blender-${BLENDER_VERSION}-linux-x64.tar.xz" -o /tmp/blender.tar.xz && printf '%s  /tmp/blender.tar.xz\n' "$BLENDER_SHA256" | sha256sum -c - && mkdir /opt/blender && tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && rm /tmp/blender.tar.xz
RUN uv pip install --system 'runpod>=1.7,<2' 'requests>=2.32,<3'
ENV NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics
WORKDIR /worker
COPY contract.py handler.py render.py ./
CMD ["python3", "-u", "/worker/handler.py"]
