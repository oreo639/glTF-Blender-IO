"""
 * ***** BEGIN GPL LICENSE BLOCK *****
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Contributor(s): Julien Duroure.
 *
 * ***** END GPL LICENSE BLOCK *****
 """

import bpy
from ...io.com.gltf2_io_node import *

class BlenderNode():

    @staticmethod
    def create(pynode, parent):

        # Blender attributes initialization
        self.blender_object = ""

        pynode.parent = parent
        if pynode.mesh:
            if pynode.name:
                pynode.gltf.log.info("Blender create Mesh node " + pynode.name)
            else:
                pynode.gltf.log.info("Blender create Mesh node")

            if pynode.name:
                name = pynode.name
            else:
                # Take mesh name if exist
                if pynode.mesh.name:
                    name = pynode.mesh.name
                else:
                    name = "Object_" + str(pynode.index)

            mesh = pynode.mesh.blender_create(parent)

            obj = bpy.data.objects.new(name, mesh)
            obj.rotation_mode = 'QUATERNION'
            bpy.data.scenes[pynode.gltf.blender_scene].objects.link(obj)

            # Transforms apply only if this mesh is not skinned
            # See implementation node of gltf2 specification
            if not (pynode.mesh and pynode.mesh.skin is not None):
                pynode.set_transforms(obj, parent)
            pynode.blender_object = obj.name
            BlenderNode.set_parent(pynode, obj, parent)

            pynode.mesh.blender_set_mesh(mesh, obj)

            for child in pynode.children:
                BlenderNode.create(child, pynode.index)

            return

        if pynode.camera:
            if pynode.name:
                pynode.gltf.log.info("Blender create Camera node " + pynode.name)
            else:
                pynode.gltf.log.info("Blender create Camera node")
            obj = pynode.camera.create_blender()
            pynode.set_transforms(obj, parent) #TODO default rotation of cameras ?
            pynode.blender_object = obj.name
            BlenderNode.set_parent(pynode, obj, parent)

            return


        if pynode.is_joint:
            if pynode.name:
                pynode.gltf.log.info("Blender create Bone node " + pynode.name)
            else:
                pynode.gltf.log.info("Blender create Bone node")
            # Check if corresponding armature is already created, create it if needed
            if pynode.gltf.skins[pynode.skin_id].blender_armature_name is None:
                pynode.gltf.skins[pynode.skin_id].create_blender_armature(parent)

            pynode.gltf.skins[pynode.skin_id].create_bone(pynode, parent)

            for child in pynode.children:
                BlenderNode.create(child, pynode.index)

            return

        # No mesh, no camera. For now, create empty #TODO

        if pynode.name:
            pynode.gltf.log.info("Blender create Empty node " + pynode.name)
            obj = bpy.data.objects.new(pynode.name, None)
        else:
            pynode.gltf.log.info("Blender create Empty node")
            obj = bpy.data.objects.new("Node", None)
        obj.rotation_mode = 'QUATERNION'
        bpy.data.scenes[pynode.gltf.blender_scene].objects.link(obj)
        pynode.set_transforms(obj, parent)
        pynode.blender_object = obj.name
        BlenderNode.set_parent(pynode, obj, parent)

        for child in pynode.children:
            BlenderNode.create(child, pynode.index)


    @staticmethod
    def set_parent(pynode, obj, parent):

        if parent is None:
            return

        for node in pynode.gltf.scene.nodes.values(): # TODO if parent is in another scene
            if node.index == parent:
                if node.is_joint == True:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.data.objects[node.blender_armature_name].select = True
                    bpy.context.scene.objects.active = bpy.data.objects[node.blender_armature_name]
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.data.objects[node.blender_armature_name].data.edit_bones.active = bpy.data.objects[node.blender_armature_name].data.edit_bones[node.blender_bone_name]
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select = True
                    bpy.data.objects[node.blender_armature_name].select = True
                    bpy.context.scene.objects.active = bpy.data.objects[node.blender_armature_name]
                    bpy.ops.object.parent_set(type='BONE', keep_transform=True)

                    return
                if node.blender_object:
                    obj.parent = bpy.data.objects[node.blender_object]
                    return

        pynode.gltf.log.error("ERROR, parent not found")
