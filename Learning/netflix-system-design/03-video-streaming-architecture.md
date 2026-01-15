# Netflix Video Streaming Architecture - System Design

## Overview
Netflix's streaming architecture handles 200+ million subscribers streaming billions of hours of content monthly, with adaptive bitrate streaming, personalized experiences, and sub-second startup times. This document details the complete streaming pipeline from playback request to video delivery.

## 1. Streaming Protocol & Technology Stack

### 1.1 Adaptive Bitrate Streaming (ABR)

**Protocol Selection**:
```
Device Type → Streaming Protocol
├── Web Browser → MPEG-DASH (Dynamic Adaptive Streaming over HTTP)
├── iOS/tvOS → HLS (HTTP Live Streaming)
├── Android → MPEG-DASH
├── Smart TVs → MPEG-DASH or HLS (device-specific)
├── Game Consoles → MPEG-DASH
└── Roku/Fire TV → Custom protocol (optimized)
```

**Why Adaptive Bitrate?**
- **Network Variability**: Internet bandwidth fluctuates (WiFi, mobile, ISP congestion)
- **Device Diversity**: Phones to 4K TVs with different capabilities
- **Quality vs Buffering**: Balance best quality with smooth playback
- **Cost Optimization**: Reduce bandwidth for users who don't need 4K

### 1.2 MPEG-DASH Technical Details

**Manifest Structure (MPD - Media Presentation Description)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" 
     type="static" 
     mediaPresentationDuration="PT2H15M30S"
     minBufferTime="PT4S">
  
  <!-- Period represents the entire movie/episode -->
  <Period id="0" duration="PT2H15M30S">
    
    <!-- Video Adaptation Sets (different codecs/profiles) -->
    <AdaptationSet id="video" 
                   mimeType="video/mp4" 
                   codecs="hvc1.2.4.L150.B0"
                   frameRate="24000/1001"
                   segmentAlignment="true"
                   startWithSAP="1">
      
      <!-- 4K HDR Representation -->
      <Representation id="4k_hdr" 
                      bandwidth="25000000" 
                      width="3840" 
                      height="2160">
        <SegmentTemplate timescale="24000"
                         initialization="init-4k-hdr.mp4"
                         media="segment-4k-hdr-$Number$.m4s"
                         startNumber="1"
                         duration="96000"/>
      </Representation>
      
      <!-- 1080p Representation -->
      <Representation id="1080p_high" 
                      bandwidth="8000000" 
                      width="1920" 
                      height="1080">
        <SegmentTemplate timescale="24000"
                         initialization="init-1080p-high.mp4"
                         media="segment-1080p-high-$Number$.m4s"
                         startNumber="1"
                         duration="96000"/>
      </Representation>
      
      <!-- Additional representations for 720p, 480p, 360p, 240p -->
      <!-- ... -->
      
    </AdaptationSet>
    
    <!-- Audio Adaptation Sets (multiple languages) -->
    <AdaptationSet id="audio_eng" 
                   mimeType="audio/mp4" 
                   codecs="ec-3"
                   lang="en">
      
      <!-- Dolby Atmos -->
      <Representation id="eng_atmos" 
                      bandwidth="768000" 
                      audioSamplingRate="48000">
        <SegmentTemplate timescale="48000"
                         initialization="init-eng-atmos.mp4"
                         media="segment-eng-atmos-$Number$.m4s"
                         startNumber="1"
                         duration="192000"/>
      </Representation>
      
      <!-- 5.1 Surround -->
      <Representation id="eng_51" 
                      bandwidth="448000" 
                      audioSamplingRate="48000">
        <SegmentTemplate timescale="48000"
                         initialization="init-eng-51.mp4"
                         media="segment-eng-51-$Number$.m4s"
                         startNumber="1"
                         duration="192000"/>
      </Representation>
      
    </AdaptationSet>
    
    <!-- Additional audio languages (Spanish, French, German, etc.) -->
    <!-- ... -->
    
    <!-- Subtitle Adaptation Sets -->
    <AdaptationSet id="subtitle_eng" 
                   mimeType="text/vtt" 
                   lang="en">
      <Representation id="eng_sub">
        <BaseURL>subtitles/eng.vtt</BaseURL>
      </Representation>
    </AdaptationSet>
    
  </Period>
