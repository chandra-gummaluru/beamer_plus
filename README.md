# Beamer+

Beamer+ is a Python-based application that enhances Beamer presentations by integrating video playback and drawing capabilities, creating a rich multimedia experience for presentations.

![Screenshot_3-4-2025_221514_www cs toronto edu](https://github.com/user-attachments/assets/439c5091-9914-4413-b4c4-7cec6445cc99)

## Features

- **Beamer Presentation Integration**: Display PDF slides created with Beamer.
- **Video Playback**: Embed and control video files within the presentation.
- **Drawing Capability**: Annotate slides in real-time during the presentation.

## Prerequisites

Ensure you have the following installed on your system:

- **Python 3.x**
- **pip (Python package installer)**

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/chandra-gummaluru/beamer_plus.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd beamer_plus
   ```

3. **Install Required Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Beamer+ uses a configuration file to manage presentation settings. An example configuration is provided in the `example` directory.

1. **Create a Configuration File**:

   Copy the example configuration to the `src` directory:

   ```bash
   cp example/config.json src/config.json
   ```

2. **Edit the Configuration File**:

   Open `src/config.json` and modify the settings as needed:

   - **slide_pdf**: Path to your Beamer-generated PDF slides.
   - **videos**: A list of video file paths to be embedded in the presentation.
   - **other_settings**: Adjust additional settings as required.

   Example `config.json`:

   ```json
   {
     "slide_pdf": "path/to/your/slides.pdf",
     "videos": [
       "path/to/video1.mp4",
       "path/to/video2.mp4"
     ],
     "other_settings": {
       // Additional settings
     }
   }
   ```

## Usage

1. **Navigate to the Source Directory**:

   ```bash
   cd src
   ```

2. **Run the Application**:

   ```bash
   python main.py
   ```

   This will launch the Beamer+ application, displaying your slides with integrated video and drawing capabilities.

## Controls

- **Navigation**: Use the arrow keys or mouse clicks to navigate through the slides.
- **Video Playback**: Embedded videos can be played/paused using the spacebar or on-screen controls.
- **Drawing**: Activate the drawing mode by pressing 'D'. Use the mouse to draw annotations on the slides. Press 'D' again to exit drawing mode.

## License

This project is licensed under the MIT License. See the `LICENSE.txt` file for details.

## Acknowledgments

Beamer+ was developed by Chandra Gummaluru. For more projects and contributions, visit [Chandra's GitHub profile](https://github.com/chandra-gummaluru).
