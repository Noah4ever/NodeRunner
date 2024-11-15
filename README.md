# NodeRunner

#### Example of exporting and importing shader nodes

https://github.com/user-attachments/assets/58fe2ed8-74bb-485b-aa89-6c8f0a16d7e0

## Overview

This **Blender Python Addon** allows you to easily **import and export shader nodes** to a simple **string format**. The exported strings can be easily shared through text messengers, YouTube comments, or any other text-based platform, allowing you to quickly share node setups without the need to send actual files.

With this addon, sharing and reusing shader node setups becomes as simple as copying and pasting a line of text!

## Features

- **🚀 Export Shader Nodes**: Converts your current shader node setup into a compact string that can be copied and shared.
- **🔄 Import Shader Nodes**: Paste a shared shader node string to recreate the exact node setup in your own Blender project.
- **💬 Text-Based Sharing**: Exported node strings are lightweight and can be shared via messengers, social media, or even in YouTube comments.

## Development

1. Clones this repository into your `addons_core` folder (should be at your local blender installation, example: `blender-4.2.2-windows-x64\4.2\scripts\addons_core`).
2. Open Blender and go into "`Edit > Preferences > Add-Ons`" and search for `Node Runner`.
3. Check the checkbox.

### Documentation

To create documentation you need to have installed:

```bash
pip install mkdocs mkdocstrings-python mkdocstrings mkdocs-material
```

After that you can run the following command:

```bash
mkdocs serve
```

## Example

- **Export**: Right-click in the shader editor > **Node Runner Export** > Copy the generated string.
- **Import**: Right-click in the shader editor > **Node Runner Import** > Paste the node string > Nodes are recreated.

## License

This addon is released under the [MIT License](LICENSE).

---

Feel free to report any issues or contribute to the project. Happy blending and node sharing! 🔥