</MPD>
```

**Segment Details**:
- **Duration**: 4 seconds per segment
- **GOP (Group of Pictures)**: 96 frames @ 24fps (exactly 4 seconds)
- **Keyframe Alignment**: All profiles have keyframes at same timestamps
- **Why 4 seconds?**
  - Fast startup: Download 1 segment and start playing
  - Quick adaptation: Switch quality every 4 seconds
  - Seek performance: Jump to any 4-second boundary
  - Balance: Smaller = more overhead, Larger = slower adaptation

### 1.3 Streaming Session Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Client Device                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           Netflix Application Layer                         │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Playback Controller (React/React Native)            │  │  │
│  │  │  - User interaction (play, pause, seek, volume)      │  │  │
│  │  │  - Subtitle rendering                                 │  │  │
│  │  │  - Quality selection (auto/manual)                    │  │  │
│  │  └────────────┬─────────────────────────────────────────┘  │  │
│  │               ▼                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  ABR Engine (Adaptive Bitrate Logic)                 │  │  │
│  │  │  - Network bandwidth measurement                      │  │  │
│  │  │  - Buffer level monitoring                            │  │  │
│  │  │  - Quality selection algorithm                        │  │  │
│  │  │  - Predictive pre-fetching                            │  │  │
│  │  └────────────┬─────────────────────────────────────────┘  │  │
│  │               ▼                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Media Source Extensions (MSE) / ExoPlayer / AVPlayer│  │  │
│  │  │  - Segment downloading                                │  │  │
│  │  │  - Buffer management (20-30 seconds)                  │  │  │
│  │  │  - Decoding & rendering                               │  │  │
│  │  └────────────┬─────────────────────────────────────────┘  │  │
│  └───────────────┼──────────────────────────────────────────┘  │
│                  │                                              │
└──────────────────┼──────────────────────────────────────────────┘
                   │ HTTPS Requests (byte-range)
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CDN Layer (CloudFront / OCA)                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Edge Location Cache                                       │  │
│  │  - Manifest caching (5 minutes TTL)                        │  │
│  │  - Segment caching (24 hours TTL)                          │  │
│  │  - Cache hit ratio: 90-95%                                 │  │
│  └────────────────┬───────────────────────────────────────────┘  │
└────────────────────┼──────────────────────────────────────────────┘
                     │ Cache Miss
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│               Origin Server (AWS S3 / OCA Fill Server)            │
│  - Encoded video segments                                        │
│  - Multi-region redundancy                                       │
│  - Throughput: 100GB/s+                                          │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Playback Session Flow

### 2.1 Session Initialization

**Step-by-Step Flow**:

```
User clicks "Play" button
    ↓
1. Authentication & Authorization (50-100ms)
   ├─→ JWT token validation
   ├─→ DRM license server check
   ├─→ Regional availability check (RDS query)
   └─→ Subscription tier validation
    ↓
2. Playback API Request (100-200ms)
   Request: POST /api/v1/playback/start
   Headers: Authorization: Bearer <JWT>
   Body: {
     "content_id": "12345678",
     "profile": "4k_hdr",
     "device_id": "device_abc123",
     "client_version": "7.105.0"
   }
   
   Response: {
     "session_id": "session_xyz789",
     "manifest_url": "https://cdn.netflix.com/content/12345678/master.mpd",
     "drm_license_url": "https://license.netflix.com/widevine",
     "bookmark": 0,  // Resume position
     "expiry": "2026-01-15T12:00:00Z"
   }
    ↓
3. Manifest Download (50-100ms)
   GET https://cdn.netflix.com/content/12345678/master.mpd
   - Client downloads MPD manifest
   - Parses available profiles (4K, 1080p, 720p, etc.)
   - Selects initial profile based on device capability
    ↓
4. DRM License Acquisition (100-200ms)
   - Client generates license challenge
   - Sends to DRM license server (Widevine/PlayReady/FairPlay)
   - Receives decryption keys
   - Stores keys in secure hardware (TEE/Secure Enclave)
    ↓
5. Initial Buffer Loading (500ms-2s)
   - Download first 2-3 segments (8-12 seconds)
   - Decrypt and decode
   - Fill buffer to minimum level (4-8 seconds)
    ↓
6. Playback Start (<2 seconds total startup time)
   - Video starts playing
   - Continue downloading segments in background
