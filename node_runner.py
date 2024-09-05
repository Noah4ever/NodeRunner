import bpy
import pickle
import base64
import mathutils
import zlib


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
        if isinstance(input, (bpy.types.NodeSocketVector, bpy.types.NodeSocketColor)):
            data.append(serialize_attr(input, value))
        else:
            data.append(serialize_attr(node, value))
    return data


def deserialize_inputs(node, data):
    """Deserialize inputs"""
    for i, input in enumerate(data):
        if hasattr(node.inputs[i], "default_value"):
            node.inputs[i].default_value = input


def serialize_curve_mapping(node):
    data = {
        "black_level": serialize_attr(node, node.mapping.black_level),
        "clip_max_x": node.mapping.clip_max_x,
        "clip_max_y": node.mapping.clip_max_y,
        "clip_min_x": node.mapping.clip_min_x,
        "clip_min_y": node.mapping.clip_min_y,
        "curves": serialize_attr(node, node.mapping.curves),  # Serialzing curces
        "extend": node.mapping.extend,
        "tone": node.mapping.tone,
        "use_clip": node.mapping.use_clip,
        "white_level": serialize_attr(node, node.mapping.white_level),
    }
    return data


def deserialize_curve_mapping(node, data):
    node.mapping.black_level = data.get("black_level", (0.0, 0.0, 0.0))
    node.mapping.clip_max_x = data.get("clip_max_x", 0)
    node.mapping.clip_max_y = data.get("clip_max_y", 0)
    node.mapping.clip_min_x = data.get("clip_min_x", 0)
    node.mapping.clip_min_y = data.get("clip_min_y", 0)
    node.mapping.curves = data.get("curves", 0)
    node.mapping.extend = data.get("extend", 0)
    node.mapping.tone = data.get("tone", 0)
    node.mapping.use_clip = data.get("use_clip", 0)
    node.mapping.white_level = data.get("white_level", (0.0, 0.0, 0.0))
    pass


def serialize_curve_map(node, curve_map):
    data = {
        "points": serialize_attr(node, curve_map.points),
    }
    return data


def serialize_curve_map_point(node, curve_map_point):
    data = {
        "handle_type": curve_map_point.handle_type,
        "location": serialize_attr(node, curve_map_point.location),
        "select": curve_map_point.select,
    }
    return data


def serialize_attr(node, attr):
    data = attr
    if isinstance(data, mathutils.Color):
        data = serialize_color(data)  # Color
    elif isinstance(data, mathutils.Vector):
        data = serialize_vector(data)  # Vector
    elif isinstance(data, mathutils.Euler):
        data = serialize_euler(data)  # Euler
    elif isinstance(data, bpy.types.ColorRamp):
        data = serialize_color_ramp(node)  # Color Ramp
    elif isinstance(data, bpy.types.ColorMapping):
        data = serialize_color_mapping(node)  # Color Mapping
    elif isinstance(data, bpy.types.TexMapping):
        data = serialize_texture_mapping(node)  # Texture Mapping
    elif isinstance(data, bpy.types.CurveMapping):
        data = serialize_curve_mapping(node)  # Texture Mapping
    elif isinstance(data, bpy.types.CurveMap):
        data = serialize_curve_map(node, attr)  # Texture Mapping
    elif isinstance(data, bpy.types.CurveMapPoint):
        data = serialize_curve_map_point(node, attr)  # Texture Mapping
    elif isinstance(data, bpy.types.NodeSocketStandard):
        if hasattr(data, "default_value"):
            data = serialize_attr(node, data.default_value)
        else:
            data = None
    elif isinstance(data, bpy.types.bpy_prop_collection):
        result = []
        for element in data.values():
            result.append(serialize_attr(node, element))
        data = result
    elif isinstance(data, bpy.types.bpy_prop_array):
        result = []
        for element in data:
            result.append(serialize_attr(node, element))
        data = result
    try:
        pickle.dumps(data)
    except:
        print(
            "Serializing error on:",
            node.name,
            "with data:",
            data,
            "and type:",
            type(data),
        )
    return data


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
        node_dict[prop] = serialize_attr(node, attr)
    node_dict["type"] = node.bl_idname
    print("Finished serializing node: ", node.name)
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
        elif prop_name == "mapping":
            deserialize_curve_mapping(new_node, prop_value)
        else:
            setattr(new_node, prop_name, prop_value)
    return new_node


