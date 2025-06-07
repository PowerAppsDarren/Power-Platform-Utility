# Power Platform Utility

A modern Python GUI application built with PySide6 for interfacing with Power Platform environments using the PAC CLI (Power Platform CLI).

## Features

### 🚀 Core Functionality
- **Environment Management**: Connect to and switch between Power Platform environments
- **Solution Operations**: Import, export, and manage Power Platform solutions
- **Authentication**: Secure authentication with Power Platform services
- **Real-time Logging**: Comprehensive activity logging and monitoring

### 🎨 Modern UI
- **PySide6 Interface**: Professional, native-looking GUI
- **Tabbed Navigation**: Organized workflow with multiple tabs
- **Progress Indicators**: Visual feedback for long-running operations
- **Responsive Design**: Adaptable layout for different screen sizes

### 🔧 Advanced Features
- **Background Processing**: Non-blocking operations using worker threads
- **Configuration Management**: Customizable settings and preferences
- **Error Handling**: Robust error management and user feedback
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Prerequisites

### Required Software
1. **Python 3.8+**: Download from [python.org](https://www.python.org/)
2. **Power Platform CLI (PAC)**: Install from [Microsoft Docs](https://docs.microsoft.com/en-us/power-platform/developer/cli/introduction)

### PAC CLI Installation
```powershell
# Install PAC CLI using PowerShell
winget install Microsoft.PowerPlatformCLI
```

Or download from the [official releases page](https://github.com/microsoft/powerplatform-build-tools).

## Installation

### 1. Clone the Repository
```powershell
git clone https://github.com/powerplatformtools/power-platform-utility.git
cd power-platform-utility
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Verify PAC CLI Installation
```powershell
pac --version
```

## Usage

### Starting the Application
```powershell
# From the project root directory
python src/main.py
```

### First Time Setup
1. **Launch the application**
2. **Authenticate**: Click "Authenticate" to sign in to Power Platform
3. **Refresh Environments**: Click "Refresh" to load your environments
4. **Select Environment**: Choose an environment from the dropdown
5. **Connect**: Click "Connect" to establish connection

### Working with Solutions

#### Viewing Solutions
1. Navigate to the **Solutions** tab
2. Click **Refresh** to load solutions from the connected environment
3. View solution details in the table

#### Exporting Solutions
1. Go to the **Import/Export** tab
2. Select a solution from the dropdown
3. Choose export location
4. Select export options (Managed/Unmanaged)
5. Click **Export Solution**

#### Importing Solutions
1. Go to the **Import/Export** tab
2. Browse and select a solution file (.zip)
3. Configure import options
4. Click **Import Solution**

## Project Structure

```
Power-Platform-Utility/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── core/              # Core business logic
│   │   ├── pac_cli.py     # PAC CLI wrapper
│   │   └── environment.py # Environment management
│   ├── ui/                # User interface
│   │   └── main_window.py # Main application window
│   └── utils/             # Utility functions
│       └── helpers.py     # Helper functions
├── config/                # Configuration files
│   └── settings.json      # Application settings
├── requirements.txt       # Python dependencies
└── setup.py              # Package setup
```

## Configuration

The application uses `config/settings.json` for configuration:

```json
{
    "application": {
        "name": "Power Platform Utility",
        "version": "1.0.0",
        "theme": "default"
    },
    "pac_cli": {
        "timeout": 30,
        "retry_attempts": 3
    },
    "ui": {
        "window_width": 1200,
        "window_height": 800,
        "remember_size": true,
        "remember_position": true
    },
    "logging": {
        "level": "INFO",
        "file_logging": true
    }
}
```

## Development

### Setting up Development Environment
```powershell
# Install development dependencies
pip install pytest black flake8

# Run code formatting
black src/

# Run linting
flake8 src/

# Run tests
pytest
```

### Building Executable
```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --windowed --onefile src/main.py --name "PowerPlatformUtility"
```

## Troubleshooting

### Common Issues

#### PAC CLI Not Found
**Error**: `PAC CLI not installed or not accessible`
**Solution**: 
1. Install PAC CLI using `winget install Microsoft.PowerPlatformCLI`
2. Restart your terminal/IDE
3. Verify with `pac --version`

#### Authentication Issues
**Error**: Authentication failures
**Solution**:
1. Clear browser cache
2. Try `pac auth clear` followed by `pac auth create`
3. Check network connectivity and proxy settings

#### Environment Connection Issues
**Error**: Failed to connect to environment
**Solution**:
1. Verify environment URL is correct
2. Check user permissions for the environment
3. Ensure proper authentication

### Logging
Application logs are stored in:
- **Console**: Real-time logging in the application
- **File**: `logs/power_platform_utility.log`
- **Detailed**: Available in the Logs tab

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/powerplatformtools/power-platform-utility/issues)
- **Discussions**: [GitHub Discussions](https://github.com/powerplatformtools/power-platform-utility/discussions)
- **Documentation**: [Wiki](https://github.com/powerplatformtools/power-platform-utility/wiki)

## Acknowledgments

- Microsoft Power Platform team for the PAC CLI
- Qt/PySide6 team for the excellent GUI framework
- Python community for the amazing ecosystem


## Project Structure


```Text
Power-Platform-Utility/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main application window
│   │   ├── dialogs/         # Various dialog windows
│   │   └── widgets/         # Custom widgets
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pac_cli.py       # PAC CLI wrapper
│   │   └── environment.py   # Environment management
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── requirements.txt
├── setup.py
└── config/
    └── settings.json
```