```

**Startup Time Optimization**:
- **Target**: <2 seconds from click to playback
- **Techniques**:
  - Parallel manifest and license requests
  - Pre-warming connections (HTTP/2 persistent connections)
  - Predictive pre-fetching (likely content to be played)
  - Lower initial quality (fast start, then adapt up)
  - Smaller initial segments (2 seconds vs 4 seconds)

### 2.2 ABR Algorithm (Quality Selection)

**Network Bandwidth Measurement**:
```python
class BandwidthEstimator:
    def __init__(self):
        self.measurements = []  # Last 10 segment downloads
        self.ewma_bandwidth = 0  # Exponential weighted moving average
        
    def measure_download(self, segment_size_bytes, download_time_ms):
        # Calculate instantaneous bandwidth
        bandwidth_kbps = (segment_size_bytes * 8) / download_time_ms
        
        # Add to measurements
        self.measurements.append(bandwidth_kbps)
        if len(self.measurements) > 10:
            self.measurements.pop(0)
        
        # Calculate EWMA (70% recent, 30% historical)
        if self.ewma_bandwidth == 0:
            self.ewma_bandwidth = bandwidth_kbps
        else:
            self.ewma_bandwidth = (0.7 * bandwidth_kbps) + 
                                   (0.3 * self.ewma_bandwidth)
        
        return self.ewma_bandwidth
```

**Quality Selection Algorithm**:
```python
class ABRController:
    def __init__(self):
        self.current_quality = "720p_medium"
        self.buffer_level = 0  # seconds
        self.bandwidth_estimator = BandwidthEstimator()
        
        # Available profiles (sorted by bitrate)
        self.profiles = [
            {"id": "240p", "bitrate": 300, "resolution": "426x240"},
            {"id": "360p", "bitrate": 600, "resolution": "640x360"},
            {"id": "480p", "bitrate": 1000, "resolution": "854x480"},
            {"id": "720p_medium", "bitrate": 2000, "resolution": "1280x720"},
            {"id": "720p_high", "bitrate": 3000, "resolution": "1280x720"},
            {"id": "1080p_medium", "bitrate": 5000, "resolution": "1920x1080"},
            {"id": "1080p_high", "bitrate": 8000, "resolution": "1920x1080"},
            {"id": "4k_sdr", "bitrate": 20000, "resolution": "3840x2160"},
            {"id": "4k_hdr", "bitrate": 25000, "resolution": "3840x2160"},
        ]
    
    def select_quality(self, available_bandwidth_kbps, buffer_level_sec):
        # Safety margin: Use 85% of measured bandwidth
        safe_bandwidth = available_bandwidth_kbps * 0.85
        
        # Buffer-based selection
        if buffer_level_sec < 5:  # Low buffer - PANIC
            # Drop to lowest quality to refill buffer quickly
            target_profile = self.profiles[0]
        elif buffer_level_sec < 10:  # Medium buffer - CONSERVATIVE
            # Stay at current or slightly lower quality
            target_profile = self.get_conservative_profile(safe_bandwidth)
        else:  # High buffer - AGGRESSIVE
            # Can afford to try higher quality
            target_profile = self.get_best_profile(safe_bandwidth)
        
        # Device capability check
        target_profile = self.limit_by_device_capability(target_profile)
        
        # Smooth transitions (avoid frequent quality changes)
        if self.should_switch_quality(target_profile):
            self.current_quality = target_profile["id"]
            
        return self.current_quality
    
    def get_best_profile(self, bandwidth_kbps):
        # Return highest quality that fits in bandwidth
        for profile in reversed(self.profiles):
            if profile["bitrate"] <= bandwidth_kbps:
                return profile
        return self.profiles[0]  # Fallback to lowest
    
    def get_conservative_profile(self, bandwidth_kbps):
        # Return quality one level below what bandwidth allows
        best = self.get_best_profile(bandwidth_kbps)
        idx = self.profiles.index(best)
        if idx > 0:
            return self.profiles[idx - 1]
        return best
    
    def should_switch_quality(self, target_profile):
        # Avoid switching too frequently (hysteresis)
        # Only switch if:
        # 1. Significant quality improvement (2+ levels up)
        # 2. Necessary drop (current profile not sustainable)
        # 3. At least 10 seconds since last switch
        
        current_idx = self.get_profile_index(self.current_quality)
        target_idx = self.get_profile_index(target_profile["id"])
        
        if target_idx < current_idx - 1:  # Drop 2+ levels
            return True
        if target_idx > current_idx + 1:  # Improve 2+ levels
            return True
        if self.time_since_last_switch() > 10:
            return True
        
        return False
