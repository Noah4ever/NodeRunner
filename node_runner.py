"""
This module adds the function to import and export
shader nodes from Blender.

It exports the shader nodes to a compressed and base64
encoded string that can be easily shared via a text
messager or comments in a video.
"""

import binascii
import pickle
import zlib
import base64
import bpy
import mathutils


def serialize_color(color):
    """Serialize color

    Args:
      color: Color to serialize
    Returns:
      Serialized color as list
    """
    return list(color)


def serialize_vector(vector):
    """Serialize vector

    Args:
      vector: Vector to serialize
    Returns:
      Serialized vector as list
    """
    return list(vector)


def serialize_euler(euler):
    """Serialize euler

    Args:
      euler: Euler to serialize
    Returns:
      Serialized euler as list
    """
    return list(euler)


def serialize_color_ramp(node):
    """Serialize color ramp

    Args:
      node: Node to serialize
    Returns:
      Serialized color ramp data
    """
    data = {
        "color_mode": node.color_ramp.color_mode,
        "elements": [],
        "hue_interpolation": node.color_ramp.hue_interpolation,
        "interpolation": node.color_ramp.interpolation,
    }
    for element in node.color_ramp.elements:
        data["elements"].append(
            {"position": element.position, "color": list(element.color)}
        )
    return data


def deserialize_color_ramp(node, data):
    """Deserialize color ramp

    Args:
      node: Node to set color ramp data
      data: Data to deserialize
    Returns:
    """
    node.color_ramp.color_mode = data.get("color_mode", 0)
    node.color_ramp.hue_interpolation = data.get("hue_interpolation", 1)
    node.color_ramp.interpolation = data.get("interpolation", 2)

    for i, element_data in enumerate(data["elements"]):
        element = node.color_ramp.elements[i]
        element.position = element_data["position"]
        element.color = element_data["color"]


def serialize_color_mapping(node):
    """Serialize color mapping

    Args:
      node: Node to serialize
    Returns:
      Serialized color mapping data
    """
    return {
        "blend_color": serialize_color(node.color_mapping.blend_color),
        "blend_factor": node.color_mapping.blend_factor,
        "blend_type": node.color_mapping.blend_type,
        "brightness": node.color_mapping.brightness,
        "color_ramp": serialize_color_ramp(node.color_mapping),
        "contrast": node.color_mapping.contrast,
        "saturation": node.color_mapping.saturation,
        "use_color_ramp": node.color_mapping.use_color_ramp,
    }


def deserialize_color_mapping(node, data):
    """Deserialize color mapping

    Args:
      node: Node to set color mapping data
      data: Data to deserialize
    Returns:
    """
    node.color_mapping.blend_color = data.get("blend_color", (0.0, 0.0, 0.0))
    node.color_mapping.blend_factor = data.get("blend_factor", 0.0)
    node.color_mapping.blend_type = data.get("blend_type", 0)
    node.color_mapping.brightness = data.get("brightness", 0.0)
    deserialize_color_ramp(node.color_mapping, data["color_ramp"])
    node.color_mapping.contrast = data.get("contrast", 0)
    node.color_mapping.saturation = data.get("saturation", 0)
    node.color_mapping.use_color_ramp = data.get("use_color_ramp", 0)


