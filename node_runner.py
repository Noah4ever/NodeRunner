import bpy
import pickle
import base64
import mathutils


def serialize_color(color):
    """Serialize color"""
    return list(color)


def serialize_vector(vector):
    """Serialize vector"""
    return list(vector)


def serialize_euler(euler):
    """Serialize euler"""
    return list(euler)


def serialize_color_ramp(node):
    """Serialize color ramp"""
    data = {
        "color_mode": node.color_ramp.color_mode,  # default RGB
        "elements": [],
        "hue_interpolation": node.color_ramp.hue_interpolation,  # default NEAR
        "interpolation": node.color_ramp.interpolation,  # default LINEAR
    }
    for element in node.color_ramp.elements:
        data["elements"].append(
            {"position": element.position, "color": list(element.color)}
        )
    return data


def deserialize_color_ramp(node, data):
    """Deserialize color ramp"""
    node.color_ramp.color_mode = data.get("color_mode", 0)
    node.color_ramp.hue_interpolation = data.get("hue_interpolation", 1)
    node.color_ramp.interpolation = data.get("interpolation", 2)

    for i, element_data in enumerate(data["elements"]):
        element = node.color_ramp.elements[i]
        element.position = element_data["position"]
        element.color = element_data["color"]


def serialize_color_mapping(node):
    """Serialize color mapping"""
    data = {
        "blend_color": serialize_color(node.color_mapping.blend_color),
        "blend_factor": node.color_mapping.blend_factor,
        "blend_type": node.color_mapping.blend_type,
        "brightness": node.color_mapping.brightness,
        "color_ramp": serialize_color_ramp(node.color_mapping),
        "contrast": node.color_mapping.contrast,
        "saturation": node.color_mapping.saturation,
        "use_color_ramp": node.color_mapping.use_color_ramp,
    }
    return data


def deserialize_color_mapping(node, data):
    """Deserialize color mapping"""
    node.color_mapping.blend_color = data.get("blend_color", (0.0, 0.0, 0.0))
    node.color_mapping.blend_factor = data.get("blend_factor", 0.0)
    node.color_mapping.blend_type = data.get("blend_type", 0)
    node.color_mapping.brightness = data.get("brightness", 0.0)
    deserialize_color_ramp(node.color_mapping, data["color_ramp"])
    node.color_mapping.contrast = data.get("contrast", 0)
    node.color_mapping.saturation = data.get("saturation", 0)
    node.color_mapping.use_color_ramp = data.get("use_color_ramp", 0)


def serialize_texture_mapping(node):
    """Serialize texture mapping"""
    data = {
        "mapping": node.texture_mapping.mapping,
        "mapping_x": node.texture_mapping.mapping_x,
        "mapping_y": node.texture_mapping.mapping_y,
        "mapping_z": node.texture_mapping.mapping_z,
        "max": serialize_vector(node.texture_mapping.max),
        "min": serialize_vector(node.texture_mapping.min),
        "rotation": serialize_vector(node.texture_mapping.rotation),
        "scale": serialize_vector(node.texture_mapping.scale),
        "translation": serialize_vector(node.texture_mapping.translation),
        "use_max": node.texture_mapping.use_max,
        "use_min": node.texture_mapping.use_min,
        "vector_type": node.texture_mapping.vector_type,
    }
    return data


def deserialize_texture_mapping(node, data):
    """Deserialize texture mapping"""
    node.texture_mapping.mapping = data.get("mapping", 0)
    node.texture_mapping.mapping_x = data.get("mapping_x", 0)
    node.texture_mapping.mapping_y = data.get("mapping_y", 0)
    node.texture_mapping.mapping_z = data.get("mapping_z", 0)
    node.texture_mapping.max = data.get("max", (0.0, 0.0, 0.0))
    node.texture_mapping.min = data.get("min", (0.0, 0.0, 0.0))
    node.texture_mapping.rotation = data.get("rotation", (0.0, 0.0, 0.0))
    node.texture_mapping.scale = data.get("scale", (0.0, 0.0, 0.0))
    node.texture_mapping.translation = data.get("translation", (0.0, 0.0, 0.0))
    node.texture_mapping.use_max = data.get("use_max", False)
    node.texture_mapping.use_min = data.get("use_min", False)
    node.texture_mapping.vector_type = data.get("vector_type", 0)


def serialize_inputs(node):
    """Serialize inputs"""
    data = []

    for input in node.inputs:
        if not hasattr(input, "default_value"):
            continue

        value = input.default_value

        if isinstance(input, bpy.types.NodeSocketVector):
            data.append(serialize_vector(value))
        elif isinstance(input, bpy.types.NodeSocketColor):
            data.append(serialize_color(value))
        elif isinstance(value, mathutils.Euler):
            data.append(serialize_euler(value))
        else:
            data.append(value)
    return data


