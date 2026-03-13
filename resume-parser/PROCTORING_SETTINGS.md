# Proctoring Settings - Quick Reference

## Current Configuration (Lenient Mode)

### Detection Sensitivity
```python
# File: tests/proctoring.py

# Frontal Face Detection
scaleFactor = 1.2      # Higher = Less Sensitive (Range: 1.1 - 1.5)
minNeighbors = 7       # Higher = Fewer False Positives (Range: 3 - 10)
minSize = (50, 50)     # Larger = Ignore Small Faces (Range: 30x30 - 100x100)

# Profile Face Detection (Head Turn)
scaleFactor = 1.2      # Same as above
minNeighbors = 7       # Same as above
minSize = (50, 50)     # Same as above
```

### Violation Thresholds
```python
# File: tests/views.py

# Test Round Proctoring
HEAD_TURN_LIMIT = 5           # Warnings before termination
MULTIPLE_FACE_LIMIT = 5       # Warnings before termination

# DSA Round Proctoring
HEAD_TURN_LIMIT = 5           # Warnings before termination
MULTIPLE_FACE_LIMIT = 5       # Warnings before termination
```

### Monitoring Frequency
```javascript
// File: tests/templates/tests/test_interface.html
// File: tests/templates/tests/dsa_interface.html

proctorInterval = setInterval(checkProctoring, 3000);  // Check every 3 seconds
```

## Adjustment Guide

### Make MORE Lenient (Fewer Violations)
1. **Increase scaleFactor**: 1.2 → 1.3 or 1.4
2. **Increase minNeighbors**: 7 → 8 or 9
3. **Increase minSize**: (50,50) → (60,60) or (70,70)
4. **Increase violation limits**: 5 → 7 or 10
5. **Increase check interval**: 3000ms → 5000ms or 10000ms

### Make MORE Strict (More Violations)
1. **Decrease scaleFactor**: 1.2 → 1.1
2. **Decrease minNeighbors**: 7 → 5 or 4
3. **Decrease minSize**: (50,50) → (40,40) or (30,30)
4. **Decrease violation limits**: 5 → 3 or 2
5. **Decrease check interval**: 3000ms → 2000ms or 1000ms

## Testing Recommendations

### Test Different Scenarios
- [ ] Normal sitting position
- [ ] Looking at notes (slight head turn)
- [ ] Looking away completely
- [ ] Someone walking behind
- [ ] Two people in frame
- [ ] Poor lighting conditions
- [ ] Different camera angles

### Optimal Settings for Different Environments

#### Home Environment (Most Lenient)
```python
scaleFactor = 1.3
minNeighbors = 8
minSize = (60, 60)
violation_limit = 7
check_interval = 5000  # 5 seconds
```

#### Office Environment (Balanced)
```python
scaleFactor = 1.2
minNeighbors = 7
minSize = (50, 50)
violation_limit = 5
check_interval = 3000  # 3 seconds
```

#### Exam Center (Strict)
```python
scaleFactor = 1.1
minNeighbors = 5
minSize = (40, 40)
violation_limit = 3
check_interval = 2000  # 2 seconds
```

## Troubleshooting

### Too Many False Positives (Violations when shouldn't)
**Symptoms**: Warnings appear even when candidate is looking at screen
**Solution**: 
- Increase scaleFactor to 1.3
- Increase minNeighbors to 8 or 9
- Increase minSize to (60, 60)

### Not Detecting Violations (Too Lenient)
**Symptoms**: No warnings when candidate clearly looks away
**Solution**:
- Decrease scaleFactor to 1.1
- Decrease minNeighbors to 5 or 6
- Decrease minSize to (40, 40)

### Lighting Issues
**Symptoms**: Inconsistent detection in different lighting
**Solution**:
- Ensure good lighting for candidates
- Increase minNeighbors to reduce noise
- Consider adding brightness normalization

### Multiple Face False Positives
**Symptoms**: Detects multiple faces when only one person
**Solution**:
- Increase minNeighbors to 8
- Increase minSize to (60, 60)
- Add minimum confidence threshold

## Performance Impact

### Current Settings Performance
- **CPU Usage**: ~5-10% per active session
- **Memory**: ~50MB per session
- **Network**: ~10KB per check (every 3 seconds)
- **Recommended Max Concurrent Sessions**: 50-100

### Optimization Tips
1. Increase check interval to reduce CPU usage
2. Reduce frame quality in JavaScript (currently 0.8)
3. Use smaller canvas size for processing
4. Implement server-side caching

## Quick Commands

### Reset Violation Counts (Django Shell)
```python
from tests.models import Test, DSASession

# Reset test violations
Test.objects.filter(status='active').update(
    head_turn_violations=0,
    multiple_face_violations=0
)

# Reset DSA violations
DSASession.objects.filter(status='active').update(
    head_turn_violations=0,
    multiple_face_violations=0
)
```

### View Current Violations
```python
from tests.models import Test

test = Test.objects.get(id=1)
print(f"Head turns: {test.head_turn_violations}")
print(f"Multiple faces: {test.multiple_face_violations}")
```

### Disable Proctoring Temporarily
```python
# In views.py, comment out the violation tracking:
# test.head_turn_violations += 1
# test.multiple_face_violations += 1
```

## Support

For issues:
1. Check browser console for JavaScript errors
2. Verify camera permissions granted
3. Test with different browsers (Chrome recommended)
4. Check server logs for Python errors
5. Verify OpenCV is installed correctly

## Version History

- **v1.0**: Initial implementation with MediaPipe (3 violations)
- **v1.1**: Switched to OpenCV Haar Cascades (3 violations)
- **v1.2**: Made lenient - 5 violations, adjusted detection parameters ✓ Current
