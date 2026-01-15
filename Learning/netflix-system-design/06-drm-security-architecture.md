# Netflix DRM & Security Architecture - System Design

## Overview
Netflix implements multi-layered security to protect premium content worth billions of dollars, prevent piracy, ensure subscriber account security, and comply with studio licensing requirements. This includes DRM (Digital Rights Management), forensic watermarking, secure playback pipelines, and account protection.

## 1. DRM (Digital Rights Management)

### 1.1 Multi-DRM Strategy

**Why Multiple DRM Systems?**
- Different platforms support different DRM technologies
- Studios require specific DRM certifications
- No single DRM works on all devices
- Redundancy and vendor independence

**DRM Systems Used by Netflix**:

```
┌────────────────────────────────────────────────────────────────┐
│                    Netflix Multi-DRM Strategy                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Widevine (Google)                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Platforms: Android, Chrome, Firefox, Edge, Smart TVs    │ │
│  │  Market Share: ~60% of Netflix streams                    │ │
│  │  Security Levels:                                          │ │
│  │  - L1: Hardware-backed (TEE), supports HD/4K             │ │
│  │  - L2: Software decryption, HD only (no 4K)              │ │
│  │  - L3: Software only, SD resolution max (480p)           │ │
│  │  Certification: Widevine Level 1 required for HD+        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  FairPlay (Apple)                                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Platforms: iOS, iPadOS, macOS, tvOS, Safari             │ │
│  │  Market Share: ~30% of Netflix streams                    │ │
│  │  Security: Hardware Secure Enclave (all Apple devices)   │ │
│  │  Supports: Up to 4K HDR                                   │ │
│  │  Certification: FPS (FairPlay Streaming) required        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  PlayReady (Microsoft)                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Platforms: Windows, Xbox, Edge (legacy), some Smart TVs │ │
│  │  Market Share: ~10% of Netflix streams                    │ │
│  │  Security Levels:                                          │ │
│  │  - SL3000: Hardware-backed, supports 4K                   │ │
│  │  - SL2000: Software + TEE, HD only                        │ │
│  │  - SL150: Software only, SD only                          │ │
│  │  Certification: PlayReady 3.0+ for HD                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 DRM Encryption Process

**Content Encryption (Server-Side)**:

```python
import os
import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class ContentEncryptor:
    def __init__(self):
        self.kms = boto3.client('kms')
        self.key_rotation_interval = 86400  # 24 hours
    
    def encrypt_segment(self, segment_data, content_id, segment_index):
        """
        Encrypt video segment using AES-128 CTR mode
        """
        # Generate or retrieve content key for this title
        content_key = self.get_content_key(content_id)
        
        # Generate unique IV (Initialization Vector) per segment
        # IV = Content ID + Segment Index + Random Nonce
        iv = self.generate_iv(content_id, segment_index)
        
        # Encrypt segment data using AES-128 CTR
        cipher = Cipher(
            algorithms.AES(content_key),
            modes.CTR(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        encrypted_data = encryptor.update(segment_data) + encryptor.finalize()
        
        return {
            'encrypted_data': encrypted_data,
            'kid': self.get_key_id(content_id),  # Key ID for license server
            'iv': iv
        }
    
    def get_content_key(self, content_id):
        """
        Retrieve or generate content encryption key (CEK)
        Stored encrypted in AWS KMS
        """
        # Check if key exists in cache
        if self.key_exists_in_cache(content_id):
            return self.get_cached_key(content_id)
        
        # Generate new 128-bit key
        content_key = os.urandom(16)  # 128 bits = 16 bytes
        
        # Encrypt with KMS master key
        kms_response = self.kms.encrypt(
            KeyId='arn:aws:kms:us-east-1:123456:key/netflix-drm-master',
            Plaintext=content_key
        )
        
        # Store encrypted key in DynamoDB
        self.store_encrypted_key(
            content_id=content_id,
            encrypted_key=kms_response['CiphertextBlob'],
            key_id=self.generate_key_id(content_id)
        )
        
        # Cache for 24 hours
        self.cache_key(content_id, content_key)
        
        return content_key
    
    def generate_iv(self, content_id, segment_index):
        """
        Generate unique IV per segment
        Format: ContentID (8 bytes) + SegmentIndex (4 bytes) + Counter (4 bytes)
        """
        content_id_bytes = int(content_id).to_bytes(8, 'big')
        segment_bytes = segment_index.to_bytes(4, 'big')
        counter_bytes = (0).to_bytes(4, 'big')  # Start at 0
        
        iv = content_id_bytes + segment_bytes + counter_bytes
        return iv[:16]  # AES requires 128-bit IV
```

**Encrypted Segment Structure**:
```
┌────────────────────────────────────────────────────────────────┐
│                   Encrypted Video Segment                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Initialization Segment (init.mp4) - UNENCRYPTED              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  - Container metadata (MP4 ftyp, moov boxes)             │ │
│  │  - Codec information (H.265, AAC)                         │ │
│  │  - DRM metadata (PSSH - Protection System Specific Header)│ │
│  │    {                                                      │ │
│  │      "system_id": "edef8ba9-79d6-4ace-a3c8-27dcd51d21ed",│ │
│  │      "key_ids": ["abc123..."],                           │ │
│  │      "license_url": "https://license.netflix.com/widevine"│ │
│  │    }                                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Media Segment (segment-001.m4s) - ENCRYPTED                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Unencrypted Header (moof, mfhd boxes)                   │ │
│  │  - Segment timing information                             │ │
│  │  - Sample sizes and offsets                               │ │
│  │                                                            │ │
│  │  Encrypted Media Data (mdat box)                          │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  Encryption Scheme: cenc (Common Encryption)       │  │ │
│  │  │  Algorithm: AES-128-CTR                             │  │ │
│  │  │  IV: 0x123456789abcdef0                            │  │ │
│  │  │  Encrypted video/audio data                         │  │ │
│  │  │  (clear H.264/H.265 NAL unit headers preserved)    │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 1.3 License Server Architecture

**DRM License Flow**:

```
┌────────────────────────────────────────────────────────────────┐
│                  DRM License Acquisition Flow                   │
│                                                                 │
│  1. User initiates playback                                    │
│     ↓                                                           │
│  2. Player parses PSSH (Protection System Specific Header)     │
│     - Extracts DRM system ID (Widevine, FairPlay, PlayReady)  │
│     - Extracts key IDs needed for content                      │
│     - Gets license server URL                                  │
│     ↓                                                           │
│  3. Player generates license request (challenge)               │
│     ┌──────────────────────────────────────────────────────┐  │
│     │  Widevine Challenge Structure:                        │  │
│     │  {                                                    │  │
│     │    "key_ids": ["abc123...", "def456..."],            │  │
│     │    "content_id": "12345678",                         │  │
│     │    "device_id": "device_xyz",                        │  │
│     │    "client_id": {                                    │  │
│     │      "device_certificate": "...",  # Device cert    │  │
│     │      "license_counter": 1234                         │  │
│     │    },                                                │  │
│     │    "type": "STREAMING"                               │  │
│     │  }                                                    │  │
│     └──────────────────────────────────────────────────────┘  │
│     ↓                                                           │
│  4. Send license request to Netflix license server             │
│     POST https://license.netflix.com/widevine/v1               │
│     Headers:                                                   │
│       Authorization: Bearer <JWT>                              │
│       Content-Type: application/x-protobuf                     │
│     Body: <Protobuf-encoded challenge>                         │
│     ↓                                                           │
│  5. License server validates request                           │
│     ┌──────────────────────────────────────────────────────┐  │
│     │  Validation Steps:                                    │  │
│     │  a) Authenticate user (JWT token)                     │  │
│     │  b) Verify device certificate                         │  │
│     │  c) Check subscription status                         │  │
│     │  d) Verify content entitlement (user can watch this) │  │
│     │  e) Check regional availability                       │  │
│     │  f) Validate device security level (L1/L2/L3)        │  │
│     │  g) Check concurrent stream limit                     │  │
│     │  h) Verify device isn't revoked/blacklisted          │  │
│     └──────────────────────────────────────────────────────┘  │
│     ↓                                                           │
│  6. License server generates license response                  │
│     ┌──────────────────────────────────────────────────────┐  │
│     │  License Response:                                    │  │
│     │  {                                                    │  │
│     │    "keys": [                                          │  │
│     │      {                                                │  │
│     │        "key_id": "abc123...",                        │  │
│     │        "key": "<encrypted CEK>",  # Content key      │  │
│     │        "type": "CONTENT"                             │  │
│     │      }                                                │  │
│     │    ],                                                │  │
│     │    "policy": {                                       │  │
│     │      "can_play": true,                               │  │
│     │      "can_persist": false,  # No offline download    │  │
│     │      "rental_duration": null,                        │  │
│     │      "playback_duration": 86400,  # 24 hours        │  │
│     │      "license_duration": 3600,    # 1 hour           │  │
│     │      "renewal_recovery": true                        │  │
│     │    },                                                │  │
│     │    "hdcp": {                                         │  │
│     │      "required": true,                               │  │
│     │      "version": "2.2"  # HDCP 2.2 for 4K            │  │
│     │    }                                                 │  │
│     │  }                                                    │  │
│     └──────────────────────────────────────────────────────┘  │
│     ↓                                                           │
│  7. Player receives and processes license                      │
│     - Extracts decryption keys                                 │
│     - Stores keys in secure hardware (TEE/Secure Enclave)     │
│     - Enforces playback policies                               │
│     ↓                                                           │
│  8. Playback begins (keys valid for 24 hours)                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**License Server Implementation**:

```python
from flask import Flask, request, jsonify
import jwt
import boto3
from datetime import datetime, timedelta

app = Flask(__name__)

class LicenseServer:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.kms = boto3.client('kms')
        self.users_table = self.dynamodb.Table('netflix-users')
        self.licenses_table = self.dynamodb.Table('netflix-licenses')
        self.revoked_devices_table = self.dynamodb.Table('revoked-devices')
    
    @app.route('/widevine/v1', methods=['POST'])
    def widevine_license(self):
        try:
            # 1. Authenticate user
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user = self.authenticate_user(auth_token)
            
            if not user:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # 2. Parse license request (Widevine protobuf)
            challenge = self.parse_widevine_challenge(request.data)
            
            # 3. Validate request
            validation = self.validate_license_request(user, challenge)
            
            if not validation['valid']:
                return jsonify({'error': validation['reason']}), 403
            
            # 4. Generate license
            license_response = self.generate_widevine_license(
                user=user,
                challenge=challenge,
                validation=validation
            )
            
            # 5. Log license issuance
            self.log_license_issuance(user, challenge, license_response)
            
            return license_response, 200
            
        except Exception as e:
            self.log_error(f"License error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def validate_license_request(self, user, challenge):
        """
        Comprehensive validation of license request
        """
        # Check subscription status
        if user['subscription_status'] != 'active':
            return {'valid': False, 'reason': 'Subscription not active'}
        
        # Check device certificate validity
        device_cert = challenge['client_id']['device_certificate']
        if not self.verify_device_certificate(device_cert):
            return {'valid': False, 'reason': 'Invalid device certificate'}
        
        # Check if device is revoked/blacklisted
        device_id = challenge['device_id']
        if self.is_device_revoked(device_id):
            return {'valid': False, 'reason': 'Device revoked'}
        
        # Check content entitlement
        content_id = challenge['content_id']
        if not self.user_can_watch(user['user_id'], content_id):
            return {'valid': False, 'reason': 'Content not available in your region'}
        
        # Check concurrent stream limit
        subscription_tier = user['subscription_tier']
        max_streams = self.get_max_streams(subscription_tier)  # Basic: 1, Standard: 2, Premium: 4
        
        active_streams = self.get_active_streams(user['user_id'])
        if active_streams >= max_streams:
            return {'valid': False, 'reason': f'Maximum {max_streams} streams exceeded'}
        
        # Check device security level (Widevine L1/L2/L3)
        security_level = self.get_device_security_level(device_cert)
        requested_quality = challenge.get('max_quality', '1080p')
        
        if requested_quality == '4K' and security_level != 'L1':
            return {'valid': False, 'reason': '4K requires hardware DRM (Widevine L1)'}
        
        if requested_quality in ['1080p', '720p'] and security_level == 'L3':
            return {'valid': False, 'reason': 'HD requires hardware DRM (Widevine L1 or L2)'}
        
        # HDCP check (for HD/4K playback)
        hdcp_version = challenge.get('hdcp_version')
        if requested_quality == '4K' and hdcp_version < '2.2':
            return {'valid': False, 'reason': '4K requires HDCP 2.2'}
        
        # All checks passed
        return {
            'valid': True,
            'max_quality': self.determine_max_quality(security_level, hdcp_version),
            'hdcp_required': requested_quality in ['1080p', '4K']
        }
    
    def generate_widevine_license(self, user, challenge, validation):
        """
        Generate Widevine license with encrypted content keys
        """
        content_id = challenge['content_id']
        key_ids = challenge['key_ids']
        
        # Retrieve content encryption keys from DynamoDB
        content_keys = self.get_content_keys(content_id, key_ids)
        
        # Encrypt keys for device (using device public key from certificate)
        device_cert = challenge['client_id']['device_certificate']
        encrypted_keys = self.encrypt_keys_for_device(content_keys, device_cert)
        
        # Build license
        license = {
            'keys': encrypted_keys,
            'policy': {
                'can_play': True,
                'can_persist': False,  # No offline for streaming
                'rental_duration': None,
                'playback_duration_seconds': 86400,  # 24 hours
                'license_duration_seconds': 3600,     # 1 hour (renew after)
                'renewal_recovery_duration_seconds': 300,  # 5 min grace
                'renewal_delay_seconds': 0
            },
            'hdcp': {
                'required': validation['hdcp_required'],
                'version': '2.2' if validation['max_quality'] == '4K' else '1.4'
            },
            'license_start_time': int(datetime.utcnow().timestamp()),
            'playback_start_time': 0,  # Starts when first byte is played
        }
        
        # Sign license (Widevine protobuf signature)
        signed_license = self.sign_widevine_license(license)
        
        return signed_license
```

**License Server Performance**:
- **Throughput**: 100,000+ licenses/second (peak)
- **Latency**: <100ms (p95), <200ms (p99)
- **Availability**: 99.99% (4 nines)
- **Infrastructure**: 
  - Multi-region deployment (5 regions)
  - Auto-scaling (10-100 EC2 instances per region)
  - Redis caching for user/subscription data
  - DynamoDB for license logs

### 1.4 HDCP (High-bandwidth Digital Content Protection)

**HDCP Requirements**:
```
┌────────────────────────────────────────────────────────────────┐
│                    HDCP Requirements by Quality                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SD (480p and below):                                          │
│  - HDCP: Not required                                          │
│  - Use case: Legacy devices, low-security scenarios           │
│                                                                 │
│  HD (720p, 1080p):                                             │
│  - HDCP: Required (version 1.4 or higher)                      │
│  - Enforced on HDMI, DisplayPort outputs                       │
│  - Playback blocked if HDCP handshake fails                    │
│                                                                 │
│  4K UHD:                                                        │
│  - HDCP: Required (version 2.2)                                │
│  - Enforced on all digital outputs                             │
│  - Falls back to 1080p if HDCP 2.2 unavailable                │
│                                                                 │
│  HDCP Handshake Process:                                       │
│  1. Source device (player) sends HDCP request to sink (TV)    │
│  2. Sink responds with certificate and public key              │
│  3. Source validates certificate (not revoked)                 │
│  4. Encrypt video data with HDCP encryption                    │
│  5. Monitor connection (periodic re-authentication)            │
│                                                                 │
│  HDCP Failure Handling:                                        │
│  - Pause playback immediately                                  │
│  - Show error: "HDCP Error: Please check your HDMI connection"│
│  - Retry HDCP handshake (3 attempts)                           │
│  - Fall back to lower resolution if supported                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## 2. Forensic Watermarking

### 2.1 Purpose & Technology

**Why Watermarking?**
- Track leaked content back to source (specific account/session)
- Deter screen recording and piracy
- Studio requirement for premium content
- Legal evidence in piracy cases

**NexGuard Forensic Watermarking** (Netflix's Provider):

```python
class ForensicWatermarking:
    """
    Forensic watermarking embeds invisible tracking data into video
    Survives: compression, scaling, cropping, cam-recording
    """
    
    def embed_watermark(self, video_segment, user_id, session_id, timestamp):
        """
        Embed watermark into video segment
        """
        # Generate unique payload for this playback session
        payload = self.generate_payload(user_id, session_id, timestamp)
        
        # Embed watermark using NexGuard algorithm
        # - Modifies video in imperceptible way
        # - Spreads payload across many frames
        # - Robust to video transformations
        watermarked_segment = nexguard.embed(
            video=video_segment,
            payload=payload,
            strength='medium',  # Strength vs visibility tradeoff
            pattern='A'         # Pattern variant (for different streams)
        )
        
        return watermarked_segment
    
    def generate_payload(self, user_id, session_id, timestamp):
        """
        Generate unique 48-bit payload
        Format: UserID (24 bits) + SessionID (16 bits) + Timestamp (8 bits)
        """
        user_bits = (user_id & 0xFFFFFF) << 24      # 24 bits
        session_bits = (session_id & 0xFFFF) << 8   # 16 bits
        time_bits = (timestamp % 256)               # 8 bits (minute of hour)
        
        payload = user_bits | session_bits | time_bits
        
        # Add error correction (Reed-Solomon)
        payload_with_ecc = self.add_error_correction(payload)
        
        return payload_with_ecc
```

**Watermark Detection (From Pirated Content)**:

```python
def detect_watermark(pirated_video_file):
    """
    Extract watermark from pirated content
    """
    # NexGuard detector
    detector = nexguard.Detector()
    
    # Analyze video frames
    detections = detector.analyze(pirated_video_file)
    
    if detections['confidence'] > 0.90:
        # High confidence detection
        payload = detections['payload']
        
        # Decode payload
        user_id = (payload >> 24) & 0xFFFFFF
        session_id = (payload >> 8) & 0xFFFF
        timestamp = payload & 0xFF
        
        # Lookup session details
        session_info = lookup_session(session_id)
        
        return {
            'detected': True,
            'user_id': user_id,
            'session_id': session_id,
            'account_email': session_info['email'],
            'device_id': session_info['device_id'],
            'ip_address': session_info['ip_address'],
            'playback_time': session_info['timestamp'],
            'confidence': detections['confidence']
        }
    else:
        return {'detected': False}
```

**Watermark Properties**:
- **Imperceptible**: Not visible to human eye (<0.1% quality impact)
- **Robust**: Survives compression, scaling, cropping, cam-recording
- **Capacity**: 40-60 bits (enough for UserID + SessionID)
- **Detection Time**: 30-60 seconds of video needed
- **False Positive Rate**: <0.01%

**Deployment**:
- **Coverage**: 100% of premium content (movies, originals)
- **Method**: Real-time watermarking during streaming
  - Each client gets unique watermark pattern
  - Embedded by CDN or client-side (depending on device)
- **Cost**: ~$0.10-0.50 per hour of content (NexGuard licensing)

### 2.2 Anti-Piracy Enforcement

**Piracy Detection Pipeline**:
```
1. Monitor piracy sites/torrents
   - Automated crawlers (100K+ sites monitored)
   - Torrent indexers
   - Streaming piracy platforms
   ↓
2. Download pirated content
   - Automated bots
   - Human verification
   ↓
3. Watermark detection
   - Extract watermark payload
   - Identify source account
   - Confidence scoring
   ↓
4. Account action (if confidence > 95%)
   - Immediate suspension (serious violation)
   - Warning email (first offense)
   - Account termination (repeat offender)
   - Legal action (large-scale piracy operations)
   ↓
5. DMCA takedown
   - Send takedown notice to hosting site
   - ISP notification
   - Domain suspension (if applicable)
```

## 3. Secure Playback Pipeline

### 3.1 Trusted Execution Environment (TEE)

**TEE Architecture**:
```
┌────────────────────────────────────────────────────────────────┐
│                  Device Architecture                            │
│                                                                 │
│  Application Processor (Normal World)                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Netflix App                                              │ │
│  │  - UI rendering                                            │ │
│  │  - Network requests                                        │ │
│  │  - Buffer management                                       │ │
│  │  - ABR logic                                               │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │ (encrypted segments)                        │
│                   ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Media Framework (MediaCodec, AVPlayer, etc.)            │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                             │
│                   ▼                                             │
│  Secure Processor (Secure World) - TEE                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  DRM Module (TrustZone, Secure Enclave)                  │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  - License storage (encrypted keys)                │  │ │
│  │  │  - Key decryption (using device private key)       │  │ │
│  │  │  - Content decryption (AES-128 CTR)               │  │ │
│  │  │  - HDCP enforcement                                 │  │ │
│  │  │  - Output protection (prevent screen capture)      │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │ (decrypted video frames)                    │
│                   ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Hardware Video Decoder                                   │ │
│  │  - Decode H.264/H.265                                     │ │
│  │  - Render to screen (via secure video path)              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Secure Video Path**:
- Decrypted video never accessible to normal OS or apps
- Video data stays in secure memory until displayed
- Screen capture APIs return black frames
- HDMI output encrypted with HDCP

### 3.2 Output Protection

**Screen Capture Prevention**:
```python
# Android Example (Netflix App)
class SecureVideoActivity(Activity):
    def onCreate(self, savedInstanceState):
        super().onCreate(savedInstanceState)
        
        # Set FLAG_SECURE to prevent screen capture
        self.getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        
        # This prevents:
        # - Screenshots
        # - Screen recording
        # - Casting to non-DRM devices
        # - Display in app switcher (shows black)
```

**iOS Example**:
```swift
// Prevent screen recording/mirroring
class NetflixPlayerViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Monitor for screen capture/recording
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(screenCaptureDetected),
            name: UIScreen.capturedDidChangeNotification,
            object: nil
        )
    }
    
    @objc func screenCaptureDetected() {
        if UIScreen.main.isCaptured {
            // Screen recording or mirroring active
            self.pausePlayback()
            self.showError("Screen recording is not allowed")
        }
    }
}
```

## 4. Account Security

### 4.1 Authentication & Authorization

**Multi-Factor Authentication**:
```python
class AccountSecurity:
    def login(self, email, password, device_id):
        # 1. Verify password
        user = self.verify_credentials(email, password)
        if not user:
            return {'success': False, 'error': 'Invalid credentials'}
        
        # 2. Check if device is recognized
        if not self.is_device_recognized(user['user_id'], device_id):
            # New device - send verification code
            code = self.send_verification_code(user['email'])
            return {
                'success': False,
                'requires_verification': True,
                'message': 'Verification code sent to your email'
            }
        
        # 3. Check for suspicious activity
        if self.is_suspicious_login(user['user_id'], self.get_client_ip()):
            # Anomalous login location/behavior
            self.send_alert_email(user['email'])
            return {
                'success': False,
                'requires_approval': True,
                'message': 'Please confirm this login attempt via email'
            }
        
        # 4. Generate session token (JWT)
        token = self.generate_jwt(user['user_id'], device_id)
        
        # 5. Log successful login
        self.log_login(user['user_id'], device_id, self.get_client_ip())
        
        return {'success': True, 'token': token}
```

### 4.2 Password Sharing Detection

**Heuristics for Account Sharing**:
```python
class PasswordSharingDetector:
    def analyze_account(self, user_id):
        """
        Detect if account is being shared beyond household
        """
        # Get recent streaming sessions (last 30 days)
        sessions = self.get_sessions(user_id, days=30)
        
        # Analyze patterns
        unique_ips = len(set(s['ip_address'] for s in sessions))
        unique_locations = len(set(s['geolocation'] for s in sessions))
        unique_devices = len(set(s['device_id'] for s in sessions))
        
        # Concurrent streams in different locations
        max_concurrent = self.get_max_concurrent_streams(sessions)
        simultaneous_locations = self.get_simultaneous_locations(sessions)
        
        # Scoring (0-100, higher = more likely sharing)
        sharing_score = 0
        
        if unique_ips > 5:
            sharing_score += 20
        
        if unique_locations > 3:  # More than 3 cities
            sharing_score += 30
        
        if simultaneous_locations > 1:  # Streaming from 2+ locations at once
            sharing_score += 40
        
        if unique_devices > 10:
            sharing_score += 10
        
        # Check if locations are far apart (>100 miles)
        if self.locations_far_apart(sessions):
            sharing_score += 20
        
        return {
            'sharing_score': min(100, sharing_score),
            'likely_sharing': sharing_score > 60,
            'unique_ips': unique_ips,
            'unique_locations': unique_locations,
            'unique_devices': unique_devices
        }
```

**Action on Detected Sharing** (2026 policy):
- Score 60-70: In-app message encouraging separate accounts
- Score 70-85: Email notification with "add member" offer
- Score 85-95: Require device verification for new logins
- Score 95+: Account review, possible suspension

## 5. Compliance & Studio Requirements

### 5.1 Hollywood Studio Requirements

**Common Studio DRM Requirements**:
```
┌────────────────────────────────────────────────────────────────┐
│            Studio Content Protection Requirements               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Tier 1 (New Releases, Blockbusters):                         │
│  - Widevine L1 or FairPlay Secure Enclave required            │
│  - HDCP 2.2 mandatory for 4K, HDCP 1.4 for HD                 │
│  - Forensic watermarking (NexGuard or equivalent)              │
│  - Geographic restrictions (staggered global release)          │
│  - No offline downloads (streaming only)                        │
│  - 4K limited to Premium tier subscribers only                 │
│                                                                 │
│  Tier 2 (Catalog Content, TV Shows):                          │
│  - Widevine L2 acceptable (L1 preferred)                       │
│  - HDCP 1.4 for HD                                             │
│  - Forensic watermarking recommended                            │
│  - Offline downloads allowed (24-48 hour expiry)               │
│                                                                 │
│  Tier 3 (Licensed TV, Older Movies):                          │
│  - Software DRM acceptable (Widevine L3)                       │
│  - HDCP optional                                               │
│  - Watermarking optional                                        │
│  - Standard availability                                        │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 Compliance Monitoring

**Automated Compliance Checks**:
- Daily audits of DRM configuration per title
- Monitoring of watermarking coverage (should be 100%)
- HDCP enforcement verification
- Device security level tracking (% on L1 vs L2 vs L3)
- Piracy monitoring (10K+ piracy sites crawled daily)

## 6. Cost & Impact

### 6.1 Security Infrastructure Costs

**Annual Costs (Estimated)**:
- DRM licensing (Widevine, FairPlay, PlayReady): $50M
- Forensic watermarking (NexGuard): $30M
- License servers (infrastructure): $20M
- Anti-piracy operations: $15M
- Compliance & auditing: $10M
- **Total**: ~$125M/year

### 6.2 Piracy Prevention Impact

**Estimated Impact**:
- Without DRM: 40-60% revenue loss (industry estimates)
- With Netflix's multi-layered security: <5% loss
- **Protected Revenue**: $12-15 billion annually
- **ROI**: 100x+ return on security investment