```

**ABR Metrics**:
- **Quality Adaptation Frequency**: 1-2 switches per minute (average)
- **Upward Switch Delay**: 10-20 seconds (ensure bandwidth is stable)
- **Downward Switch Speed**: <4 seconds (prevent buffering)
- **Buffer Target**: 20-30 seconds (optimal balance)

### 2.3 Buffering Strategy

**Buffer Management**:
```
┌────────────────────────────────────────────────────────────────┐
│                    Video Buffer                                 │
│                                                                 │
│  ┌───────┬───────┬───────┬───────┬───────┬───────┬─────────┐  │
│  │ Played│ Play  │ Next  │ Next  │ Next  │ Next  │ Fetching │  │
│  │ (4s)  │ (4s)  │ (4s)  │ (4s)  │ (4s)  │ (4s)  │  (4s)   │  │
│  └───────┴───────┴───────┴───────┴───────┴───────┴─────────┘  │
│           ↑                                                     │
│       Playhead                                                  │
│                                                                 │
│  Buffer Status:                                                 │
│  - Minimum: 4 seconds (start playback)                         │
│  - Target: 20-30 seconds (steady state)                        │
│  - Maximum: 60 seconds (cap to save bandwidth)                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Buffer Rules**:
1. **Initial Buffer**: Download 2-3 segments (8-12 seconds) before playback
2. **Steady State**: Maintain 20-30 seconds ahead
3. **Low Buffer (<10s)**: Aggressive downloading + quality drop
4. **High Buffer (>40s)**: Slow down downloads to save bandwidth
5. **Buffer Starvation (0s)**: Display loading spinner, pause playback

**Segment Prefetching**:
```python
class SegmentDownloader:
    def __init__(self):
        self.download_queue = []
        self.active_downloads = 0
        self.max_parallel_downloads = 3
        
    def schedule_downloads(self, current_segment_index, buffer_level):
        # Calculate how many segments ahead to download
        if buffer_level < 10:
            # Low buffer: aggressive downloading
            segments_to_fetch = 5
        elif buffer_level < 20:
            # Medium buffer: normal downloading
            segments_to_fetch = 3
        else:
            # High buffer: slow down
            segments_to_fetch = 1
        
        # Add segments to download queue
        for i in range(segments_to_fetch):
            segment_index = current_segment_index + buffer_level / 4 + i
            if segment_index not in self.download_queue:
                self.download_queue.append(segment_index)
        
        # Start parallel downloads
        while (self.active_downloads < self.max_parallel_downloads and 
               len(self.download_queue) > 0):
            segment_index = self.download_queue.pop(0)
            self.download_segment_async(segment_index)
```

### 2.4 Seeking & Trick Play

**Seek Operation**:
```
User drags seek bar to t=1234 seconds
    ↓
1. Calculate target segment
   segment_index = floor(1234 / 4) = 308
   segment_timestamp = 308 * 4 = 1232 seconds
    ↓
2. Clear current buffer
   - Abort in-flight downloads
   - Clear buffered segments
    ↓
3. Download target segment (keyframe)
   GET /segment-1080p-high-308.m4s
   - Always starts at keyframe (SAP Type 1)
   - Instant decode without waiting for previous frames
    ↓
4. Resume playback at new position
   - Download next 2-3 segments for buffer
   - Start playback within 500ms
```

**Trick Play (Preview Thumbnails)**:
```
User hovers over seek bar at t=1234 seconds
    ↓
1. Calculate thumbnail index
   thumbnail_index = floor(1234 / 10) = 123  // Every 10 seconds
    ↓
2. Load thumbnail sprite sheet
   GET /thumbnails/sprite_12.jpg
   - Sprite sheet contains 25 thumbnails (250 seconds)
   - Each thumbnail: 160x90 pixels
   - Layout: 5 columns × 5 rows
    ↓
3. Extract specific thumbnail
   column = 123 % 5 = 3
   row = floor(123 / 5) % 5 = 4
   crop: (3*160, 4*90, 160, 90)
    ↓
4. Display in seek bar tooltip
   - Show thumbnail + timestamp
   - Update in real-time as user moves cursor
```

## 3. Content Type Specific Streaming

### 3.1 Movies

**Characteristics**:
- **Duration**: 90-180 minutes (typical)
- **Content Structure**: Single continuous stream
- **Viewing Pattern**: Watch from start to finish (70%+ completion rate)
- **Optimization**: Pre-fetch entire movie during playback

**Streaming Strategy**:
```python
class MovieStreamingStrategy:
    def optimize_playback(self, movie_duration_sec, bandwidth_kbps):
        # Pre-download strategy
        if bandwidth_kbps > 10000:  # High bandwidth
            # Download entire movie in background
            # Target: Complete download within 30 minutes
            download_speed_multiplier = movie_duration_sec / 1800
            
        # Quality selection
        if movie_duration_sec > 7200:  # >2 hours
            # Longer movies: optimize for consistency
            quality_switches_allowed = 5
        else:
            # Shorter movies: more aggressive quality
            quality_switches_allowed = 10
        
        return {
            "prefetch_strategy": "aggressive",
            "quality_stability": "high",
            "buffer_target": 30  # seconds
        }
```

