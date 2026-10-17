"""Blender entrypoint; refuses CPU fallback. No network or credentials here."""
import bpy,sys,json,time
from pathlib import Path
from mathutils import Vector
p=Path(sys.argv[sys.argv.index('--')+1]); x=json.loads(p.read_text()); out=p.parent
start=time.monotonic()
is_blend=x.get('model_format','glb')=='blend'
if is_blend:
 bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
else:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'))
s=bpy.context.scene
meshes=[o for o in s.objects if o.type=='MESH']
if not meshes: raise RuntimeError('Scene contains no meshes')
if is_blend:
 if not s.camera or s.camera.type!='CAMERA': raise RuntimeError('BLEND requires an active camera')
 if bpy.data.libraries: raise RuntimeError('Linked libraries must be made local before submission')
 for image in bpy.data.images:
  if image.source not in ('GENERATED','VIEWER') and not image.packed_file and not len(image.packed_files):
   raise RuntimeError('All scene images must be packed')
 if s.sequence_editor and len(getattr(s.sequence_editor,'sequences_all',getattr(s.sequence_editor,'strips',[]))):
  raise RuntimeError('Sequencer input is not supported')
 if bpy.data.movieclips or bpy.data.sounds or bpy.data.volumes:
  raise RuntimeError('External media and volumes are not supported')
 # Output remains confined to the worker job, including compositor outputs.
 if s.use_nodes and s.node_tree:
  for node in s.node_tree.nodes:
   if node.type=='OUTPUT_FILE': raise RuntimeError('Compositor File Output nodes are not supported')
original={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in meshes}
preferences=bpy.context.preferences.addons['cycles'].preferences
preferences.compute_device_type='OPTIX'; preferences.get_devices()
gpus=[d for d in preferences.devices if d.type=='OPTIX']
if not gpus: raise RuntimeError('Real NVIDIA OptiX GPU required; CPU fallback disabled')
for d in preferences.devices: d.use=d.type=='OPTIX'
s.render.engine='CYCLES'; s.cycles.device='GPU'; s.cycles.samples=x['samples']; s.cycles.use_denoising=True
s.cycles.denoiser='OPTIX'
if not is_blend:
 s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
# Preserve imported PBR materials; assign neutral material only to unassigned meshes.
assumptions=[]
if not is_blend:
 for o in meshes:
  if not o.data.materials:
   mat=bpy.data.materials.get('Fallback neutral') or bpy.data.materials.new('Fallback neutral')
   mat.use_nodes=True; shader=mat.node_tree.nodes.get('Principled BSDF'); shader.inputs['Base Color'].default_value=(0.6,0.6,0.6,1); shader.inputs['Roughness'].default_value=.55
   o.data.materials.append(mat); assumptions.append('Neutral material: '+o.name)
 # Lighting is presentation-only; no objects pretending to be architectural fixtures.
 world=s.world or bpy.data.worlds.new('Studio environment'); s.world=world; world.use_nodes=True
 world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.65,0.75,1,1)
 world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
 sun=bpy.data.lights.new('Presentation daylight','SUN'); sun.energy=2; sun.angle=.12
 ob=bpy.data.objects.new(sun.name,sun); s.collection.objects.link(ob); ob.rotation_euler=(.5,-.4,-.7)
 bpy.ops.object.camera_add(location=x['camera']['position']); cam=bpy.context.object
 cam.rotation_euler=(Vector(x['camera']['target'])-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=x['camera'].get('lens',24); cam.data.clip_start=.02; s.camera=cam
 fill=bpy.data.lights.new('Presentation soft fill','AREA'); fill.energy=150; fill.shape='DISK'; fill.size=3
 ob=bpy.data.objects.new(fill.name,fill); s.collection.objects.link(ob); ob.location=cam.location; ob.rotation_euler=cam.rotation_euler
 assumptions+=['Generic daylight and camera-side soft fill; not a measured lighting simulation','No furniture added; original geometry and assigned PBR materials preserved','Metres per glTF specification; compare with project reference dimensions']
else:
 assumptions.append('Packed Blender scene: original camera, world, lights, units and materials retained')
s.render.resolution_x,s.render.resolution_y=x['resolution']; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.filepath=str(out/'render.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'project.blend'))
bpy.ops.render.render(write_still=True)
assert original=={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in meshes}
report={'gpu_devices':[d.name for d in gpus],'engine':'CYCLES','device':'GPU','compute':'OPTIX','blender':bpy.app.version_string,'model_format':x.get('model_format','glb'),'mesh_objects':len(meshes),'seconds':time.monotonic()-start,'assumptions':assumptions,'resolution':x['resolution']}
(out/'report.json').write_text(json.dumps(report,indent=2))