def encode_data(material, selected_node_names=None):
    node_tree = material.node_tree
    nodes = node_tree.nodes

    # Initialize empty data structure for nodes and links
    data = {"nodes": {}, "links": []}

    # Check if specific nodes are provided for export, otherwise use all nodes
    selected_nodes = (
        nodes
        if selected_node_names is None
        else [nodes[node_name] for node_name in selected_node_names]
    )

    # Save links (only for selected nodes or all if no nodes are selected)
    print("LINK serialization")
    for link in node_tree.links:
        if selected_node_names is None or (
            link.from_node.name in selected_node_names
            and link.to_node.name in selected_node_names
        ):
            data["links"].append(
                {
                    "from_node": link.from_node.name,
                    "to_node": link.to_node.name,
                    "from_socket": link.from_socket.name,
                    "to_socket": link.to_socket.name,
                }
            )

    print("NODE serialization")
    # Serialize selected nodes
    for node in selected_nodes:
        node_dict = serialize_node(node)
        data["nodes"][node.name] = node_dict

    # Encode data (links and nodes)
    compress_data = zlib.compress(pickle.dumps(data), 9)
    base64_encoded = base64.b64encode(compress_data).decode("utf-8")

    print(base64_encoded)
    print(len(base64_encoded))
    return base64_encoded


def decode_data(base64_encoded, material):
    node_tree = material.node_tree
    nodes = node_tree.nodes

    deserialized_data = pickle.loads(zlib.decompress(base64.b64decode(base64_encoded)))

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


# Add all possible nodes
import inspect

i = 0
location_x = 0
location_y = 0
for dad in dir(bpy.types):
    continue
    real_type = getattr(bpy.types, dad)
    if inspect.isclass(real_type) and issubclass(real_type, bpy.types.ShaderNode):
        try:
            i = i + 1
            node = bpy.context.object.active_material.node_tree.nodes.new(type=dad)
            node.width = 250
            node.location = (location_x, location_y)
            location_x += 300
            if location_x > 4000:
                location_x = 0
                location_y -= 450
        except:
            print("set this")
            pass


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
        self.report({"INFO"}, "Node Runner Export successful")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager

        # Get the active material from the context
        material = bpy.context.object.active_material
        if not material or not hasattr(material, "node_tree"):
            self.report({"ERROR"}, "No valid material with a node tree selected")
            return {"CANCELLED"}

        # Get selected nodes using bpy.context.selected_nodes
        selected_nodes = bpy.context.selected_nodes

        if not selected_nodes:
            self.report({"WARNING"}, "No nodes selected. Exporting all nodes.")
            selected_node_names = None  # Will default to all nodes in encode_data
        else:
            # Get the names of the selected nodes
            selected_node_names = [node.name for node in selected_nodes]

        # Encode data with the selected nodes
        self.my_node_runner_string = encode_data(
            material, selected_node_names=selected_node_names
        )
        # Trigger the props dialog to show the result
        return wm.invoke_props_dialog(self)


class NodeRunnerImportContextMenu(bpy.types.Operator):
    bl_idname = "object.node_runner_import_context_menu"
    bl_label = "Node Runner Import Context Menu"

    def execute(self, context):
        bpy.ops.object.node_runner_import("INVOKE_DEFAULT")
        self.report({"INFO"}, "Node Runner Import executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class NodeRunnerExportContextMenu(bpy.types.Operator):
    bl_idname = "object.node_runner_export_context_menu"
    bl_label = "Node Runner Export Context Menu"

    def execute(self, context):
        bpy.ops.object.node_runner_export("INVOKE_DEFAULT")
        self.report({"INFO"}, "Node Runner Export executed")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def menu_func_node_runner_export(self, context):
    self.layout.operator(
        NodeRunnerExportContextMenu.bl_idname, text="Node Runner Export"
    )


def menu_func_node_runner_import(self, context):
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
    bpy.types.NODE_MT_context_menu.append(menu_func_node_runner_import)
    bpy.types.NODE_MT_context_menu.append(menu_func_node_runner_export)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(menu_func_node_runner_export)
    bpy.types.NODE_MT_context_menu.remove(menu_func_node_runner_import)

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
