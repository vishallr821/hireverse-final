# Proctoring System Documentation

## Overview
This proctoring system monitors test-takers using their webcam to detect violations during the test.

## Features

### 1. Head Turn Detection
- Monitors if the candidate turns their head away from the screen
- Uses OpenCV Haar Cascade to detect profile faces
- **Threshold**: More lenient detection (scaleFactor: 1.2, minNeighbors: 7)
- **Action**: After 5 violations, test is automatically terminated

### 2. Multiple Face Detection
- Detects if more than one person appears in the camera frame
- **First Detection**: Warning displayed to candidate
- **Action**: After 5 violations, test is automatically terminated

## Technical Implementation

### Backend (Python/Django)
- **proctoring.py**: Core monitoring logic using OpenCV and MediaPipe
- **models.py**: Added fields to track violations:
  - `head_turn_violations`: Counter for head turn violations
  - `multiple_face_violations`: Counter for multiple face violations
  - `proctoring_terminated`: Flag indicating if test was terminated due to violations
- **views.py**: API endpoint `/proctor/<token>/` to analyze frames

### Frontend (JavaScript)
- Captures webcam frames every 3 seconds
- Sends frames to backend for analysis
- Displays warnings to candidates
- Auto-submits test when violations exceed threshold

## Installation

1. Install dependencies:
```bash
pip install opencv-python
```

2. Run migrations:
```bash
python manage.py migrate
```

## Current Settings (Lenient)

### Detection Parameters
- **scaleFactor**: 1.2 (higher = less sensitive)
- **minNeighbors**: 7 (higher = fewer false positives)
- **minSize**: 50x50 pixels (larger = ignore small detections)

### Violation Thresholds
- **Head Turn**: 5 warnings before termination
- **Multiple Faces**: 5 warnings before termination

These settings provide a more lenient proctoring experience while still maintaining security.

## Configuration

### Adjusting Thresholds

In `proctoring.py`, modify these values:

```python
# Face detection sensitivity (more lenient settings)
scaleFactor=1.2  # Higher = less sensitive (default: 1.2)
minNeighbors=7   # Higher = less sensitive (default: 7)
minSize=(50, 50) # Larger = less sensitive (default: 50x50)
```

### Violation Limits

In `views.py`, change the violation thresholds:

```python
if test.head_turn_violations >= 5:  # Current: 5 warnings before termination
if test.multiple_face_violations >= 5:  # Current: 5 warnings before termination
```

### Frame Capture Interval

In `test_interface.html`, adjust the monitoring frequency:

```javascript
proctorInterval = setInterval(checkProctoring, 3000);  // Change 3000 to 5000 for 5 seconds
```

## Usage

1. When a candidate starts the test, they will be prompted for camera access
2. The system monitors continuously in the background
3. Violations trigger warnings displayed on screen
4. After 3 violations of the same type, the test auto-submits

## Privacy & Security

- Video frames are processed in real-time and not stored
- Only violation counts are saved to the database
- Candidates are informed about monitoring before starting

## Troubleshooting

### Camera Not Working
- Ensure HTTPS is enabled (required for webcam access in browsers)
- Check browser permissions for camera access

### False Positives
- Adjust sensitivity thresholds in `proctoring.py`
- Increase violation limits in `views.py`
- Ensure good lighting conditions for candidates

## Future Enhancements

- Eye gaze tracking
- Tab switching detection
- Audio monitoring
- Screen recording
- AI-based suspicious behavior detection