### 3.2 TV Series Episodes

**Characteristics**:
- **Duration**: 20-60 minutes (typical)
- **Content Structure**: Part of a series
- **Viewing Pattern**: Binge-watching (60%+ watch next episode)
- **Optimization**: Pre-fetch next episode during credits

**Auto-Play Next Episode**:
```
Current episode playback reaches t=2400s (40 minutes)
Episode duration: 2700s (45 minutes)
Remaining: 300s (5 minutes = credits)
    ↓
1. Detect credits sequence
   - ML model identifies credit roll (95% accuracy)
   - Timestamp: t=2430s (last 4.5 minutes)
    ↓
2. Show "Next Episode" countdown
   - UI overlay: "Next episode in 15 seconds"
   - User can cancel auto-play
    ↓
3. Pre-fetch next episode manifest
   GET /api/v1/playback/next-episode?current_id=12345678
   Response: {
     "next_episode_id": "12345679",
     "manifest_url": "...",
     "skip_intro_timestamp": 45  // seconds
   }
    ↓
4. Pre-download first segments of next episode
   - Download segments 0-5 (20 seconds) in background
   - Store in separate buffer
    ↓
5. Seamless transition (t=2685s)
   - Fade out current episode
   - Fade in next episode
   - Auto-skip intro (if user enabled)
   - Total interruption: <500ms
```

**Binge-Watching Optimization**:
- **Next Episode Prediction**: 80% probability user continues
- **Pre-fetch Timing**: Start at 80% completion of current episode
- **Bandwidth Strategy**: Use idle bandwidth during current playback
- **Storage**: Cache next 2 episodes locally (if space available)

### 3.3 Live Events (Experimental)

**Netflix is primarily VOD, but has limited live streaming**:
- Live stand-up comedy specials
- Interactive events (e.g., "Is It Cake?" live)

**Live Streaming Architecture**:
```
┌───────────────────────────────────────────────────────────────┐
│                   Live Event Venue                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Camera Feed → Video Encoder (H.265/AVC)                 │ │
│  │  Audio Feed → Audio Encoder (AAC/Opus)                   │ │
│  └────────────────────┬─────────────────────────────────────┘ │
└────────────────────────┼──────────────────────────────────────┘
                         │ RTMP/SRT
                         ▼
┌───────────────────────────────────────────────────────────────┐
│          AWS Elemental MediaLive (Transcoding)                │
│  - Ingest live feed                                           │
│  - Transcode to multiple profiles (same as VOD)               │
│  - Output: HLS/DASH chunks (2-second segments)                │
│  - Latency: 6-10 seconds (glass-to-glass)                     │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────┐
│          AWS Elemental MediaPackage (Packaging)               │
│  - Convert to HLS/DASH                                        │
│  - DRM encryption (on-the-fly)                                │
│  - DVR functionality (4-hour rewind)                          │
│  - Manifest generation (updated every 2 seconds)              │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────┐
│                  CloudFront (Distribution)                     │
│  - Cache segments (TTL: 4 seconds for live)                   │
│  - Manifest no-cache (always fetch latest)                    │
│  - Scale to millions of concurrent viewers                    │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     ▼
                Client Devices
```

**Live vs VOD Differences**:
- **Latency**: 6-10 seconds (live) vs instant (VOD)
- **Segment Duration**: 2 seconds (live) vs 4 seconds (VOD)
- **Buffer Target**: 10-15 seconds (live) vs 20-30 seconds (VOD)
- **Seek**: Limited (DVR window) vs full movie (VOD)

### 3.4 Interactive Content (e.g., Black Mirror: Bandersnatch)

**Characteristics**:
- **Branching Narratives**: User makes choices affecting story
- **Decision Points**: 5-10 choices per show
- **Complexity**: ~5 hours of total footage for a 90-minute show