def deserialize_inputs(node, data):
    """Deserialize inputs"""
    for i, input in enumerate(data):
        if hasattr(node.inputs[i], "default_value"):
            node.inputs[i].default_value = input


def serialize_node(node):
    """Serialize node properties"""
    exclude_props = [
        "__doc__",
        "__module__",
        "__slots__",
        "bl_description",
        "bl_height_default",
        "bl_height_max",
        "bl_height_min",
        "bl_icon",
        "bl_idname",
        "bl_label",
        "bl_rna",
        "bl_static_type",
        "bl_width_default",
        "bl_width_max",
        "bl_width_min",
        "dimensions",
        "draw_buttons",
        "draw_buttons_ext",
        "hide",
        "input_template",
        "internal_links",
        "is_registered_node_type",
        "label",
        "output_template",
        "poll",
        "poll_instance",
        "rna_type",
        "select",
        "socket_value_update",
        "type",
        "update",
        "use_custom_color",
        "outputs",
    ]

    node_dict = {}

    for prop in [p for p in dir(node) if p not in exclude_props]:
        attr = getattr(node, prop)
        if isinstance(attr, mathutils.Color):
            node_dict[prop] = serialize_color(attr)  # Color
        elif isinstance(attr, mathutils.Vector):
            node_dict[prop] = serialize_vector(attr)  # Vector
        elif isinstance(attr, bpy.types.ColorRamp):
            node_dict[prop] = serialize_color_ramp(node)  # Color Ramp
        elif isinstance(attr, bpy.types.ColorMapping):
            node_dict[prop] = serialize_color_mapping(node)  # Color Mapping
        elif isinstance(attr, bpy.types.TexMapping):
            node_dict[prop] = serialize_texture_mapping(node)  # Texture Mapping
        elif prop == "inputs":
            node_dict[prop] = serialize_inputs(node)  # Inputs
        else:
            node_dict[prop] = attr

    node_dict["type"] = node.bl_idname

    return node_dict


def deserialize_node(node_data, nodes):
    """Deserialize node properties and add new node"""
    new_node = nodes.new(type=node_data["type"])  # Create new node

    readonly_props = ["type"]
    for prop_name, prop_value in node_data.items():
        if prop_name in readonly_props:
            continue

        # Special handling for complex types
        if prop_name == "color_ramp":
            deserialize_color_ramp(new_node, prop_value)
        elif prop_name == "color_mapping":
            deserialize_color_mapping(new_node, prop_value)
        elif prop_name == "texture_mapping":
            deserialize_texture_mapping(new_node, prop_value)
        elif prop_name == "inputs":
            deserialize_inputs(new_node, prop_value)
        else:
            setattr(new_node, prop_name, prop_value)
    return new_node


# TODO: Add support for letting the user select the nodes to export
def encode_data(material):
    node_tree = material.node_tree
    nodes = node_tree.nodes

    data = {"nodes": {}, "links": []}

    # Save links
    for link in node_tree.links:
        data["links"].append(
            {
                "from_node": link.from_node.name,
                "to_node": link.to_node.name,
                "from_socket": link.from_socket.name,
                "to_socket": link.to_socket.name,
            }
        )

    # Serialize nodes
    for node in nodes:
        node_dict = serialize_node(node)
        data["nodes"][node.name] = node_dict

    # Encode data (links and nodes)
    serialized_data = pickle.dumps(data)
    base64_encoded = base64.b64encode(serialized_data).decode("utf-8")
    return base64_encoded


def decode_data(base64_encoded, material):
    node_tree = material.node_tree
    nodes = node_tree.nodes

    deserialized_data = pickle.loads(base64.b64decode(base64_encoded))

    node_names = {}

    # Save new node with name for linking
    for node_name, node_data in deserialized_data["nodes"].items():
        node_names[node_name] = deserialize_node(
            node_data, nodes
        )  # Decode node and return new node

    # Apply links
    for link_data in deserialized_data["links"]:
        from_node = node_names[link_data["from_node"]]
        output_socket = from_node.outputs.get(link_data["from_socket"])
        to_node = node_names[link_data["to_node"]]
        input_socket = to_node.inputs.get(link_data["to_socket"])
        node_tree.links.new(input_socket, output_socket)


