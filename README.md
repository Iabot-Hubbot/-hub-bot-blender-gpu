# hub-bot-blender-gpu

Experimental RunPod queue worker. Not yet GPU-tested or production integrated.

Build from this repository using RunPod GitHub integration, Dockerfile at repository root. Blender 4.5.14 official Linux distribution is installed at build time with verified SHA256; no runtime installation. No Docker installation on Daytona is required.

Endpoint settings: queue based, min workers 0, max workers 1, 1 NVIDIA 24GB GPU per worker, idle timeout 5 seconds, execution timeout 1800000 milliseconds. Verify actual provider rates before starting. This repository does not enforce an account-wide monetary budget.

Required environment: STORAGE_ALLOWED_HOSTS, a comma-separated list of explicitly permitted private object storage hostnames. No RunPod account API key belongs in the worker image.

Input: model_url (HTTPS signed download), model_sha256, quality (preview or final), camera {position:[x,y,z], target:[x,y,z], lens:24}, output_urls {png,blend,report} (HTTPS signed PUT URLs). Units metres. Preview 960x540; final defaults 1920x1080 and requires approved:true. Caller must enforce authorization, file ownership, spend limits and approvals independently; the approved flag is not an authorization boundary.

Worker rejects CPU fallback and requires OptiX. It imports the existing geometry, retains PBR materials, adds presentation lights and a camera, saves project.blend, renders PNG and uploads outputs with a diagnostic report. No furniture is generated. Generic lighting and neutral materials when absent are documented assumptions, not measured architectural specifications.

Run tests: python3 -m unittest test_contract.py

Outstanding: container build verification, real GPU render, private storage provisioning and signed PUT compatibility, deployment/API orchestration, durable spend accounting, tenant isolation in trusted caller, cancellation, scale-to-zero verification, and Hermes tool registration. Unit tests do not verify these requirements.

## Packed Blender scenes

Set `model_format: "blend"` to render a self-contained BLEND. Default remains
`glb` for existing callers. The active scene must contain meshes and an active
camera. Its camera, lights, world, material nodes, units and color management are
retained. Job resolution, samples and GPU execution policy still apply.
Pack image textures and HDRIs, make linked libraries local, and remove external
media and compositor File Output nodes. Auto-execution of embedded scripts is
disabled. This is not a sandbox for arbitrary untrusted Blender content; the
trusted caller must enforce ownership and access. Render on an isolated worker.
The transfer service must offer `model.blend`; do not send BLEND to old workers.
A new GitHub release triggers the configured RunPod build. A successful unit
test or release publication does not establish completed deployment or a GPU render.