**Technical Implementation**:
```
┌───────────────────────────────────────────────────────────────┐
│                Interactive Content Structure                   │
│                                                                │
│  Scene Graph:                                                  │
│  ┌─────┐     ┌─────┐     ┌─────┐                            │
│  │  1  │────▶│  2  │────▶│  3  │────▶ Ending A              │
│  └─────┘     └─────┘     └─────┘                            │
│                  │           │                                 │
│                  │           └─────▶ Scene 4 ────▶ Ending B  │
│                  │                                             │
│                  └─────▶ Scene 5 ────▶ Ending C              │
│                                                                │
└───────────────────────────────────────────────────────────────┘

Decision Point at t=300s:
    ↓
1. Pause playback, show choice UI
   - "Accept job offer?"
   - Option A: "Accept"  → scene_6
   - Option B: "Decline" → scene_7
    ↓
2. Pre-fetch both branches
   - Download first segment of scene_6
   - Download first segment of scene_7
   - Both ready in buffer (no delay)
    ↓
3. User selects Option A within 10 seconds
   - Resume playback with scene_6
   - Discard scene_7 buffer
    ↓
4. Record decision for analytics
   POST /api/v1/interactive/decision
   Body: {
     "content_id": "interactive_123",
     "scene_id": "scene_5",
     "decision_id": "decision_2",
     "choice": "option_a",
     "timestamp": 1705318800
   }
```

**Storage Implications**:
- **Total Content**: 3-5x regular episode length
- **Pre-fetching**: All possible next scenes (2-3 options)
- **Bandwidth**: 50% higher than regular streaming
- **Encoding**: Each scene segment encoded independently

**Interactive Content Manifest** (Custom Format):
```json
{
  "content_id": "interactive_123",
  "title": "Black Mirror: Bandersnatch",
  "initial_scene": "scene_1",
  "scenes": [
    {
      "scene_id": "scene_1",
      "duration": 180,
      "video_url": "/content/interactive_123/scene_1/",
      "next": "scene_2"
    },
    {
      "scene_id": "scene_2",
      "duration": 240,
      "video_url": "/content/interactive_123/scene_2/",
      "decision": {
        "decision_id": "decision_1",
        "timestamp": 220,
        "timeout": 10,
        "prompt": "Which cereal?",
        "options": [
          {
            "id": "option_a",
            "label": "Sugar Puffs",
            "next_scene": "scene_3"
          },
          {
            "id": "option_b",
            "label": "Frosties",
            "next_scene": "scene_4"
          }
        ]
      }
    }
  ]
}
```

## 4. Streaming Performance Optimization

### 4.1 Predictive Pre-fetching

**User Behavior Prediction**:
```python
class PredictivePrefetcher:
    def predict_next_action(self, user_history, current_content):
        # Predict what user will do next
        predictions = {
            "continue_watching": 0.0,  # Continue current content
            "next_episode": 0.0,        # Auto-play next episode
            "browse": 0.0,              # Return to browse
            "exit": 0.0                 # Close app
        }
        
        # Factors:
        # 1. Time of day
        # 2. Historical binge-watching patterns
        # 3. Content type (episode vs movie)
        # 4. Viewing progress (10% vs 90%)
        
        if current_content["type"] == "episode":
            if user_history["binge_rate"] > 0.7:  # 70% continue to next
                predictions["next_episode"] = 0.75
                predictions["browse"] = 0.15
                predictions["exit"] = 0.10
        
        return predictions
    
    def prefetch_content(self, predictions, current_content):
        if predictions["next_episode"] > 0.6:
            # High probability: pre-fetch next episode
            next_episode_id = self.get_next_episode(current_content["id"])
            self.download_first_segments(next_episode_id, segments=5)
            
        if predictions["browse"] > 0.3:
            # Medium probability: pre-fetch homepage recommendations
            self.prefetch_thumbnails(user_homepage)
```

### 4.2 Startup Time Optimization

**Parallel Initialization**:
```javascript
// Client-side optimization
async function initializePlayback(contentId) {
    // Start all API calls in parallel
    const [
        playbackData,
        manifest,
        drmLicense,
        bookmarkPosition
    ] = await Promise.all([
        fetchPlaybackAPI(contentId),     // 100ms
        fetchManifest(contentId),         // 50ms
        fetchDRMLicense(contentId),       // 150ms
        fetchBookmark(contentId)          // 30ms
    ]);
    
    // Total time: ~150ms (max of all parallel calls)
    // vs ~330ms if sequential
    
    // Start downloading first segments while DRM initializes
    const segmentPromises = [];
    for (let i = 0; i < 3; i++) {
        segmentPromises.push(downloadSegment(i));
    }
    
    // Wait for DRM and first segments
    await Promise.all([
        initializeDRM(drmLicense),
        ...segmentPromises
    ]);
    
    // Start playback
    player.play();
}
```

