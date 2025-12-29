# Deployment Checklist

## Pre-Deployment

### File Preparation

- [ ] Review all new files created
- [ ] Verify boot.py has been updated
- [ ] Verify main.py has been updated
- [ ] Ensure config.py is ready
- [ ] Ensure wifi_manager.py is ready

### Hardware Check

- [ ] ESP32 powered and accessible
- [ ] LED strip connected to GPIO 16
- [ ] LED strip has external power if needed
- [ ] Buzzer connected to GPIO 25 (optional)
- [ ] Relay connected to GPIO 12 (optional)

## Upload Files to ESP32

### Required Files (Must upload)

1. [ ] `boot.py` - Updated version with wifi_manager import
2. [ ] `main.py` - Updated version with config loading
3. [ ] `wifi_manager.py` - New file
4. [ ] `config.py` - New file

### Optional Files (Recommended)

5. [ ] `config_helper.py` - For easy config management
6. [ ] `config_server.py` - For runtime configuration
7. [ ] `test_wifi.py` - For testing
8. [ ] `README.md` - Documentation
9. [ ] `SETUP.md` - Quick start guide

### Files NOT to upload

- [ ] ~~IMPLEMENTATION.md~~ (Documentation only)
- [ ] ~~ARCHITECTURE.md~~ (Documentation only)
- [ ] ~~example_config_integration.py~~ (Example code only)

## Initial Configuration

### Option A: Web Interface (Recommended for first-time users)

1. [ ] Upload required files to ESP32
2. [ ] Restart ESP32 (press RST button or power cycle)
3. [ ] Wait for blue LED spinner (15 seconds)
4. [ ] Look for "scorebox-XXXX" WiFi network (XXXX is unique to your device)
5. [ ] Connect to "scorebox-XXXX" (password: configure)
6. [ ] Open browser to http://192.168.4.1
7. [ ] Enter WiFi credentials
8. [ ] Enter device settings
9. [ ] Click "Save & Restart"
10. [ ] Wait for device to reboot
11. [ ] Verify device connects to WiFi

### Option B: Pre-configured File

1. [ ] Run config_helper.py locally or on device
2. [ ] Create config.json with your settings
3. [ ] Upload config.json to ESP32
4. [ ] Upload required code files
5. [ ] Restart ESP32
6. [ ] Verify connection

## Testing Phase

### WiFi Connection

- [ ] Device shows blue loading spinner
- [ ] Device connects to WiFi within 15 seconds
- [ ] Blue LEDs turn off after connection
- [ ] Device prints IP address to console
- [ ] Hostname appears on router's device list

### Fallback to AP Mode

- [ ] Delete or rename config.json
- [ ] Restart device
- [ ] Blue spinner appears
- [ ] After timeout, solid blue appears
- [ ] "scorebox-XXXX" network is visible
- [ ] Can connect to network
- [ ] Config page loads at 192.168.4.1

### LED Functionality

- [ ] Blue spinner animates smoothly
- [ ] Brightness is visibly dimmed (5%)
- [ ] LEDs clear after WiFi connection
- [ ] Score LEDs work (green/red)
- [ ] Goal celebration works

### Configuration Persistence

- [ ] Save configuration via web interface
- [ ] Device restarts automatically
- [ ] config.json exists on device
- [ ] Configuration survives power cycle
- [ ] Can read config.json contents

## Production Deployment

### Security (Consider these)

- [ ] Change AP password from "configure" in wifi_manager.py (optional)
- [ ] Add authentication to config server (optional)
- [ ] Use strong WiFi password
- [ ] Consider network isolation for device
- [ ] Note: Network name includes unique device code for identification

### Customization

- [ ] Set correct team abbreviation
- [ ] Adjust poll interval for your needs
- [ ] Set correct number of LEDs
- [ ] Customize hostname
- [ ] Test with your team's schedule

### Monitoring

- [ ] Verify API calls work
- [ ] Check memory usage (gc.mem_free())
- [ ] Monitor for crashes
- [ ] Test goal detection
- [ ] Verify score updates

## Optional Enhancements

### Config Server (Runtime Configuration)

- [ ] Add config_server import to main.py
- [ ] Start server on port 8080
- [ ] Test access at http://[device-ip]:8080
- [ ] Verify main loop continues normally

### Advanced Features

- [ ] Add team logo patterns
- [ ] Custom celebration animations
- [ ] Score persistence across games
- [ ] Network status indicator
- [ ] Multiple team tracking

## Troubleshooting Tests

### Test 1: No WiFi Config

```
1. Delete config.json
2. Restart device
3. Expected: AP mode with blue LEDs
4. Expected: Can access config page
```

### Test 2: Wrong WiFi Password

```
1. Enter wrong password in config
2. Restart device
3. Expected: Blue spinner for 15 seconds
4. Expected: Fallback to AP mode
```

### Test 3: Config Persistence

```
1. Configure via web interface
2. Power off device
3. Power on device
4. Expected: Connects automatically
5. Expected: config.json still exists
```

### Test 4: LED Patterns

```
1. Boot device (no WiFi)
2. Expected: Blue spinner
3. After timeout
4. Expected: Solid blue (AP mode)
```

### Test 5: Memory Stability

```python
import gc
print(f"Free memory: {gc.mem_free()} bytes")
# Should have at least 50KB free
```

## Post-Deployment Verification

### Functional Check

- [ ] Device boots successfully
- [ ] WiFi connection stable
- [ ] LEDs respond correctly
- [ ] API calls successful
- [ ] Score detection works
- [ ] Goal celebrations trigger
- [ ] Configuration interface accessible

### Performance Check

- [ ] Boot time < 30 seconds
- [ ] WiFi connection < 15 seconds
- [ ] API response time reasonable
- [ ] LED updates smooth
- [ ] No memory errors
- [ ] No unexpected reboots

### Documentation

- [ ] Note device IP address
- [ ] Note device hostname
- [ ] Save config.json backup
- [ ] Document customizations
- [ ] Record team abbreviation

## Maintenance

### Regular Tasks

- [ ] Monitor for API changes
- [ ] Update team if traded/moved
- [ ] Check for memory leaks
- [ ] Verify WiFi stability
- [ ] Test during actual games

### Updates

- [ ] Backup config.json before updates
- [ ] Test new code on bench first
- [ ] Keep copy of working version
- [ ] Document changes made

## Emergency Procedures

### Device Won't Boot

1. Check power supply
2. Check USB connection
3. Reflash MicroPython if needed
4. Re-upload files

### Can't Connect to WiFi

1. Check WiFi credentials in config.json
2. Verify 2.4GHz network available
3. Delete config.json to force AP mode
4. Reconfigure via web interface

### LEDs Not Working

1. Check DATA_PIN (should be 16)
2. Verify LED strip power
3. Test with color-test.py
4. Check NUM_LEDS setting

### Config Page Won't Load

1. Verify connected to scorebox-XXXX network
2. Try http://192.168.4.1 (exact IP)
3. Disable mobile data on phone
4. Try different browser
5. Restart device
6. Check that the network name matches your device code

## Success Criteria

Your deployment is successful when:

- [x] Device boots and connects to WiFi automatically
- [x] Blue loading spinner appears during connection
- [x] Device falls back to AP mode when needed
- [x] Configuration can be changed via web interface
- [x] Settings persist across reboots
- [x] LEDs display score correctly
- [x] Goal celebrations work
- [x] No memory errors or crashes

---

**Notes:**

- Keep a backup of working config.json
- Document any custom modifications
- Test thoroughly before game day
- Have fun! 🏒

**Estimated deployment time:** 15-30 minutes