def serialize_texture_mapping(node):
    """Serialize texture mapping

    Args:
      node: Node to serialize
    Returns:
      Serialized texture mapping data
    """
    return {
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


def deserialize_texture_mapping(node, data):
    """Deserialize texture mapping

    Args:
      node: Node to set texture mapping data
      data: Data to deserialize
    Returns:
    """
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


def deserialize_inputs(node, data):
    """Deserialize inputs

    Check if the node has inputs and set the input values.

    Args:
      node: Node to set inputs
      data: Data to deserialize
    Returns:
    """
    # Inputs of NodeGroupInput and NodeGroupOutput cannot be set on the node
    # but need to be set on the group instead
    if isinstance(node, (bpy.types.NodeGroupInput, bpy.types.NodeGroupOutput)):
        return

    for i, input_value in enumerate(data):
        if (
            input_value is not None
            and hasattr(node, "inputs")
            and len(node.inputs) > 0
            and hasattr(node.inputs[i], "default_value")
        ):
            node.inputs[i].default_value = input_value


def deserialize_outputs(node, data):
    """Deserialize outputs

    Check if the node has outputs and set the output values.

    Args:
      node: Node to set outputs
      data: Data to deserialize
    Returns:
    """
    # Output of NodeGroupInput and NodeGroupOutput cannot be set on the node
    # but need to be set on the group instead
    if isinstance(node, (bpy.types.NodeGroupInput, bpy.types.NodeGroupOutput)):
        return

    for i, output in enumerate(data):
        if (
            output is not None
            and hasattr(node, "outputs")
            and len(node.outputs) > 0
            and hasattr(node.outputs[i], "default_value")
        ):
            node.outputs[i].default_value = output


def serialize_curve_mapping(node):
    """Serialize curve mapping

    Args:
      node: Node to serialize
    Returns:
      Serialized curve mapping data
    """
    return {
        "black_level": serialize_attr(node, node.mapping.black_level),
        "clip_max_x": node.mapping.clip_max_x,
        "clip_max_y": node.mapping.clip_max_y,
        "clip_min_x": node.mapping.clip_min_x,
        "clip_min_y": node.mapping.clip_min_y,
        "curves": serialize_attr(node, node.mapping.curves), 
        "extend": node.mapping.extend,
        "tone": node.mapping.tone,
        "use_clip": node.mapping.use_clip,
        "white_level": serialize_attr(node, node.mapping.white_level),
    }


def deserialize_curve_mapping(node, data):
    """Deserialize curve mapping

    Args:
      node: Node to set curve mapping data
      data: Data to deserialize
    Returns:
    """
    node.mapping.black_level = data.get("black_level", (0.0, 0.0, 0.0))

    i = 0
    for curve_map in data.get("curves", 0):
        
        j = 0
        # Set first and last point because by default there are two points in a new curve
        for point in node.mapping.curves[i].points:
            point.location = curve_map.get("points")[j].get("location", (0.0, 0.0))
            j -= 1

        # Create and set the rest of the points
        for k in  range(1, len(curve_map.get("points")) - 1):
            location = curve_map.get("points")[k].get("location", (0.0, 0.0))
            node.mapping.curves[i].points.new(location[0], location[1])
        i += 1

    node.mapping.clip_max_x = data.get("clip_max_x", 0)
    node.mapping.clip_max_y = data.get("clip_max_y", 0)
    node.mapping.clip_min_x = data.get("clip_min_x", 0)
    node.mapping.clip_min_y = data.get("clip_min_y", 0)

    node.mapping.extend = data.get("extend", 0)
    node.mapping.tone = data.get("tone", 0)
    node.mapping.use_clip = data.get("use_clip", 0)
    node.mapping.white_level = data.get("white_level", (0.0, 0.0, 0.0))


def serialize_curve_map(node, curve_map: bpy.types.CurveMap):
    """Serialize curve map

    Args:
      node: Node to serialize
      curve_map: Curve map to serialize
      curve_map: bpy.types.CurveMap:
    Returns:
      Serialized curve map data
    """
    return {
        "points": serialize_attr(node, curve_map.points),
    }


def serialize_curve_map_point(node, curve_map_point: bpy.types.CurveMapPoint):
    """Serialize curve map point

    Args:
      node: Node to serialize
      curve_map_point: Curve map point to serialize
      curve_map_point: bpy.types.CurveMapPoint:
    Returns:
      Serialized curve map point data
    """
    return {
        "handle_type": curve_map_point.handle_type,
        "location": serialize_attr(node, curve_map_point.location),
        "select": curve_map_point.select,
    }


def serialize_image(image: bpy.types.Image):
    """Serialize image.

    Args:
      node: Node to serialize.
      image(bpy.types.Image): Image to serialize.
      image: bpy.types.Image:
    Returns:
      dict: Serialized image data.
    """
    return {
        "name": image.name,
    }


def deserialize_image(node, data):
    """Deserialize image

    Args:
      node: Node to set image data
      data: Data to deserialize
    Returns:
    """
    image = next(
        (obj for obj in bpy.context.blend_data.images if obj.name == data.get("name")),
        None,
    )
    if not image:
        return
    node.image = image


def serialize_text_line(text: bpy.types.TextLine):
    """Serialize text line

    Args:
        text: Text line to serialize
    Returns:
        Serialized text line data
    """
    return {
        "body": text.body,
    }


def deserialize_text_line(text_line, data):
    """Deserialize text line

    Args:
      node: Node to set text line data
      data: Data to deserialize
    Returns:
    """
    text_line.body = data.get("body", "")


def serialize_text(text: bpy.types.Text):
    """Serialize text

    Args:
      text: Text to serialize
    Returns:
      Serialized text data
    """

    serializes_lines = []
    for line in text.lines:
        serializes_lines.append(serialize_text_line(line))

    return {
        "current_character": text.current_character,
        "current_line": serialize_text_line(text.current_line),
        "current_line_index": text.current_line_index,
        "filepath": text.filepath,
        "indentation": text.indentation,
        "lines": serializes_lines,
        "select_end_character": text.select_end_character,
        "select_end_line_index": text.select_end_line_index,
        "use_module": text.use_module,
    }


def deserialize_text(node, data):
    """Deserialize text

    Args:
      node: Node to set text data
      data: Data to deserialize
    Returns:
    """

    # if data.filepath can be found in bpy.data.texts, use that text
    text = next(
        (
            obj
            for obj in bpy.context.blend_data.texts
            if obj.filepath == data.get("filepath")
        ),
        None,
    )
    if text:
        return text

    text = bpy.data.texts.new(name="Text")
    text.current_character = data.get("current_character", 0)
    deserialize_text_line(text.current_line, data.get("current_line", {}))
    text.current_line_index = data.get("current_line_index", 0)
    text.filepath = data.get("filepath", "")
    text.indentation = data.get("indentation", 0)
    text.select_end_character = data.get("select_end_character", 0)
    text.select_end_line_index = data.get("select_end_line_index", 0)
    text.use_module = data.get("use_module", False)

    return text


def serialize_node_frame(node: bpy.types.NodeFrame):
    """Serialize node frame

    Args:
      node: Node to serialize
    Returns:
      Serialized node frame data
    """
    return {
        "label_size": node.label_size,
        "shrink": node.shrink,
        "text": serialize_text(node.text),
    }


def serialize_attr(node, attr):
    """Serialize attribute of a node

    Check the type of the attribute and serialize it accordingly.
    If the attribute is a complex type, call the corresponding serialization function.
    Prints an error message if the serialization fails.

    Args:
      node: Node to serialize
      attr: Attribute to serialize
    Returns:
      Serialized attribute data
    """
    serializers = {
        mathutils.Color: serialize_color,
        mathutils.Vector: serialize_vector,
        mathutils.Euler: serialize_euler,
        bpy.types.ColorRamp: lambda d: serialize_color_ramp(node),
        bpy.types.ShaderNodeTree: lambda d: serialize_node_tree(node.node_tree),
        bpy.types.ColorMapping: lambda d: serialize_color_mapping(node),
        bpy.types.TexMapping: lambda d: serialize_texture_mapping(node),
        bpy.types.CurveMapping: lambda d: serialize_curve_mapping(node),
        bpy.types.CurveMap: lambda d: serialize_curve_map(node, d),
        bpy.types.CurveMapPoint: lambda d: serialize_curve_map_point(node, d),
        bpy.types.Image: serialize_image,
        bpy.types.ImageUser: lambda d: {},
        bpy.types.NodeFrame: lambda d: serialize_node_frame(node, d),
        bpy.types.Text: lambda d: serialize_text(node.script),
        bpy.types.Object: lambda d: None,
        bpy.types.NodeSocketStandard: lambda d: (
            serialize_attr(node, d.default_value)
            if hasattr(d, "default_value")
            else None
        ),
        bpy.types.bpy_prop_collection: lambda d: [
            serialize_attr(node, element) for element in d.values()
        ],
        bpy.types.bpy_prop_array: lambda d: [
            serialize_attr(node, element) for element in d
        ],
    }

    for data_type, serializer in serializers.items():
        if isinstance(attr, data_type):
            return serializer(attr)
    try:
        pickle.dumps(attr)  # Try to pickle dump to get error message
    except (pickle.PicklingError, TypeError, AttributeError, EOFError):
        print(
            "[ERROR] Serializing error on:",
            node.name,
            "with data:",
            attr,
            "and type:",
            type(attr),
        )
    return attr


def serialize_node(node):
    """Serialize node properties

    Loop through all properties of the node and serialize them and add them to a dictionary.

    Args:
      node: Node to serialize
    Returns:
      Serialized node dictionary
    """
    exclude_props = [
        "__doc__",
        "__module__",
        "__slots__",
        "__slotnames__",
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
        "cache_point_density",
        "calc_point_density",
        "calc_point_density_minmax",
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
    ]

    node_dict = {}

    for prop in [p for p in dir(node) if p not in exclude_props]:
        attr = getattr(node, prop)
        if attr is None:
            continue
        if prop == "parent":
            # Serialize parent node name for NodeFrame's
            node_dict["parent"] = node.parent.name
            continue
        node_dict[prop] = serialize_attr(node, attr)
    node_dict["type"] = node.bl_idname
    node_dict["label"] = node.label
    return node_dict


def deserialize_node(node_data, nodes):
    """Deserialize node

    Loop through all properties of the node data and deserialize them accordingly.

    Args:
      node_data: Node data to deserialize
      nodes: Nodes to add the new node to
    Returns:
      New node
    """
    if node_data["type"] == "NodeUndefined":
        return None

    new_node = nodes.new(type=node_data["type"])  # Create new node
    new_node.label = node_data["label"]  # Set node label

    # Node tree has to be done before other properties like inputs and outputs
    if "node_tree" in node_data:
        new_node.node_tree = bpy.data.node_groups.new(node_data["node_tree"]["name"], "ShaderNodeTree")
        deserialize_node_tree(new_node.node_tree, node_data["node_tree"])
        node_data.pop("node_tree")

    readonly_props = ["type", "image_user"]
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
        elif prop_name == "mapping":
            deserialize_curve_mapping(new_node, prop_value)
        elif prop_name == "image":
            deserialize_image(new_node, prop_value)
        elif prop_name == "inputs":
            deserialize_inputs(new_node, prop_value)
        elif prop_name == "outputs":
            deserialize_outputs(new_node, prop_value)
        elif prop_name == "script":
            new_node.script = deserialize_text(new_node, prop_value)
        elif prop_name == "parent" and prop_value in nodes:
            new_node.parent = nodes[prop_value]
        else:
            setattr(new_node, prop_name, prop_value)
    return new_node


def serialize_node_tree(node_tree, selected_node_names=None):
    """Serialize node tree

    Loop through all nodes and links of the node tree and serialize them.

    Args:
      node_tree: Node tree to serialize
      selected_node_names: Selected node names (Default value = None)
    Returns:
      Serialized node tree data
    """
    nodes = node_tree.nodes

    # Initialize empty data structure for nodes and links
    data = {"nodes": {}, "links": []}
    selected_nodes = []
    if selected_node_names is None:
        selected_nodes = list(node_tree.nodes)
    else:
        for node_name in selected_node_names:
            if node_name in nodes:
                selected_nodes.append(nodes[node_name])
            
    # Serialize selected nodes
    for node in selected_nodes:
        node_dict = serialize_node(node)
        data["nodes"][node.name] = node_dict

    # Save links (only for selected nodes)
    for link in node_tree.links:
        if link.from_node in selected_nodes and link.to_node in selected_nodes:
            data["links"].append(
                {
                    "from_node": link.from_node.name,
                    "to_node": link.to_node.name,
                    "from_socket": link.from_socket.name,
                    "from_socket_type": link.from_socket.bl_idname,
                    "from_socket_identifier": link.from_socket.identifier,
                    "to_socket": link.to_socket.name,
                    "to_socket_type": link.to_socket.bl_idname,
                    "to_socket_identifier": link.to_socket.identifier,
                }
            )
    data["name"] = node_tree.name
    return data


def get_node_socket_base_type(socket_type):
    """Get base type of node socket.

    This is used to create new sockets on the ShaderNodeGroup.
    Only base types can be used for creating a new socket on the ShaderNodeGroup.

    Args:
      type: str
    Returns:
      str: Base type of node socket
    """
    usable_type_array = [
        "NodeSocketBool",
        "NodeSocketVector",
        "NodeSocketInt",
        "NodeSocketShader",
        "NodeSocketFloat",
        "NodeSocketColor",
    ]
    for usable_type in usable_type_array:
        if usable_type in socket_type:
            return usable_type
    return usable_type_array[0]


def get_socket_by_identifier(node, identifier, socket_type="INPUT"):
    """Get socket by identifier

    Loops through the input or output sockets of a node and
    returns the socket with the given identifier.

    Args:
      node: Node to get the socket from
      identifier: Identifier of the socket
      socket_type:  (Default value = "INPUT")
    Returns:
      Socket with the given identifier
    """
    # Select input or output sockets
    sockets = node.inputs if socket_type.upper() == "INPUT" else node.outputs

    # Find the socket by identifier
    for socket in sockets:
        if socket.identifier == identifier:
            return socket
    return None


def create_socket(node_tree, socket_name, description, in_out, socket_type):
    """Create new socket on the ShaderNodeGroup

    Args:
      node_tree: Node tree to create the socket on
      socket_name: Name of the socket
      description: Description of the socket
      in_out: INPUT" or "OUTPUT"
      socket_type: Type of the socket
    Returns:
      New socket
    """
    return node_tree.interface.new_socket(
        name=socket_name,
        description=description,
        in_out=in_out,
        socket_type=socket_type,
    )


def deserialize_link(node_tree, node_names, link_data):
    """Deserialize link

    Deserialize the link data and create a new link.
    If the link is connected to a NodeGroupInput or NodeGroupOutput, create
    a new input or output socket on the ShaderNodeGroup.

    Args:
      node: Node to deserialize the link on
      node_names: Dictionary with node names
      link_data: Link data to deserialize
    Returns:
      Output and input socket of the link
    """
    if (
        node_names[link_data["from_node"]] is None
        or node_names[link_data["to_node"]] is None
    ):
        print("[ERROR] Node not found")
        return None, None

    # === From node ===
    from_node = node_names[link_data["from_node"]]
    output_socket = get_socket_by_identifier(
        from_node, link_data["from_socket_identifier"], "OUTPUT"
    )

    if from_node.bl_idname == "NodeGroupInput":
        # Create new input socket on the ShaderNodeGroup
        if output_socket is None:
            output_interface_socket: bpy.types.NodeTreeInterfaceSocket = create_socket(
                node_tree,
                link_data["from_socket"],
                link_data["from_socket"] + " Input",
                "INPUT",
                get_node_socket_base_type(link_data["to_socket_type"]),
            )
            output_socket = get_socket_by_identifier(
                from_node, output_interface_socket.identifier, "OUTPUT"
            )

    # === To node ===
    to_node = node_names[link_data["to_node"]]
    input_socket = get_socket_by_identifier(
        to_node, link_data["to_socket_identifier"], "INPUT"
    )
    if to_node.bl_idname == "NodeGroupOutput":
        # Create new output socket on the ShaderNodeGroup
        if input_socket is None:
            input_interface_socket: bpy.types.NodeTreeInterfaceSocket = create_socket(
                node_tree,
                link_data["to_socket"],
                link_data["to_socket"] + " Output",
                "OUTPUT",
                get_node_socket_base_type(link_data["from_socket_type"]),
            )
            input_socket = get_socket_by_identifier(
                to_node, input_interface_socket.identifier, "INPUT"
            )

    return output_socket, input_socket


def build_node_parent_name_map(data, node_tree):
    """
    Build a mapping of old node names to new node names (for frames).

    Args:
        data: Serialized data containing the node structure.
        node_tree: The node tree where new nodes will be added.

    Returns:
        node_parent_name: A dictionary mapping old node names to new names.
    """
    node_parent_name = {}
    node_frame_location = {}

    # Create nodes for frames first to ensure they exist
    for node_name, node_data in data["nodes"].items():
        if node_data["type"] == "NodeFrame": 
            new_node = deserialize_node(node_data, node_tree.nodes)
            new_node.name = node_data["name"]

            # If the name was changed, map the old name to the new name
            if new_node.name != node_name:
                node_parent_name[node_name] = new_node.name
            else:
                node_parent_name[node_name] = node_name
                        
            node_frame_location[node_parent_name[node_name]] = new_node.location
            #new_node.location = [0, 0]

    # Remove the frame nodes from the node list
    for node_name in node_parent_name:
        data["nodes"].pop(node_name)

    return node_parent_name, node_frame_location


def update_parent_references(data, node_parent_name):
    """
    Update the parent references in the serialized node data based on the new node names.

    Args:
        data: Serialized data containing the node structure.
        node_parent_name: A mapping from old node names to new node names.
    """
    for node_name, node_data in data["nodes"].items():
        # Check if the node has a parent frame
        if "parent" in node_data and node_data["parent"] in node_parent_name:
            # Update the parent frame to the new name
            node_data["parent"] = node_parent_name[node_data["parent"]]

def deserialize_node_tree(node_tree, data):
    """Deserialize node tree

    Deserialize the node tree data and create new nodes and links.

    Args:
      node: Node to deserialize the node tree on
      data: Data to deserialize
    Returns:
    """
    node_names = {}

    node_parent_name = {}
    node_frame_location = {}

    node_parent_name, node_frame_location = build_node_parent_name_map(data, node_tree)

    update_parent_references(data, node_parent_name)

    # Save the new node with the node name which is used for linking to get the node
    for node_name, node_data in data["nodes"].items():
        node_names[node_name] = deserialize_node(node_data, node_tree.nodes)
        # Setting correct location for frames
        if node_names[node_name].parent and isinstance(node_names[node_name].parent, bpy.types.NodeFrame):
            node_frame_name = node_names[node_name].parent.name
            if node_frame_name in node_frame_location:
                location = node_frame_location[node_frame_name]
                node_names[node_name].location = node_names[node_name].location + location
            else:
                # Remove parent from created node if its not inside the current deserialized nodes
                node_names[node_name].parent = None


    # Apply links
    for link_data in data["links"]:
        # Deserialize link
        input_socket, output_socket = deserialize_link(node_tree, node_names, link_data)
        # Create new link
        if input_socket and output_socket:
            node_tree.links.new(input_socket, output_socket)


def encode_data(node_tree, selected_node_names=None):
    """Encode data

    Serialize the node tree and compress and encode the data with zlib and base64.

    Args:
      node_tree: Node tree to encode
      selected_node_names: Selected node names (Default value = None)
    Returns:
      Base64 encoded data
    """
    # Serialize node tree
    data = serialize_node_tree(node_tree, selected_node_names)

    # Compress and encode data
    compress_data = zlib.compress(pickle.dumps(data), 9)
    base64_encoded = base64.b64encode(compress_data).decode("utf-8")

    print(base64_encoded)
    print(len(base64_encoded))
    return base64_encoded


def decode_data(base64_encoded, material):
    """Decode data

    Decode and decompress the base64 encoded data and deserialize the data.

    Args:
      base64_encoded: Base64 encoded data
      material: Material to set the node tree on
    Returns:
      Result of the operation: ("FINISHED", "Node Runner Import executed")
    """

    # Create new material if none is selected
    if not material or not hasattr(material, "node_tree"):
        material = bpy.data.materials.new(name="Material")
        if bpy.context.active_object:
            bpy.context.active_object.data.materials.append(material)

    # Decode base64 encoded data
    try:
        decompressed_data = zlib.decompress(base64.b64decode(base64_encoded))
        deserialized_data = pickle.loads(decompressed_data)
    except (zlib.error, pickle.UnpicklingError, binascii.Error):
        return ("CANCELLED", "Decoding error")
    except Exception as e:
        return ("CANCELLED", f"Decoding error: {e}")


    # Deserialize node tree
    deserialize_node_tree(bpy.context.space_data.edit_tree, deserialized_data)
    return ("FINISHED", "Node Runner Import executed")


class NodeRunnerImport(bpy.types.Operator):
    """Class for import dialog"""

    bl_idname = "object.node_runner_import"
    bl_label = "Node Runner Import"
    bl_options = {"REGISTER", "UNDO"}

    my_node_runner_string: bpy.props.StringProperty(
        name="Node Runner Hash",
        default="",
        description="Node Runner Hash",
    )  # type: ignore

    # pylint: disable=unused-argument
    def execute(self, context):
        """
        Args:
          self:
          context:
        Returns:
        """
        if self.my_node_runner_string == "":
            self.report({"INFO"}, "No Node Runner Hash String provided")
            return {"CANCELLED"}
        
        

        result = decode_data(self.my_node_runner_string.split("__NR", 1)[1], bpy.context.material)

        self.report({"INFO"}, result[1])
        return {result[0]}

    # pylint: disable=unused-argument
    def invoke(self, context, event):
        """
        Args:
          self:
          context:
          event:
        Returns:
        """
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class NodeRunnerExport(bpy.types.Operator):
    """Class for export dialog"""

    bl_idname = "object.node_runner_export"
    bl_label = "Node Runner Export"
    bl_options = {"REGISTER", "UNDO"}

    node_runner_export_field: bpy.props.StringProperty(
        name="Node Runner Hash String",
        default="",
        description="Node Runner Hash String",
    )  # type: ignore

    # pylint: disable=unused-argument
    def execute(self, context):
        """
        Args:
          self:
          context:
        Returns:
        """

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        # Show some text
        layout.label(text="Hash has been copied to clipboard")

        # Create the input field
        layout.prop(self, "node_runner_export_field", text="Export Field")

    # pylint: disable=unused-argument
    def invoke(self, context, event):
        """
        Args:
          self:
          context:
          event:
        Returns:
        """
        wm = context.window_manager
        material = bpy.context.object.active_material
        if not material or not hasattr(material, "node_tree"):
            self.report({"INFO"}, "No valid material with a node tree selected")
            return {"CANCELLED"}

        selected_nodes = bpy.context.selected_nodes
        selected_node_names = []
        for node in selected_nodes:
            # NodeGroupInput and NodeGroupOutput are generated automatically by a NodeGroup and cannot be exported/imported
            if selected_nodes and not isinstance(node, (bpy.types.NodeGroupInput, bpy.types.NodeGroupOutput)):
                selected_node_names.append(node.name)

        compress_nodes = encode_data(
            bpy.context.space_data.edit_tree, selected_node_names=selected_node_names
        )
        self.report({"INFO"}, "Node Runner Hash copied to clipboard")

        compress_nodes_with_header = "YourNodeName__NR" + compress_nodes

        self.node_runner_export_field = compress_nodes_with_header
        bpy.context.window_manager.clipboard = compress_nodes_with_header
        return wm.invoke_props_dialog(self)


class NodeRunnerImportContextMenu(bpy.types.Operator):
    """Class for import option in context menu"""

    bl_idname = "object.node_runner_import_context_menu"
    bl_label = "Node Runner Import Context Menu"

    # pylint: disable=unused-argument
    def execute(self, context):
        """Checks for a valid material and node tree and invokes
        the import dialog
        Args:
          self:
          context:
        Returns:
        """
        material = bpy.context.object.active_material
        if not material:
            self.report({"WARNING"}, "No valid material selected")
            return {"CANCELLED"}
        if not hasattr(material, "node_tree"):
            self.report({"WARNING"}, "No node tree found")
            return {"CANCELLED"}
        bpy.ops.object.node_runner_import("INVOKE_DEFAULT")
        return {"FINISHED"}

    # pylint: disable=unused-argument
    def invoke(self, context, event):
        """
        Args:
          self:
          context:
          event:
        Returns:
        """
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class NodeRunnerExportContextMenu(bpy.types.Operator):
    """Class for export option in context menu"""

    bl_idname = "object.node_runner_export_context_menu"
    bl_label = "Node Runner Export Context Menu"

    # pylint: disable=unused-argument
    def execute(self, context):
        """
        Args:
          self:
          context:
        Returns:
        """
        selected_nodes = bpy.context.selected_nodes
        selected_node_names = (
            [node.name for node in selected_nodes] if selected_nodes else None
        )

        if selected_node_names is None:
            self.report({"WARNING"}, "No nodes selected!")
            return {"CANCELLED"}
        
        nodes = bpy.context.space_data.edit_tree.nodes
        i = 0
        for selected_node in selected_node_names:
            if not isinstance(nodes[selected_node], (bpy.types.NodeGroupInput, bpy.types.NodeGroupOutput)):
                i += 1
        if i == 0:
            self.report({"WARNING"}, "No valid nodes selected!")
            return {"CANCELLED"}
                
        bpy.ops.object.node_runner_export("INVOKE_DEFAULT")
        return {"FINISHED"}

    # pylint: disable=unused-argument
    def invoke(self, context, event):
        """
        Args:
          self:
          context:
          event:
        Returns:
        """
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# pylint: disable=unused-argument
def menu_func_node_runner_export(self, context):
    """
    Args:
      self:
      context:
    Returns:
    """
    self.layout.operator(
        NodeRunnerExportContextMenu.bl_idname, text="Node Runner Export"
    )


# pylint: disable=unused-argument
def menu_func_node_runner_import(self, context):
    """
    Args:
      self:
      context:
    Returns:
    """
    self.layout.operator(
        NodeRunnerImportContextMenu.bl_idname, text="Node Runner Import"
    )


def register():
    """Register classes"""
    bpy.utils.register_class(NodeRunnerImportContextMenu)
    bpy.utils.register_class(NodeRunnerExportContextMenu)
    bpy.utils.register_class(NodeRunnerImport)
    bpy.utils.register_class(NodeRunnerExport)

    # Add it to the Shader Editor context menu
    bpy.types.NODE_MT_context_menu.append(menu_func_node_runner_import)
    bpy.types.NODE_MT_context_menu.append(menu_func_node_runner_export)


def unregister():
    """Unregister classes"""
    bpy.types.NODE_MT_context_menu.remove(menu_func_node_runner_export)
    bpy.types.NODE_MT_context_menu.remove(menu_func_node_runner_import)

    bpy.utils.unregister_class(NodeRunnerExport)
    bpy.utils.unregister_class(NodeRunnerImport)
    bpy.utils.unregister_class(NodeRunnerExportContextMenu)
    bpy.utils.unregister_class(NodeRunnerImportContextMenu)


if __name__ == "__main__":
    register()