**Startup Time Distribution** (Target <2 seconds):
- API calls: 150ms (parallel)
- Manifest download: 50ms
- DRM initialization: 150ms
- First segment download: 500ms (over 5 Mbps network)
- Decoding & rendering: 100ms
- **Total**: ~950ms - 1.5 seconds

### 4.3 Quality of Experience (QoE) Metrics

**Key Metrics**:
```python
class QoEMetrics:
    def calculate_qoe_score(self, session_data):
        metrics = {
            "startup_time": session_data["time_to_first_frame"],  # ms
            "rebuffering_ratio": session_data["total_rebuffer_time"] / 
                                  session_data["play_duration"],    # %
            "rebuffering_count": session_data["rebuffer_events"],   # count
            "average_bitrate": session_data["average_bitrate"],     # kbps
            "bitrate_switches": session_data["quality_switches"],   # count
            "completion_rate": session_data["watched_duration"] / 
                               session_data["content_duration"]     # %
        }
        
        # Calculate composite QoE score (0-100)
        qoe_score = (
            (100 - min(metrics["startup_time"] / 30, 100)) * 0.2 +     # 20%
            (100 - metrics["rebuffering_ratio"] * 1000) * 0.3 +        # 30%
            (100 - min(metrics["rebuffering_count"] * 10, 100)) * 0.2 + # 20%
            (metrics["average_bitrate"] / 250) * 0.2 +                 # 20%
            (100 - min(metrics["bitrate_switches"] * 5, 100)) * 0.1    # 10%
        )
        
        return max(0, min(100, qoe_score))

# Target QoE Metrics (p95):
# - Startup time: <2 seconds
# - Rebuffering ratio: <0.5% (30 seconds per hour)
# - Rebuffering count: <1 per session
# - Average bitrate: >3 Mbps
# - Quality switches: <5 per session
# - Completion rate: >80% (for engaged users)
```

## 5. Error Handling & Resilience

### 5.1 Network Errors

**Retry Strategy**:
```python
class NetworkErrorHandler:
    def download_segment(self, segment_url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    segment_url,
                    timeout=10,  # 10-second timeout
                    headers={"Range": "bytes=0-"}  # Support resume
                )
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 416:  # Range not satisfiable
                    # Re-try without range header
                    response = requests.get(segment_url, timeout=10)
                    return response.content
                elif response.status_code == 503:  # Service unavailable
                    # CDN overloaded, try alternate CDN
                    alternate_url = self.get_alternate_cdn(segment_url)
                    return self.download_segment(alternate_url, max_retries-1)
                    
            except requests.exceptions.Timeout:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                
            except requests.exceptions.ConnectionError:
                # Network disruption, wait and retry
                time.sleep(5)
                
        # All retries failed
        raise SegmentDownloadError(f"Failed to download {segment_url}")
```

### 5.2 DRM Errors

**License Server Failure**:
```python
def handle_drm_error(error_code):
    if error_code == "LICENSE_EXPIRED":
        # Refresh license
        new_license = request_new_license()
        player.update_license(new_license)
        
    elif error_code == "DEVICE_LIMIT_EXCEEDED":
        # User has too many active devices
        show_error_dialog(
            "You've reached the maximum number of devices. "
            "Please sign out of another device to continue."
        )
        
    elif error_code == "HDCP_ERROR":
        # HDCP (copy protection) failure
        # Fall back to SD quality (lower DRM requirements)
        player.set_max_quality("480p")
        player.retry_playback()
        
    elif error_code == "LICENSE_SERVER_UNAVAILABLE":
        # License server down (rare)
        # Retry with exponential backoff
        retry_with_backoff(request_license, max_attempts=5)
```

### 5.3 Graceful Degradation

**Fallback Strategies**:
1. **CDN Failure** → Switch to alternate CDN (OCA → CloudFront → Direct S3)
2. **High Latency** → Reduce quality, increase buffer target
3. **DRM Issues** → Fall back to SD with lower DRM requirements
4. **Slow Device** → Disable 4K, limit to 1080p maximum
5. **Low Memory** → Reduce buffer size, clear thumbnail cache

## 6. Telemetry & Analytics

### 6.1 Real-time Streaming Telemetry

