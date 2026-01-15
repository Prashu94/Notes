# Netflix Encoding & Transcoding Pipeline - System Design

## Overview
Netflix's encoding pipeline transforms raw source files into hundreds of optimized streaming variants, processing thousands of hours of content daily with custom encoding algorithms that save petabytes of storage and billions in bandwidth costs.

## 1. Encoding Architecture

### 1.1 High-Level Encoding Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│                    Raw Source File                              │
│  Format: ProRes 4444, DNxHR 444                                │
│  Resolution: 4K (3840x2160) or higher                          │
│  Size: 800GB - 2TB for 2-hour movie                            │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│              Pre-Processing & Analysis                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Shot Detection                                           │ │
│  │  - Identify scene changes                                 │ │
│  │  - Detect fade in/out                                     │ │
│  │  - Find opening/closing credits                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Content Analysis (Netflix VMAF)                          │ │
│  │  - Complexity per scene (grain, motion, detail)           │ │
│  │  - Optimal encoding parameters                            │ │
│  │  - Per-title bitrate ladder recommendation                │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Audio Analysis                                           │ │
│  │  - Dialogue detection (dialogue vs music vs effects)      │ │
│  │  - Loudness normalization (LKFS measurement)              │ │
│  │  - Dynamic range analysis                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│              Parallel Encoding Jobs                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 4K HDR Job   │  │ 4K SDR Job   │  │ 1080p Job    │        │
│  │ 25 Mbps      │  │ 20 Mbps      │  │ 8/5 Mbps     │        │
│  │ HEVC Main10  │  │ HEVC Main    │  │ HEVC/AVC     │        │
│  │ 1x instance  │  │ 1x instance  │  │ 1x instance  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 720p Job     │  │ 480p Job     │  │ 240p Job     │        │
│  │ 3/2 Mbps     │  │ 1 Mbps       │  │ 0.3 Mbps     │        │
│  │ AVC High     │  │ AVC Main     │  │ AVC Baseline │        │
│  │ 1x instance  │  │ 1x instance  │  │ 1x instance  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  (Each job runs on dedicated EC2 instance or AWS Batch)        │
│  Total: 30-40 video encodes × 40-50 audio encodes = 1200+ jobs│
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│              Post-Processing & Packaging                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Segmentation (4-second chunks)                           │ │
│  │  - Cut at keyframe boundaries                             │ │
│  │  - Generate initialization segments                        │ │
│  │  - Create DASH/HLS manifests                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  DRM Encryption                                           │ │
│  │  - Widevine (Android, Chrome, Edge)                       │ │
│  │  - PlayReady (Windows, Xbox)                              │ │
│  │  - FairPlay (iOS, Safari, Apple TV)                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Quality Validation                                       │ │
│  │  - VMAF score calculation (target: >95)                   │ │
│  │  - A/V sync validation (<40ms offset)                     │ │
│  │  - Playback testing (automated)                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│            Encoded Assets Storage (S3)                          │
│  30-40 video profiles × 40-50 audio tracks                     │
│  Total size: 80GB-150GB for 2-hour movie                       │
└────────────────────────────────────────────────────────────────┘
```

## 2. Per-Title Encoding (Netflix Innovation)

### 2.1 Concept

**Traditional Encoding**: One-size-fits-all bitrate ladder
- Simple animation (e.g., BoJack Horseman): Wastes bandwidth on high bitrates
- Complex action movie (e.g., Extraction): Insufficient quality at standard bitrates

**Per-Title Encoding**: Custom bitrate ladder per content
- Analyze content complexity
- Optimize bitrate allocation
- 20-30% bitrate savings while maintaining quality

### 2.2 Implementation

**Analysis Phase**:
```python
class ContentComplexityAnalyzer:
    def analyze_content(self, video_file):
        """
        Analyze video content to determine optimal encoding parameters
        """
        # Extract sample frames (every 5 seconds)
        sample_frames = self.extract_frames(video_file, interval=5)
        
        complexity_scores = []
        for frame in sample_frames:
            # Spatial complexity (texture, detail)
            spatial = self.calculate_spatial_complexity(frame)
            
            # Temporal complexity (motion)
            temporal = self.calculate_temporal_complexity(frame, prev_frame)
            
            # Combined score
            complexity = (spatial * 0.6) + (temporal * 0.4)
            complexity_scores.append(complexity)
            
            prev_frame = frame
        
        # Calculate statistics
        avg_complexity = np.mean(complexity_scores)
        p95_complexity = np.percentile(complexity_scores, 95)
        
        return {
            "average_complexity": avg_complexity,
            "p95_complexity": p95_complexity,
            "content_category": self.categorize_complexity(avg_complexity)
        }
    
    def calculate_spatial_complexity(self, frame):
        """
        Measure spatial complexity using Laplacian variance
        Higher values = more detail/texture
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    def calculate_temporal_complexity(self, current_frame, previous_frame):
        """
        Measure motion/temporal complexity using optical flow
        Higher values = more motion
        """
        if previous_frame is None:
            return 0
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev=cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY),
            next=cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY),
            flow=None, pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        # Calculate magnitude of motion vectors
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        return np.mean(magnitude)
    
    def categorize_complexity(self, complexity_score):
        """
        Categorize content into complexity buckets
        """
        if complexity_score < 10:
            return "simple_animation"       # e.g., simple cartoons
        elif complexity_score < 30:
            return "moderate_animation"      # e.g., Pixar movies
        elif complexity_score < 60:
            return "live_action_dialogue"    # e.g., dramas, comedies
        elif complexity_score < 100:
            return "action_medium"           # e.g., moderate action
        else:
            return "action_high"             # e.g., intense action, grain
```

**Bitrate Ladder Generation**:
```python
class BitrateOptimizer:
    # Standard bitrate ladder (baseline)
    STANDARD_LADDER = [
        {"resolution": "240p", "bitrate": 300},
        {"resolution": "360p", "bitrate": 600},
        {"resolution": "480p", "bitrate": 1000},
        {"resolution": "720p", "bitrate": 2500},
        {"resolution": "1080p", "bitrate": 5000},
        {"resolution": "4K", "bitrate": 20000}
    ]
    
    def generate_optimal_ladder(self, content_analysis):
        """
        Generate custom bitrate ladder based on content complexity
        """
        complexity = content_analysis["average_complexity"]
        category = content_analysis["content_category"]
        
        # Adjustment factors based on content category
        if category == "simple_animation":
            bitrate_multiplier = 0.5  # Can use much lower bitrates
        elif category == "moderate_animation":
            bitrate_multiplier = 0.7
        elif category == "live_action_dialogue":
            bitrate_multiplier = 0.9
        elif category == "action_medium":
            bitrate_multiplier = 1.0  # Standard
        else:  # action_high
            bitrate_multiplier = 1.3  # Need higher bitrates
        
        # Generate custom ladder
        custom_ladder = []
        for profile in self.STANDARD_LADDER:
            custom_bitrate = int(profile["bitrate"] * bitrate_multiplier)
            custom_ladder.append({
                "resolution": profile["resolution"],
                "bitrate": custom_bitrate
            })
        
        # Validate with convex hull optimization
        validated_ladder = self.convex_hull_optimization(
            custom_ladder, 
            content_analysis
        )
        
        return validated_ladder
    
    def convex_hull_optimization(self, ladder, content_analysis):
        """
        Use convex hull to find Pareto-optimal bitrate-quality curve
        Remove inefficient encoding points
        """
        # For each bitrate in ladder, encode short sample clip
        # and measure VMAF quality
        quality_points = []
        
        sample_clip = self.extract_sample_clip(content_analysis["video_file"])
        
        for profile in ladder:
            encoded_sample = self.encode_sample(
                sample_clip,
                resolution=profile["resolution"],
                bitrate=profile["bitrate"]
            )
            
            vmaf_score = self.calculate_vmaf(
                reference=sample_clip,
                distorted=encoded_sample
            )
            
            quality_points.append({
                "bitrate": profile["bitrate"],
                "vmaf": vmaf_score,
                "resolution": profile["resolution"]
            })
        
        # Find convex hull (optimal quality-bitrate tradeoff)
        optimal_points = self.find_convex_hull(quality_points)
        
        return optimal_points
```

**Example Bitrate Ladders**:

| Content Type | 240p | 360p | 480p | 720p | 1080p | 4K |
|--------------|------|------|------|------|-------|-----|
| **Simple Animation** (BoJack Horseman) | 150 | 300 | 500 | 1200 | 2500 | 8000 |
| **Moderate Animation** (Pixar) | 200 | 400 | 700 | 1800 | 3500 | 12000 |
| **Dialogue Heavy** (The Crown) | 270 | 540 | 900 | 2200 | 4500 | 18000 |
| **Standard** (Baseline) | 300 | 600 | 1000 | 2500 | 5000 | 20000 |
| **Action/Grain** (Extraction) | 390 | 780 | 1300 | 3200 | 6500 | 26000 |

**Savings**:
- Simple animation: 50-60% bitrate reduction
- Moderate animation: 30-40% reduction
- Average across catalog: 20-30% reduction
- **Total savings**: Petabytes of storage, $300M+ annually in bandwidth

## 3. Video Encoding Technology

### 3.1 Codec Selection

**H.264 (AVC) - Legacy/Compatibility**:
- **Usage**: 240p-720p profiles, older devices
- **Profile**: Baseline (240p-360p), Main (480p), High (720p+)
- **Encoder**: x264 (open source, highly optimized)
- **Pros**: Universal compatibility, hardware decode everywhere
- **Cons**: Lower compression efficiency (1.0x baseline)

**H.265 (HEVC) - Current Standard**:
- **Usage**: 720p-4K profiles, modern devices (2016+)
- **Profile**: Main (SDR), Main10 (HDR)
- **Encoder**: x265 (open source) + custom Netflix optimizations
- **Pros**: 30-50% better compression vs H.264
- **Cons**: Higher encoding complexity, licensing costs
- **Adoption**: 70% of Netflix streams (2026)

**AV1 - Future (Rolling Out)**:
- **Usage**: All profiles (gradual rollout)
- **Profile**: Main (8-bit), High (10-bit)
- **Encoder**: SVT-AV1 (Scalable Video Technology), libaom
- **Pros**: 40-50% better compression vs H.265, royalty-free
- **Cons**: Very high encoding complexity (10-20x slower), limited hardware decode
- **Adoption**: 5% of Netflix streams (2026), targeting 50% by 2028

### 3.2 Encoding Parameters (H.265 Example)

**x265 Command Line**:
```bash
#!/bin/bash

# Netflix-optimized H.265 encoding for 1080p profile

x265 \
  --input source_4k.y4m \
  --output encoded_1080p.hevc \
  \
  # Resolution & Frame Rate
  --input-res 1920x1080 \
  --fps 24000/1001 \
  \
  # Rate Control
  --bitrate 5000 \
  --vbv-bufsize 7500 \
  --vbv-maxrate 6000 \
  \
  # Codec Profile
  --profile main \
  --level-idc 4.1 \
  --high-tier \
  \
  # GOP Structure
  --keyint 96 \              # Keyframe every 4 seconds @ 24fps
  --min-keyint 96 \
  --scenecut 0 \             # Disable adaptive keyframes (fixed 4s)
  --no-open-gop \
  \
  # B-frames & Reference Frames
  --bframes 4 \              # 4 B-frames between P-frames
  --b-adapt 2 \              # Adaptive B-frame placement
  --ref 4 \                  # 4 reference frames
  \
  # Motion Estimation
  --me 3 \                   # STAR motion estimation (high quality)
  --subme 5 \                # Subpixel motion estimation
  --merange 57 \             # Motion search range
  \
  # Rate-Distortion Optimization
  --rd 4 \                   # RD level 4 (high quality, slower)
  --psy-rd 2.0 \             # Psychovisual RD optimization
  --rdoq-level 1 \
  --psy-rdoq 1.0 \
  \
  # Deblocking Filter
  --deblock -1:-1 \          # Slightly weaker deblocking
  \
  # SAO (Sample Adaptive Offset)
  --sao \                    # Enable SAO (reduces banding)
  \
  # Performance & Multi-threading
  --pools 16 \               # 16 thread pools
  --frame-threads 4 \        # 4 frame-level threads
  --preset slow \            # Encoding speed preset (slow = better quality)
  \
  # Analysis
  --aq-mode 3 \              # Adaptive quantization mode 3 (edge-based)
  --aq-strength 1.0 \
  --cutree \                 # MB-tree rate control
  \
  # Output
  --output-depth 8 \         # 8-bit output (Main profile)
  --log-level info
```

**Encoding Performance**:
- **Encoding Speed**: 0.5-2x realtime (depends on preset)
  - x265 slow preset: ~0.5-1x realtime on 32-core CPU
  - x265 medium preset: ~1-2x realtime
  - x264 veryslow: ~1-3x realtime
- **Hardware**: 
  - CPU: Dual Intel Xeon Platinum 8375C (32 cores, 64 threads)
  - Memory: 256GB RAM
  - Storage: 2TB NVMe SSD (for temp files)
- **Cost per Hour**:
  - AWS EC2 c6i.16xlarge: $2.72/hour
  - 2-hour movie 1080p encode: 2-4 hours = $5.44-$10.88
  - All 10 video profiles: ~$100 encoding cost per title

### 3.3 HDR Encoding

**HDR10 Encoding**:
```bash
x265 \
  --input source_4k_hdr.y4m \
  --output encoded_4k_hdr10.hevc \
  \
  # HDR Profile
  --profile main10 \          # 10-bit color depth
  --level-idc 5.1 \
  --high-tier \
  \
  # HDR Metadata (Static)
  --hdr10 \
  --master-display "G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,50)" \
  --max-cll "1000,400" \      # Max content light level, Max frame average
  \
  # Color Space
  --colorprim bt2020 \        # BT.2020 color primaries
  --transfer smpte2084 \      # SMPTE ST 2084 (PQ transfer)
  --colormatrix bt2020nc \    # BT.2020 non-constant luminance
  \
  # Other parameters same as SDR...
```

**Dolby Vision Encoding**:
- **Requires**: Dolby Vision encoding license
- **Process**: 
  1. Encode base layer (HDR10 or SDR)
  2. Generate Dolby Vision metadata (RPU - Reference Processing Unit)
  3. Mux RPU with base layer
- **Tool**: Dolby Vision Professional Tools
- **Metadata**: Dynamic metadata per scene (vs static HDR10)
- **Advantage**: Optimizes HDR for each display capability

## 4. Audio Encoding

### 4.1 Audio Codec Selection

**AAC (Advanced Audio Coding)**:
- **Usage**: Stereo profiles (96-192 Kbps)
- **Profile**: AAC-LC (Low Complexity)
- **Encoder**: Fraunhofer FDK-AAC
- **Pros**: Good quality at low bitrates, universal compatibility
- **Cons**: Not ideal for surround sound

**Dolby Digital (AC-3)**:
- **Usage**: 5.1 surround (448 Kbps)
- **Channels**: 5.1 (L, C, R, Ls, Rs, LFE)
- **Encoder**: Dolby Digital encoding tool
- **Pros**: Standard surround format, widely supported
- **Cons**: Moderate compression efficiency

**Dolby Digital Plus (E-AC-3)**:
- **Usage**: 5.1 and Atmos (448-768 Kbps)
- **Channels**: Up to 7.1 + objects (Atmos)
- **Encoder**: Dolby Digital Plus encoding tool
- **Pros**: Better compression than AC-3, Atmos support
- **Cons**: Requires license

### 4.2 Dolby Atmos Encoding

**Dolby Atmos Architecture**:
```
Source: 128 audio stems (objects + beds)
  ├─ Dialogue objects (3-5 channels)
  ├─ Music objects (10-20 channels)
  ├─ Effects objects (50-100 channels)
  └─ Bed channels (7.1.2 or 7.1.4)

Encoding:
  ↓
Dolby Atmos Renderer
  - Render to 7.1.4 layout (7 surround + 4 height)
  - Generate metadata (object positions, movement)
  ↓
Encode to E-AC-3 with JOC (Joint Object Coding)
  - Bitrate: 768 Kbps
  - Backward compatible: Falls back to 7.1 or 5.1
  ↓
Delivery:
  - E-AC-3 JOC stream (768 Kbps)
  - Decoded by Atmos-capable devices
  - Rendered to speaker layout (5.1.2, 7.1.4, 9.1.6, etc.)
```

**Encoding Process**:
1. **Source Audio**: 48 kHz, 24-bit, multi-channel stems
2. **Atmos Authoring**: Position objects in 3D space
3. **Rendering**: Generate 7.1.4 bed + metadata
4. **Encoding**: E-AC-3 JOC encoding
5. **Validation**: QC on reference system (7.1.4 or 5.1.2)

### 4.3 Audio Normalization

**Loudness Normalization (LKFS)**:
```python
class AudioNormalizer:
    TARGET_LKFS = -24.0  # Netflix standard (same as most streaming)
    MAX_TRUE_PEAK = -2.0  # dBTP (to prevent clipping)
    
    def normalize_audio(self, audio_file):
        # Measure integrated loudness (LKFS)
        integrated_lkfs = self.measure_lkfs(audio_file)
        
        # Calculate gain adjustment
        gain_adjustment = self.TARGET_LKFS - integrated_lkfs
        
        # Check if gain would cause clipping
        true_peak = self.measure_true_peak(audio_file)
        adjusted_peak = true_peak + gain_adjustment
        
        if adjusted_peak > self.MAX_TRUE_PEAK:
            # Limit gain to prevent clipping
            gain_adjustment = self.MAX_TRUE_PEAK - true_peak
        
        # Apply gain
        normalized_audio = self.apply_gain(audio_file, gain_adjustment)
        
        # Verify
        final_lkfs = self.measure_lkfs(normalized_audio)
        final_peak = self.measure_true_peak(normalized_audio)
        
        return {
            "normalized_audio": normalized_audio,
            "original_lkfs": integrated_lkfs,
            "final_lkfs": final_lkfs,
            "gain_applied": gain_adjustment,
            "true_peak": final_peak
        }
```

**Why Normalize?**
- **Consistent Volume**: No jarring volume changes between titles
- **Prevent Clipping**: Avoid distortion on playback
- **User Experience**: No need to adjust volume constantly

## 5. Encoding Infrastructure

### 5.1 Compute Architecture

**AWS Compute Options**:

1. **EC2 Instances (On-Demand)**:
   - **Instance Type**: c6i.16xlarge (64 vCPU, 128GB RAM)
   - **Use Case**: Urgent encodes, unpredictable workload spikes
   - **Cost**: $2.72/hour
   - **Quantity**: 100-500 instances (baseline capacity)

2. **EC2 Spot Instances**:
   - **Instance Type**: c6i.16xlarge (same specs)
   - **Use Case**: Bulk encoding (90% of workload)
   - **Cost**: $0.80-$1.20/hour (70% savings vs on-demand)
   - **Quantity**: 2,000-10,000 instances (scales dynamically)
   - **Strategy**: Diversified across multiple instance types and AZs

3. **AWS Batch**:
   - **Orchestration**: Manages spot instance fleet
   - **Job Queue**: Priority-based encoding queue
   - **Auto-scaling**: Scale from 0 to 10,000+ instances
   - **Retry Logic**: Auto-retry on spot interruption

**Encoding Farm Architecture**:
```
┌────────────────────────────────────────────────────────────────┐
│                    Encoding Job Queue (SQS)                     │
│  - 10,000+ jobs in queue (titles × profiles)                   │
│  - Priority: Urgent > Standard > Backfill                      │
│  - Message: {content_id, profile, s3_source, s3_output}        │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    AWS Batch (Job Scheduler)                    │
│  - Monitors queue depth                                        │
│  - Scales compute capacity (0-10,000 instances)                │
│  - Distributes jobs to available instances                     │
└────────────────────┬───────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┬──────────┬──────────┐
          ▼                     ▼          ▼          ▼
    ┌─────────┐           ┌─────────┐  ┌─────────┐  ...
    │ EC2 #1  │           │ EC2 #2  │  │ EC2 #N  │  (10,000+)
    │ Spot    │           │ Spot    │  │ Spot    │
    │ c6i.16xl│           │ c6i.16xl│  │ c6i.16xl│
    └────┬────┘           └────┬────┘  └────┬────┘
         │                     │            │
         ▼                     ▼            ▼
    ┌─────────────────────────────────────────────┐
    │          Encoding Worker Container          │
    │  - Docker image with x265, x264, FFmpeg    │
    │  - Download source from S3                  │
    │  - Encode video                             │
    │  - Upload output to S3                      │
    │  - Report metrics to CloudWatch             │
    └─────────────────────────────────────────────┘
```

### 5.2 Encoding Worker Implementation

**Docker Container**:
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    x264 \
    x265 \
    python3 \
    python3-pip \
    awscli

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy encoding scripts
COPY encode_worker.py /app/
COPY encode_profiles.json /app/

WORKDIR /app

# Start worker
CMD ["python3", "encode_worker.py"]
```

**Worker Script** (Simplified):
```python
import boto3
import subprocess
import json
import time

class EncodingWorker:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.sqs = boto3.client('sqs')
        self.cloudwatch = boto3.client('cloudwatch')
        self.queue_url = os.environ['ENCODING_QUEUE_URL']
    
    def process_jobs(self):
        while True:
            # Poll for jobs
            messages = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20  # Long polling
            )
            
            if 'Messages' not in messages:
                continue
            
            message = messages['Messages'][0]
            job = json.loads(message['Body'])
            
            try:
                # Process encoding job
                self.encode_video(job)
                
                # Delete message from queue (success)
                self.sqs.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
            except Exception as e:
                # Log error, message will return to queue after visibility timeout
                print(f"Encoding failed: {e}")
                self.report_failure(job, str(e))
    
    def encode_video(self, job):
        content_id = job['content_id']
        profile = job['profile']
        s3_source = job['s3_source']
        s3_output = job['s3_output']
        
        # Download source from S3
        local_source = f"/tmp/source_{content_id}.mov"
        self.s3.download_file(
            Bucket=s3_source['bucket'],
            Key=s3_source['key'],
            Filename=local_source
        )
        
        # Encode video
        local_output = f"/tmp/encoded_{content_id}_{profile}.mp4"
        start_time = time.time()
        
        self.run_encoding(local_source, local_output, profile)
        
        encode_time = time.time() - start_time
        
        # Upload output to S3
        self.s3.upload_file(
            Filename=local_output,
            Bucket=s3_output['bucket'],
            Key=s3_output['key']
        )
        
        # Report metrics
        self.report_success(content_id, profile, encode_time)
        
        # Cleanup
        os.remove(local_source)
        os.remove(local_output)
    
    def run_encoding(self, input_file, output_file, profile):
        # Load encoding parameters for profile
        params = self.load_profile_params(profile)
        
        # Build FFmpeg/x265 command
        cmd = [
            'x265',
            '--input', input_file,
            '--output', output_file,
            '--bitrate', str(params['bitrate']),
            '--input-res', params['resolution'],
            '--fps', params['fps'],
            # ... (all other parameters)
        ]
        
        # Execute encoding
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True
        )
        
        return result
```

### 5.3 Encoding Performance & Costs

**Throughput**:
- **Single Instance**: 0.5-2x realtime (depends on profile)
  - 4K HEVC slow: 0.5x realtime (4 hours for 2-hour movie)
  - 1080p HEVC medium: 1x realtime (2 hours)
  - 720p AVC fast: 2x realtime (1 hour)
- **Fleet**: 10,000 instances = 5,000-20,000x realtime
  - Can encode entire 2-hour movie (all profiles) in 10-20 minutes

**Costs (per 2-hour movie)**:
- 10 video profiles × $5-10 each = $50-100 (video)
- 50 audio profiles × $1-2 each = $50-100 (audio)
- **Total encoding cost**: $100-200 per title
- **Monthly encoding**: 1,000 titles × $150 = $150,000

**Cost Optimization**:
- **Spot Instances**: 70% cost savings
- **Preemptible Workers**: Handle spot interruptions gracefully
- **Batch Processing**: Group low-priority jobs during off-peak hours
- **Reserved Instances**: Baseline capacity (20% of fleet)

## 6. Quality Assurance

### 6.1 VMAF (Video Multimethod Assessment Fusion)

**Netflix's Perceptual Quality Metric**:
- **Developed by**: Netflix + USC (University of Southern California)
- **Open Source**: Available on GitHub
- **Range**: 0-100 (100 = perfect quality, indistinguishable from source)
- **Target**: VMAF > 95 for all encodes

**VMAF Calculation**:
```python
import subprocess
import json

def calculate_vmaf(reference_video, distorted_video, model='vmaf_v0.6.1'):
    """
    Calculate VMAF score comparing distorted video to reference
    """
    cmd = [
        'ffmpeg',
        '-i', distorted_video,
        '-i', reference_video,
        '-lavfi', f'[0:v][1:v]libvmaf=model_path=/models/{model}.json:log_path=/tmp/vmaf.json:log_fmt=json',
        '-f', 'null', '-'
    ]
    
    result = subprocess.run(cmd, capture_output=True, check=True)
    
    # Parse VMAF results
    with open('/tmp/vmaf.json', 'r') as f:
        vmaf_data = json.load(f)
    
    # Extract mean VMAF score
    mean_vmaf = vmaf_data['pooled_metrics']['vmaf']['mean']
    min_vmaf = vmaf_data['pooled_metrics']['vmaf']['min']
    
    # Also extract per-frame scores for analysis
    frame_scores = [
        frame['metrics']['vmaf']
        for frame in vmaf_data['frames']
    ]
    
    return {
        'mean_vmaf': mean_vmaf,
        'min_vmaf': min_vmaf,
        'frame_scores': frame_scores,
        'p5_vmaf': np.percentile(frame_scores, 5),  # 5th percentile
        'p95_vmaf': np.percentile(frame_scores, 95)
    }
```

**VMAF Targets by Profile**:
- 4K profiles: VMAF > 98
- 1080p profiles: VMAF > 95
- 720p profiles: VMAF > 93
- 480p profiles: VMAF > 90
- 240p-360p profiles: VMAF > 85

**If VMAF < Target**:
1. Increase bitrate by 10-20%
2. Re-encode
3. Re-measure VMAF
4. Repeat until target achieved

### 6.2 Automated Quality Checks

**QC Pipeline**:
```python
class QualityValidator:
    def validate_encode(self, encoded_file, reference_file, profile):
        issues = []
        
        # 1. VMAF Quality Check
        vmaf = self.calculate_vmaf(reference_file, encoded_file)
        if vmaf['mean_vmaf'] < profile['vmaf_target']:
            issues.append({
                'severity': 'CRITICAL',
                'issue': 'VMAF_TOO_LOW',
                'details': f"VMAF {vmaf['mean_vmaf']} < target {profile['vmaf_target']}"
            })
        
        # 2. A/V Sync Check
        av_offset = self.measure_av_sync(encoded_file)
        if abs(av_offset) > 40:  # >40ms offset
            issues.append({
                'severity': 'CRITICAL',
                'issue': 'AV_SYNC_ERROR',
                'details': f"A/V offset: {av_offset}ms"
            })
        
        # 3. Duration Check
        ref_duration = self.get_duration(reference_file)
        enc_duration = self.get_duration(encoded_file)
        if abs(ref_duration - enc_duration) > 1.0:  # >1 second diff
            issues.append({
                'severity': 'CRITICAL',
                'issue': 'DURATION_MISMATCH',
                'details': f"Ref: {ref_duration}s, Enc: {enc_duration}s"
            })
        
        # 4. Playback Test (automated)
        playback_result = self.test_playback(encoded_file)
        if not playback_result['success']:
            issues.append({
                'severity': 'CRITICAL',
                'issue': 'PLAYBACK_FAILED',
                'details': playback_result['error']
            })
        
        # 5. Black Frame Detection
        black_frames = self.detect_black_frames(encoded_file)
        if len(black_frames) > 0:
            issues.append({
                'severity': 'WARNING',
                'issue': 'BLACK_FRAMES_DETECTED',
                'details': f"{len(black_frames)} black frames at timestamps: {black_frames[:10]}"
            })
        
        return {
            'passed': len([i for i in issues if i['severity'] == 'CRITICAL']) == 0,
            'issues': issues
        }
```

## 7. Future Encoding Technologies

### 7.1 AV1 Rollout Plan

**Phase 1 (2026-2027)**: 
- Encode new popular titles in AV1 (in addition to H.265)
- Target devices with AV1 hardware decode (2021+ chips)
- ~10% of streams

**Phase 2 (2027-2028)**:
- Encode all new titles in AV1
- Re-encode top 1,000 popular titles
- ~30% of streams

**Phase 3 (2028-2030)**:
- Deprecate H.264 for 1080p+ (keep for 480p and below)
- Re-encode entire catalog (phased over 2 years)
- 70%+ of streams

**Benefits**:
- 40-50% bandwidth savings = $500M+ annually
- Better quality at same bitrates
- Royalty-free (no licensing costs)

### 7.2 Machine Learning for Encoding

**Content-Aware Encoding**:
- ML models predict optimal encoding parameters per scene
- Dynamic bitrate allocation (more bits to complex scenes)
- 5-15% additional bitrate savings

**Neural Video Compression** (Research):
- End-to-end learned compression (replace traditional codecs)
- Promising results in research (50-70% better than H.265)
- Not production-ready (decoder complexity, standardization)

### 7.3 Cloud Gaming & Low-Latency Encoding

**Potential Future**: Netflix gaming with cloud streaming
- **Latency Requirement**: <50ms glass-to-glass
- **Encoding**: Real-time (<20ms encoding latency)
- **Technology**: 
  - NVIDIA NVENC (hardware encoder)
  - H.264 Low-Latency preset
  - 60fps, 1080p/1440p
- **Infrastructure**: Edge compute (AWS Local Zones, Wavelength)

