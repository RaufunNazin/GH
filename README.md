# Girls' Hall Search Portal

A modern web application for searching and viewing hall and department information from Excel data. The application supports both Bengali and English text search with a beautiful, responsive user interface.

## Features

- 🔍 **Advanced Search**: Search by hall name, department name, or any field in the data
- 🌐 **Multilingual Support**: Full support for Bengali and English text
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- 💾 **Data Export**: Export search results to CSV format
- 🎨 **Modern UI**: Clean, professional interface with smooth animations
- ⚡ **Real-time Suggestions**: Auto-complete suggestions as you type
- 📊 **Detailed View**: Modal popup for detailed record information

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files** to your local machine

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your Excel file** in the project directory with the name `Emails Latest (1).xlsx`

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5001
   ```

3. **Search for data**:
   - Type in the search box to find halls or departments
   - Use suggestions that appear as you type
   - Click on any result to view detailed information
   - Export results to CSV if needed

## File Structure

```
Girls' Hall/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── Emails Latest (1).xlsx # Your Excel data file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── app.js        # Frontend JavaScript
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/data` - Get all hall data
- `GET /api/search?q=<query>` - Search data by query
- `GET /api/columns` - Get column names

## Search Features

- **Case-insensitive search**: Works regardless of text case
- **Partial matching**: Finds results containing your search term
- **Multi-field search**: Searches across all data fields
- **Bengali text support**: Properly handles Bengali characters
- **Real-time suggestions**: Shows suggestions as you type

## Customization

### Styling
Edit `static/css/style.css` to customize the appearance:
- Colors and themes
- Fonts and typography
- Layout and spacing
- Animations and effects

### Functionality
Modify `static/js/app.js` to add features:
- Additional search filters
- Custom export formats
- Enhanced user interactions
- Integration with external services

### Backend
Update `app.py` to:
- Add new API endpoints
- Implement data validation
- Add authentication
- Connect to databases

## Troubleshooting

### Common Issues

1. **Excel file not found**:
   - Ensure `Emails Latest (1).xlsx` is in the project directory
   - Check file permissions

2. **Dependencies not installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Port already in use**:
   - Change the port in `app.py` (line 67)
   - Or kill the process using port 5000

4. **Bengali text not displaying**:
   - Ensure your browser supports Unicode
   - Check that the Excel file contains proper Bengali text

### Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

To extend or modify the application:

1. **Backend changes**: Edit `app.py`
2. **Frontend changes**: Edit files in `templates/` and `static/`
3. **Dependencies**: Update `requirements.txt`
4. **Testing**: Test with different Excel files and data formats

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Excel file format and content
3. Ensure all dependencies are properly installed
4. Check browser console for JavaScript errors

---

**Note**: Make sure your Excel file contains the data in a tabular format with headers in the first row for best results.
