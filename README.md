# PDF Merger

A simple, lightweight web application to merge multiple PDF files into one. Built with Flask and PyPDF2.

## Features

- Drag and drop or click to upload multiple PDFs
- Reorder files before merging
- Download the merged PDF instantly
- Automatic cleanup of uploaded files
- Open source — anyone can contribute

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
git clone https://github.com/your-username/pdf-merger.git
cd pdf-merger
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `CLEANUP_INTERVAL` | Seconds between automatic cleanups | 3600 |
| `SESSION_MAX_AGE` | Max age in seconds before session deletion | 3600 |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home page |
| POST | `/upload` | Upload PDF files |
| POST | `/reorder` | Reorder uploaded files |
| POST | `/merge` | Merge files and get download URL |
| GET | `/download/<session_id>` | Download merged PDF |
| POST | `/admin/cleanup` | Manually purge old sessions |

## Tech Stack

- **Backend:** Flask, PyPDF2
- **Frontend:** HTML, CSS, JavaScript

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source under the MIT License.