for obj in bpy.data.objects:
    continue
    if obj.name == "Cube":
        material = obj.active_material
        node_tree = material.node_tree
        nodes = node_tree.nodes

        data = {"nodes": {}, "links": []}

        # Save links
        for link in node_tree.links:
            data["links"].append(
                {
                    "from_node": link.from_node.name,
                    "to_node": link.to_node.name,
                    "from_socket": link.from_socket.name,
                    "to_socket": link.to_socket.name,
                }
            )

        # Encode nodes
        for node in nodes:
            node_dict = serialize_node(node)
            data["nodes"][node.name] = node_dict

        # Serialize data (links and nodes)
        serialized_data = pickle.dumps(data)
        base64_encoded = base64.b64encode(serialized_data).decode("utf-8")
        print(base64_encoded)
        print("Encoded Nodes Length", len(base64_encoded))

        # continue

        # deserialize data
        deserialized_data = pickle.loads(base64.b64decode(base64_encoded))

        node_names = {}

        # Save new node with name for linking
        for node_name, node_data in deserialized_data["nodes"].items():
            node_names[node_name] = deserialize_node(
                node_data, nodes
            )  # Decode node and return new node

        # Apply links
        for link_data in deserialized_data["links"]:
            from_node = node_names[link_data["from_node"]]
            output_socket = from_node.outputs.get(link_data["from_socket"])
            to_node = node_names[link_data["to_node"]]
            input_socket = to_node.inputs.get(link_data["to_socket"])
            node_tree.links.new(input_socket, output_socket)


class NodeRunnerImport(bpy.types.Operator):
    bl_idname = "object.node_runner_import"
    bl_label = "Node Runner Import"
    bl_options = {"REGISTER", "UNDO"}

    my_node_runner_string: bpy.props.StringProperty(
        name="Node Runner Hash",
        default="",
        description="Node Runner Hash",
    )  # type: ignore

    def execute(self, context):
        decode_data(self.my_node_runner_string, bpy.context.material)
        self.report({"INFO"}, "Node Runner Import Main executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class NodeRunnerExport(bpy.types.Operator):
    bl_idname = "object.node_runner_export"
    bl_label = "Node Runner Export"
    bl_options = {"REGISTER", "UNDO"}

    my_node_runner_string: bpy.props.StringProperty(
        name="Node Runner Hash String",
        default="",
        description="Node Runner Hash String",
    )  # type: ignore

    def execute(self, context):
        self.my_node_runner_string = "TEST"
        # get current material
        self.report({"INFO"}, "Node Runner Export Main executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        self.my_node_runner_string = encode_data(bpy.context.material)
        return wm.invoke_props_dialog(self)


class NodeRunnerImportContextMenu(bpy.types.Operator):
    bl_idname = "object.node_runner_import_context_menu"
    bl_label = "Node Runner Import"

    def execute(self, context):
        bpy.ops.object.node_runner_import("INVOKE_DEFAULT")
        self.report({"INFO"}, "Node Runner Import executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class NodeRunnerExportContextMenu(bpy.types.Operator):
    bl_idname = "object.node_runner_export_context_menu"
    bl_label = "Node Runner Export"

    def execute(self, context):
        bpy.ops.object.node_runner_export("INVOKE_DEFAULT")
        self.report({"INFO"}, "Node Runner Export executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def menu_func_NodeRunnerExport(self, context):
    self.layout.operator(
        NodeRunnerExportContextMenu.bl_idname, text="Node Runner Export"
    )


def menu_func_NodeRunnerImport(self, context):
    self.layout.operator(
        NodeRunnerImportContextMenu.bl_idname, text="Node Runner Import"
    )


# Register the operator
def register():
    bpy.utils.register_class(NodeRunnerImportContextMenu)
    bpy.utils.register_class(NodeRunnerExportContextMenu)
    bpy.utils.register_class(NodeRunnerImport)
    bpy.utils.register_class(NodeRunnerExport)

    # Add it to the Shader Editor context menu
    bpy.types.NODE_MT_context_menu.append(menu_func_NodeRunnerImport)
    bpy.types.NODE_MT_context_menu.append(menu_func_NodeRunnerExport)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(menu_func_NodeRunnerExport)
    bpy.types.NODE_MT_context_menu.remove(menu_func_NodeRunnerImport)

    bpy.utils.unregister_class(NodeRunnerExport)
    bpy.utils.unregister_class(NodeRunnerImport)
    bpy.utils.unregister_class(NodeRunnerExportContextMenu)
    bpy.utils.unregister_class(NodeRunnerImportContextMenu)


if __name__ == "__main__":
    try:
        unregister()  # Ensure any previously registered classes are unregistered first
    except Exception as e:
        print(f"Unregister failed: {e}")
    register()