**Metrics Collection**:
```javascript
class StreamingTelemetry {
    constructor() {
        this.metrics = [];
        this.reportInterval = 30000;  // Report every 30 seconds
        setInterval(() => this.reportMetrics(), this.reportInterval);
    }
    
    collectMetric(event) {
        const metric = {
            timestamp: Date.now(),
            session_id: this.sessionId,
            content_id: this.contentId,
            event_type: event.type,
            data: {}
        };
        
        if (event.type === "quality_change") {
            metric.data = {
                from_quality: event.oldQuality,
                to_quality: event.newQuality,
                reason: event.reason,  // "bandwidth" | "buffer" | "manual"
                buffer_level: this.getBufferLevel()
            };
        } else if (event.type === "rebuffer") {
            metric.data = {
                duration_ms: event.duration,
                quality: this.getCurrentQuality(),
                bandwidth_kbps: this.getCurrentBandwidth()
            };
        } else if (event.type === "error") {
            metric.data = {
                error_code: event.code,
                error_message: event.message,
                stack_trace: event.stack
            };
        }
        
        this.metrics.push(metric);
    }
    
    async reportMetrics() {
        if (this.metrics.length === 0) return;
        
        // Batch send to analytics pipeline
        await fetch("/api/v1/telemetry/batch", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                device_id: this.deviceId,
                metrics: this.metrics
            })
        });
        
        this.metrics = [];  // Clear after sending
    }
}
```

**Analytics Pipeline**:
```
Client Devices (200M+ devices)
    ↓ (HTTPS POST batches)
AWS API Gateway + Lambda
    ↓
Amazon Kinesis Data Streams (1M+ events/second)
    ↓ (Real-time processing)
┌──────────────────┬──────────────────┬───────────────────┐
│                  │                  │                   │
▼                  ▼                  ▼                   ▼
Kinesis Analytics  Lambda (Aggregate) S3 (Raw logs)     Amazon
(Real-time alerts) (Real-time dash)   (Long-term)       Redshift
│                  │                  │                   │
└──────────────────┴──────────────────┴──────────────────┘
                            │
                            ▼
                   CloudWatch Dashboard
                   (Real-time monitoring)
```

### 6.2 A/B Testing for Streaming

**Example: Testing New ABR Algorithm**:
```python
class ABTestingController:
    def get_abr_algorithm(self, user_id):
        # Split users into control (90%) and treatment (10%)
        if self.hash_user(user_id) % 10 == 0:
            # Treatment group: new algorithm
            return "abr_v2_aggressive"
        else:
            # Control group: current algorithm
            return "abr_v1_stable"
    
    def compare_results(self):
        # After 7 days, compare metrics
        control_qoe = self.get_qoe_score("abr_v1_stable")
        treatment_qoe = self.get_qoe_score("abr_v2_aggressive")
        
        improvement = (treatment_qoe - control_qoe) / control_qoe * 100
        
        if improvement > 2% and self.is_statistically_significant():
            # Roll out new algorithm to 100% of users
            self.rollout("abr_v2_aggressive")
        else:
            # Keep current algorithm
            self.rollback("abr_v2_aggressive")
```

**Common A/B Tests**:
- ABR algorithm variations (quality selection logic)
- Buffer target sizes (20s vs 30s vs 40s)
- Startup strategies (low-quality fast start vs high-quality delayed)
- Segment duration (2s vs 4s vs 6s)
- Pre-fetching strategies (aggressive vs conservative)

## 7. Cost & Bandwidth Management

### 7.1 Bandwidth Costs

**Breakdown**:
- **CloudFront Data Transfer**: $0.085/GB (first 10TB)
- **OCA (ISP peering)**: $0.01/GB (negotiated rates)
- **S3 Egress**: $0.09/GB (to internet)

**Monthly Bandwidth** (Estimated):
- 200M subscribers × 50 hours/month × 3 Mbps average = 270 petabytes
- **CloudFront cost**: $22.95M (assuming 50% cache hit)
- **OCA cost**: $2.7M (50% served from OCA)
- **Total**: ~$25M/month bandwidth cost

### 7.2 Bandwidth Optimization

**Techniques**:
1. **Per-Title Encoding**: Optimize bitrate ladder per content (not one-size-fits-all)
2. **Perceptual Quality**: ML-based encoding (lower bitrate, same perceived quality)
3. **CDN Hit Ratio**: 90%+ cache hit rate reduces origin egress
4. **OCA Deployment**: 95%+ traffic served from ISP-hosted OCAs
5. **Codec Efficiency**: H.265 (30% savings) and AV1 (40-50% savings, rolling out)

**Savings from Optimizations**:
- Per-title encoding: 20% bitrate reduction = $5M/month saved
- OCA deployment: 90% cost reduction on served traffic = $20M/month saved
- Total savings: **$300M+/year**

