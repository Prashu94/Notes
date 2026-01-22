# Netflix System Design - Interview Questions

## Overview

This document contains comprehensive interview questions based on Netflix's streaming platform architecture. Questions are organized by difficulty level and topic area, covering content ingestion, storage, encoding, streaming, CDN distribution, and DRM security.

---

## Table of Contents

1. [System Architecture & Design](#system-architecture--design)
2. [Content Ingestion Pipeline](#content-ingestion-pipeline)
3. [Storage Architecture](#storage-architecture)
4. [Video Encoding & Transcoding](#video-encoding--transcoding)
5. [Streaming & Playback](#streaming--playback)
6. [CDN & Global Distribution](#cdn--global-distribution)
7. [DRM & Security](#drm--security)
8. [Performance & Scalability](#performance--scalability)
9. [AWS Cloud Infrastructure](#aws-cloud-infrastructure)
10. [Behavioral & Scenario-Based](#behavioral--scenario-based)

---

## System Architecture & Design

### Junior Level (1-3 years)

**Q1: Describe the high-level architecture of Netflix's streaming platform.**
- Expected: Content Sources → Ingestion → Storage → Encoding → CDN → Users
- Follow-up: What happens if the encoding pipeline fails?

**Q2: What is the difference between video streaming and video downloading?**
- Expected: Streaming = progressive playback while downloading, Download = complete file transfer first
- Follow-up: Why does Netflix use streaming instead of downloads for most content?

**Q3: What are the main components needed to deliver video to 200 million subscribers?**
- Expected: Content storage (S3), CDN (CloudFront + Open Connect), encoding pipeline, playback APIs
- Follow-up: Which component handles the most traffic?

**Q4: Explain what a CDN (Content Delivery Network) is.**
- Expected: Distributed network of servers that cache content closer to users for faster delivery
- Follow-up: Why not serve everything from a central data center?

**Q5: What is adaptive bitrate streaming?**
- Expected: Dynamically adjusting video quality based on network conditions
- Follow-up: How does the player know which quality to select?

### Mid Level (3-6 years)

**Q6: Design a content ingestion pipeline for receiving content from 100+ studios.**
- Expected:
  - Upload mechanisms (SFTP, API Gateway, AWS Transfer Family)
  - S3 storage with multi-region replication
  - Validation pipeline (Lambda, Step Functions)
  - Metadata extraction and storage (DynamoDB, RDS)
  - Quality control checks (Rekognition, custom ML)
- Follow-up: How do you handle a 2TB video file upload?

**Q7: Explain the CAP theorem and how it applies to Netflix's architecture.**
- Expected:
  - Content Catalog: CP (Consistency over Availability) - users must see correct content
  - User Preferences: AP (Availability over Consistency) - stale watchlist acceptable
  - Playback Metrics: AP - eventual consistency for analytics
- Follow-up: What happens during a network partition?

**Q8: How would you design the storage tier strategy for 175PB of content?**
- Expected:
  - Hot tier (S3 Standard): Active streaming content, $0.023/GB/month
  - Warm tier (S3 Intelligent-Tiering): Recent additions, auto-transition
  - Cold tier (Glacier): Removed titles, $0.0036/GB/month
  - Archive tier (Glacier Deep Archive): Masters, $0.00099/GB/month
  - Cost optimization through lifecycle policies
- Follow-up: How do you decide when to move content between tiers?

**Q9: Design an API for playback session management.**
- Expected:
  - Authentication/authorization (OAuth 2.0)
  - Session creation (POST /api/playback/session)
  - Manifest retrieval (GET /api/playback/manifest)
  - DRM license acquisition
  - Progress tracking
  - Bitrate adaptation reporting
- Follow-up: How many API calls per second during peak hours?

**Q10: How do you implement exactly-once processing for encoding jobs?**
- Expected:
  - Idempotent job IDs
  - AWS Batch with job deduplication
  - DynamoDB for job state tracking
  - S3 atomic writes for encoded outputs
  - Retry logic with exponential backoff
- Follow-up: What if an encoding job gets stuck?

### Senior Level (6+ years)

**Q11: You need to reduce streaming startup time from 3 seconds to <1 second globally. Design your strategy.**
- Expected:
  - Pre-load manifest files at CDN edge
  - Reduce initialization segment size
  - Predictive pre-fetching based on user behavior
  - HTTP/3 with QUIC for faster connection
  - Optimize DRM license acquisition (parallel with manifest)
  - Edge computing for personalized manifests
  - CDN placement optimization (more OCAs in ISPs)
- Follow-up: What's the latency budget breakdown?

**Q12: Design a disaster recovery strategy for Netflix with 99.99% availability.**
- Expected:
  - Multi-region active-active for APIs (Route 53)
  - S3 cross-region replication for content
  - Stateless microservices (ECS/EKS)
  - Database replication (Aurora Global Database)
  - CDN redundancy (CloudFront + OCA)
  - Automated failover with health checks
  - Chaos engineering for validation
- Follow-up: What's your RTO and RPO?

**Q13: Netflix streams 1 billion hours per day. How do you architect this scale?**
- Expected:
  - 10,000+ Open Connect Appliances (95% of traffic)
  - Each OCA: 8,000-15,000 concurrent streams, 40-80 Gbps
  - CloudFront for cache misses (200+ edge locations)
  - S3 multi-region for origin (<1% of traffic)
  - Predictive content pre-positioning
  - Load balancing across OCAs
  - Auto-scaling microservices
- Follow-up: How do you handle traffic spikes for new releases?

**Q14: Design a recommendation system that can influence content pre-positioning on CDN.**
- Expected:
  - ML model predicting regional content popularity
  - Features: viewing history, genre trends, cast popularity, marketing spend
  - Real-time stream processing (Kinesis, Spark)
  - Content popularity scores per OCA location
  - Automated overnight fills based on predictions
  - A/B testing for recommendation accuracy
  - Feedback loop for model improvement
- Follow-up: How do you measure recommendation quality?

**Q15: Your encoding costs are $50M/year. How do you reduce by 30% without quality loss?**
- Expected:
  - Per-title encoding (20-30% bitrate savings already)
  - AV1 codec adoption (30% more efficient than H.265)
  - Spot instances for encoding (70% cost reduction)
  - Encoding farm optimization (GPU vs CPU)
  - Content complexity analysis (reduce profiles for simple content)
  - Reuse encoding for similar content
  - Encoding parallelization improvements
- Follow-up: What's the trade-off between cost and time-to-publish?

---

## Content Ingestion Pipeline

### Junior Level

**Q16: What formats do studios typically deliver content in?**
- Expected: ProRes 4444, DNxHR 444, 4K resolution, 800GB-2TB per 2-hour movie
- Follow-up: Why such large file sizes?

**Q17: What is the difference between raw source and mezzanine format?**
- Expected: Raw = original from studio, Mezzanine = validated intermediate format for encoding
- Follow-up: Why keep both?

**Q18: What validations would you perform on uploaded content?**
- Expected: File integrity (MD5), codec validation, resolution check, audio sync, frame rate
- Follow-up: What happens if validation fails?

### Mid Level

**Q19: Implement a multipart upload strategy for a 2TB video file.**
- Expected:
```python
import boto3

class LargeFileUploader:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.chunk_size = 500 * 1024 * 1024  # 500MB chunks
    
    def upload_large_file(self, file_path, bucket, key):
        # Initiate multipart upload
        response = self.s3.create_multipart_upload(
            Bucket=bucket, Key=key)
        upload_id = response['UploadId']
        
        parts = []
        part_number = 1
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                
                # Upload part (with retry)
                part = self.s3.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk
                )
                
                parts.append({
                    'PartNumber': part_number,
                    'ETag': part['ETag']
                })
                part_number += 1
        
        # Complete upload
        self.s3.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
```
- Follow-up: How do you handle network failures mid-upload?

**Q20: Design a metadata extraction pipeline for video content.**
- Expected:
  - Lambda triggered on S3 upload
  - MediaInfo/FFprobe for technical metadata
  - AWS Rekognition for scene detection
  - Custom ML for content analysis
  - Store in DynamoDB/RDS
  - Generate thumbnails every 10 seconds
- Follow-up: How long should this process take?

**Q21: How would you implement quality control automation?**
- Expected:
  - Frame-by-frame analysis for artifacts
  - Audio level normalization check (LKFS)
  - A/V sync validation (<40ms tolerance)
  - Color grading verification
  - Resolution and aspect ratio checks
  - Automated vs manual QC thresholds
- Follow-up: What percentage should go through manual QC?

**Q22: Design a notification system for content ingestion status.**
- Expected:
  - SNS topics for different events
  - SQS for reliable delivery
  - EventBridge for complex routing
  - Email/Slack notifications
  - Studio-facing dashboard
  - Status API for polling
- Follow-up: How do you handle notification failures?

### Senior Level

**Q23: You're ingesting 1,000 hours of new content per day. How do you scale the pipeline?**
- Expected:
  - Parallel processing with AWS Batch
  - Multiple S3 upload endpoints
  - Regional ingestion points (closer to studios)
  - Auto-scaling Lambda for validation
  - Priority queue (originals vs licensed)
  - Spot instances for cost optimization
  - Processing time SLA: <24 hours
- Follow-up: What's the bottleneck and how do you identify it?

**Q24: Implement a content versioning and rollback system.**
- Expected:
  - S3 versioning enabled
  - Content version metadata in database
  - Encoding job tied to specific version
  - Rollback mechanism for bad encodes
  - Audit trail of changes
  - Automated testing for new versions
- Follow-up: How do you handle rollback for live content?

**Q25: Design a multi-region ingestion strategy with 99.9% reliability.**
- Expected:
  - Primary region: us-east-1
  - Secondary: us-west-2, eu-west-1
  - Cross-region replication (CRR)
  - Regional processing pipelines
  - Failover logic based on health checks
  - Consistency checks across regions
- Follow-up: What's the cost of multi-region redundancy?

---

## Storage Architecture

### Junior Level

**Q26: Why does Netflix use multiple storage tiers?**
- Expected: Cost optimization - frequently accessed content in fast/expensive tier, archives in slow/cheap tier
- Follow-up: What percentage of content is in each tier?

**Q27: What is the difference between S3 Standard and S3 Glacier?**
- Expected: 
  - S3 Standard: Instant access, $0.023/GB/month
  - Glacier: 1-5 minute retrieval, $0.0036/GB/month
- Follow-up: When would you use Glacier Deep Archive?

**Q28: How much storage does a 2-hour movie require after encoding?**
- Expected: 
  - Raw source: 800GB-2TB
  - Mezzanine: 50GB-120GB
  - Encoded variants: 80GB-150GB (30-40 profiles)
- Follow-up: How do you calculate total storage needs?

### Mid Level

**Q29: Design a storage lifecycle policy for Netflix content.**
- Expected:
```yaml
Lifecycle_Policy:
  Rules:
    - Id: "Raw_Source_Archive"
      Status: "Enabled"
      Transitions:
        - Days: 90
          StorageClass: "GLACIER"
        - Days: 365
          StorageClass: "DEEP_ARCHIVE"
    
    - Id: "Mezzanine_Transition"
      Status: "Enabled"
      Transitions:
        - Days: 180
          StorageClass: "INTELLIGENT_TIERING"
    
    - Id: "Encoded_Assets_Hot"
      Status: "Enabled"
      # Keep in S3 Standard indefinitely
```
- Follow-up: How do you restore archived content?

**Q30: Implement a cross-region replication strategy.**
- Expected:
  - Primary: us-east-1
  - Replicas: us-west-2, eu-west-1, ap-southeast-1
  - S3 CRR with replication time control (RTC)
  - Encryption during transfer
  - Replication metrics and monitoring
  - Cost: ~$10M/year for 175PB
- Follow-up: What's the replication lag?

**Q31: How would you organize 30-40 encoding profiles for a single title?**
- Expected:
```
s3://netflix-content/{content_id}/
  video/
    4k_hdr_25mbps/
    4k_sdr_20mbps/
    1080p_high_8mbps/
    1080p_medium_5mbps/
    720p_high_3mbps/
    ...
  audio/
    eng_atmos_768k/
    eng_51_448k/
    spa_51_448k/
    ...
  subtitles/
  manifests/
```
- Follow-up: How do you version these assets?

**Q32: Design a storage cost optimization strategy.**
- Expected:
  - Intelligent-Tiering for uncertain access patterns
  - Lifecycle policies for automatic transitions
  - Compression for metadata (10:1 ratio)
  - Deduplication for identical segments
  - Delete temporary encoding artifacts
  - Reserved capacity for predictable usage
- Follow-up: What's the monthly storage cost for 175PB?

### Senior Level

**Q33: Your S3 costs are $4M/month. Reduce by 40% without impacting performance.**
- Expected:
  - Analyze access patterns (80/20 rule)
  - Move infrequently accessed to Glacier (85% savings)
  - Intelligent-Tiering for variable access
  - Compression (reduce size by 20-30%)
  - Delete redundant copies
  - Cross-region replication optimization
  - Target: $2.4M/month
- Follow-up: What's the risk of aggressive archiving?

**Q34: Design a storage architecture for interactive content (Bandersnatch-style).**
- Expected:
  - Branching narrative structure
  - Pre-encode all possible paths
  - Decision point metadata
  - Seamless switching between branches
  - Predictive pre-fetching of likely paths
  - Storage: 3-5x normal content
  - CDN caching strategy for branches
- Follow-up: How do you test all possible paths?

**Q35: Implement a disaster recovery strategy for 175PB of content.**
- Expected:
  - Multi-region replication (3+ regions)
  - Automated failover with Route 53
  - Recovery time: <1 hour for critical content
  - Backup verification (monthly sampling)
  - Restoration testing (quarterly)
  - Cost: $10-15M/year
  - Insurance for catastrophic loss
- Follow-up: What if an entire AWS region goes down?

---

## Video Encoding & Transcoding

### Junior Level

**Q36: What is the purpose of video encoding/transcoding?**
- Expected: Convert raw video to compressed formats suitable for streaming at various quality levels
- Follow-up: Why multiple quality levels?

**Q37: What is the difference between H.264 and H.265 codecs?**
- Expected: H.265 (HEVC) is 40-50% more efficient than H.264, same quality at lower bitrate
- Follow-up: Why still use H.264?

**Q38: What is VMAF and why does Netflix use it?**
- Expected: Video Multimethod Assessment Fusion - predicts perceived video quality, Netflix targets >95 score
- Follow-up: How is it different from PSNR?

### Mid Level

**Q39: Explain Netflix's Per-Title Encoding innovation.**
- Expected:
  - Analyze content complexity per title
  - Simple animation (BoJack Horseman): lower bitrates sufficient
  - Complex action (Extraction): higher bitrates needed
  - Custom bitrate ladder per title
  - 20-30% bandwidth savings
  - Maintains quality (VMAF >95)
- Follow-up: How do you determine content complexity?

**Q40: Design an encoding pipeline for a 2-hour 4K HDR movie.**
- Expected:
```
Pre-Processing:
  - Shot detection and scene analysis
  - Content complexity scoring
  - Audio loudness normalization

Parallel Encoding Jobs (AWS Batch):
  Video: 30-40 profiles
    - 4K HDR (25 Mbps, H.265 Main10)
    - 4K SDR (20 Mbps, H.265)
    - 1080p High (8 Mbps), Medium (5 Mbps)
    - 720p, 480p, 360p, 240p
  
  Audio: 40-50 tracks
    - Multiple languages
    - Dolby Atmos, 5.1, Stereo
    - Multiple bitrates

Post-Processing:
  - Segmentation (4-second chunks)
  - DRM encryption
  - VMAF scoring
  - Manifest generation

Total: 1200+ encoding jobs
Time: 4-8 hours
Cost: $100-200 per title
```
- Follow-up: How do you prioritize jobs for new releases?

**Q41: Implement VMAF quality scoring in the encoding pipeline.**
- Expected:
```python
import subprocess
import json

class VMafScorer:
    def calculate_vmaf(self, reference_video, encoded_video):
        """Calculate VMAF score comparing encoded vs reference"""
        cmd = [
            'ffmpeg',
            '-i', encoded_video,
            '-i', reference_video,
            '-lavfi',
            '[0:v]scale=1920:1080:flags=bicubic[main];'
            '[1:v]scale=1920:1080:flags=bicubic[ref];'
            '[main][ref]libvmaf=model_path=/usr/share/model/vmaf_v0.6.1.json:'
            'log_path=vmaf_output.json:log_fmt=json',
            '-f', 'null', '-'
        ]
        
        subprocess.run(cmd, check=True)
        
        with open('vmaf_output.json', 'r') as f:
            results = json.load(f)
            vmaf_score = results['pooled_metrics']['vmaf']['mean']
        
        return vmaf_score
    
    def meets_quality_threshold(self, score):
        return score >= 95.0  # Netflix quality threshold
```
- Follow-up: What do you do if VMAF score is <95?

**Q42: How would you implement encoding job retry logic?**
- Expected:
  - Exponential backoff (1min, 2min, 4min, 8min)
  - Max retries: 3
  - Different error types: transient vs permanent
  - Dead letter queue for failed jobs
  - Alert on repeated failures
  - Alternative instance types for retries
- Follow-up: How do you detect stuck jobs?

### Senior Level

**Q43: You need to re-encode 15,000 titles with AV1 codec. Design the migration strategy.**
- Expected:
  - Prioritize popular content first (80/20 rule)
  - Gradual rollout: 100 titles/day
  - A/B testing for quality/performance
  - Dual encode (AV1 + H.265) during transition
  - Client capability detection
  - 6-month timeline, $15M cost
  - Keep H.265 as fallback for 1 year
- Follow-up: How do you measure AV1 adoption?

**Q44: Design a real-time encoding system for live events.**
- Expected:
  - Low-latency encoding (<3 second delay)
  - AWS Elemental MediaLive for broadcast
  - Chunked transfer encoding (HLS)
  - 2-second segment duration
  - Parallel encoding for ABR profiles
  - Just-in-time packaging
  - Fallback to recorded stream
- Follow-up: What's the trade-off between latency and quality?

**Q45: Optimize encoding farm to reduce costs from $50M/year to $35M/year.**
- Expected:
  - 100% spot instances (70% savings)
  - Spot fleet with fallback to on-demand
  - Regional pricing optimization
  - GPU encoding for H.265/AV1 (2x faster)
  - Encoding job batching
  - Off-peak scheduling for non-urgent content
  - Target: $35M/year
- Follow-up: What's the risk of spot instance interruptions?

---

## Streaming & Playback

### Junior Level

**Q46: What is MPEG-DASH?**
- Expected: Dynamic Adaptive Streaming over HTTP - protocol for adaptive bitrate streaming
- Follow-up: What's the alternative to DASH?

**Q47: Explain how adaptive bitrate (ABR) streaming works.**
- Expected: Player monitors bandwidth, selects appropriate quality profile, switches dynamically
- Follow-up: How often does quality change?

**Q48: What is a manifest file in streaming?**
- Expected: XML/JSON file listing all available quality profiles and segment URLs
- Follow-up: When is the manifest downloaded?

### Mid Level

**Q49: Design the playback session flow from "Play" button to video playback.**
- Expected:
```
1. User clicks "Play"
2. Client authenticates (JWT token)
3. Request manifest (GET /playback/{title_id}/manifest)
4. Download manifest (MPD/M3U8)
5. DRM license acquisition (parallel)
6. Download initialization segment
7. Buffer first 3 segments (12 seconds)
8. Start playback
9. Adaptive streaming loop:
   - Measure bandwidth
   - Select next quality
   - Download next segment
   - Update buffer
```
- Follow-up: What's the target startup time?

**Q50: Implement an ABR algorithm for quality selection.**
- Expected:
```javascript
class ABRAlgorithm {
  selectQuality(bandwidth, buffer, profiles) {
    // Conservative approach
    const safetyFactor = 0.9; // Use 90% of available bandwidth
    const safeBandwidth = bandwidth * safetyFactor;
    
    // Filter profiles by bandwidth
    const suitable = profiles.filter(p => p.bitrate <= safeBandwidth);
    
    // Buffer-based adjustment
    if (buffer < 10) {
      // Low buffer: choose lower quality for faster download
      return suitable[Math.floor(suitable.length / 2)];
    } else if (buffer > 30) {
      // High buffer: can try higher quality
      return suitable[suitable.length - 1];
    } else {
      // Moderate buffer: safe choice
      return suitable[Math.floor(suitable.length * 0.75)];
    }
  }
  
  measureBandwidth(downloadTime, segmentSize) {
    return (segmentSize * 8) / downloadTime; // bits per second
  }
}
```
- Follow-up: How do you handle bandwidth spikes/drops?

**Q51: How would you implement "Continue Watching" with resume from last position?**
- Expected:
  - Periodic progress updates (every 30 seconds)
  - POST /api/playback/progress
  - Store in DynamoDB (user_id, title_id, position, timestamp)
  - Resume request retrieves last position
  - Account for buffered content
  - 98% position = mark as completed
- Follow-up: What if user watches on multiple devices?

**Q52: Design error handling for streaming failures.**
- Expected:
  - Network errors: retry with exponential backoff
  - DRM errors: re-request license
  - Corrupt segment: skip and request next
  - CDN failures: fallback to alternate CDN
  - Persistent errors: display user-friendly message
  - Telemetry for debugging
- Follow-up: How many retries before giving up?

### Senior Level

**Q53: You're seeing 5% of users with >10 second startup time. How do you debug and fix?**
- Expected:
  - Analyze telemetry by region, ISP, device
  - Identify bottlenecks: DNS, manifest, DRM, segments
  - Solutions:
    - Pre-fetch manifests on app open
    - DRM license caching
    - Smaller initialization segments
    - HTTP/3 for faster connection
    - CDN placement optimization
  - A/B test improvements
  - Target: <2 seconds for 95% of users
- Follow-up: Show me the telemetry data structure.

**Q54: Design a streaming architecture for interactive content (Bandersnatch).**
- Expected:
  - Decision points metadata in manifest
  - Pre-buffer both paths before decision
  - Seamless switching at decision point
  - Branch tracking for analytics
  - Predictive pre-fetching based on popularity
  - State management across branches
  - Unique manifest per user session
- Follow-up: How do you handle 5 decision points with 2 options each?

**Q55: Implement a player that optimizes for low-bandwidth users (<1 Mbps).**
- Expected:
  - Aggressive quality downgrade (240p-360p)
  - Larger buffer (60 seconds)
  - Longer segments (10 seconds vs 4)
  - Disable auto-play next episode
  - Smart download in background
  - Offline download recommendation
  - Data usage warnings
- Follow-up: What's the minimum bitrate Netflix supports?

---

## CDN & Global Distribution

### Junior Level

**Q56: What is Netflix Open Connect?**
- Expected: Netflix's proprietary CDN with 10,000+ servers placed in ISP networks worldwide
- Follow-up: Why not just use CloudFront?

**Q57: What is the difference between edge location and origin server?**
- Expected: Edge = cache near users (low latency), Origin = source of truth (S3)
- Follow-up: What happens on cache miss?

**Q58: Why does Netflix place servers inside ISP networks?**
- Expected: Reduce latency (<5ms), save transit costs, improve reliability
- Follow-up: How does Netflix convince ISPs to host servers?

### Mid Level

**Q59: Explain Netflix's multi-tier CDN architecture.**
- Expected:
```
Tier 1: Open Connect (95% traffic)
  - 10,000+ OCA servers in ISPs/IXPs
  - <5ms latency to users
  - Zero transit cost
  
Tier 2: CloudFront (4% traffic)
  - 200+ edge locations
  - Cache misses from OCA
  - New content distribution
  
Tier 3: S3 Origin (1% traffic)
  - Source of truth
  - Only for cache misses
```
- Follow-up: Why not 100% on Tier 1?

**Q60: Design the content pre-positioning strategy for OCAs.**
- Expected:
  - ML model predicting regional popularity
  - Features: viewing history, genre, cast, marketing
  - Overnight fills during low traffic hours
  - 780TB capacity per OCA
  - 15,000-30,000 titles cached
  - Update cycle: daily
  - Prediction accuracy: 85%
- Follow-up: What if prediction is wrong?

**Q61: Calculate the capacity needed for an OCA serving 50,000 subscribers.**
- Expected:
  - Peak usage: 30% concurrent (15,000 users)
  - Average bitrate: 5 Mbps
  - Total: 15,000 × 5 Mbps = 75 Gbps
  - Hardware: 2× OCA (40-80 Gbps each)
  - Redundancy: N+1 for failover
- Follow-up: What happens during new season release spike?

**Q62: Implement cache eviction policy for OCA with 780TB storage.**
- Expected:
  - LRU (Least Recently Used) with popularity weight
  - 60TB SSD for top 20% content (hot)
  - 720TB HDD for next 60% (warm)
  - Evict bottom 20% (cold)
  - Keep Netflix Originals permanently
  - Regional popularity adjustments
- Follow-up: How do you handle seasonal content?

### Senior Level

**Q63: You're launching Netflix in a new country with limited infrastructure. Design the CDN strategy.**
- Expected:
  - Phase 1: CloudFront only (month 1-3)
  - Phase 2: Partner with major ISP, deploy 10-20 OCAs
  - Phase 3: IXP deployments (month 6)
  - Phase 4: Full OCA rollout (12-18 months)
  - Bandwidth estimates and capacity planning
  - Regional content preferences
  - Local CDN partnerships
- Follow-up: What's the cost for first year?

**Q64: Your CDN is serving 270 petabytes/month. How do you reduce bandwidth costs by $100M/year?**
- Expected:
  - Current: ~$25M/month CloudFront
  - Increase OCA coverage (95% → 98%)
  - Better pre-positioning (reduce cache misses)
  - Compression improvements
  - Peer-assisted delivery (P2P)
  - Negotiate better ISP terms
  - Target: ~$16M/month
- Follow-up: What's the ROI on additional OCAs?

**Q65: Design a monitoring system for 10,000 OCAs worldwide.**
- Expected:
  - Metrics: throughput, cache hit rate, disk health, temperature
  - Collection: Agents on each OCA → Kinesis → S3/Redshift
  - Alerting: CloudWatch, PagerDuty
  - Dashboards: Grafana per region
  - Anomaly detection: ML for unusual patterns
  - Auto-remediation: restart services, reroute traffic
  - SLA: 99.9% uptime per OCA
- Follow-up: How do you detect a failing disk before it fails?

---

## DRM & Security

### Junior Level

**Q66: What is DRM and why does Netflix need it?**
- Expected: Digital Rights Management - prevents unauthorized copying/distribution, required by studios
- Follow-up: What happens without DRM?

**Q67: What are the three main DRM systems Netflix uses?**
- Expected: Widevine (Google, 60%), FairPlay (Apple, 30%), PlayReady (Microsoft, 10%)
- Follow-up: Why multiple DRM systems?

**Q68: What is HDCP?**
- Expected: High-bandwidth Digital Content Protection - prevents HDMI capture, required for HD/4K
- Follow-up: What HDCP version for 4K?

### Mid Level

**Q69: Explain the DRM license acquisition flow.**
- Expected:
```
1. Player parses PSSH (Protection System Specific Header)
2. Generates license challenge with device info
3. Sends to license server (HTTPS POST)
4. Server validates:
   - User authentication
   - Subscription status
   - Device certification
   - Geographic rights
5. Server returns encrypted content keys
6. Player decrypts keys in TEE
7. Secure playback pipeline
```
- Follow-up: What if license request fails?

**Q70: Implement content key encryption for DRM.**
- Expected:
```python
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_content_segment(segment_data, content_id, segment_index):
    # Generate content key (CEK)
    content_key = os.urandom(16)  # 128-bit AES key
    
    # Generate unique IV per segment
    iv = generate_iv(content_id, segment_index)
    
    # Encrypt with AES-128-CTR
    cipher = Cipher(algorithms.AES(content_key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(segment_data) + encryptor.finalize()
    
    # Store encrypted content key in KMS
    encrypted_cek = kms.encrypt(content_key)
    
    return {
        'encrypted_segment': encrypted,
        'key_id': generate_key_id(content_id),
        'iv': iv
    }
```
- Follow-up: How do you rotate content keys?

**Q71: Design an account security system to prevent password sharing.**
- Expected:
  - Device fingerprinting
  - Concurrent stream limits (2-4 based on plan)
  - Geographic anomaly detection
  - Login pattern analysis
  - Suspicious activity alerts
  - Gradual enforcement (warnings first)
  - Account verification challenges
- Follow-up: How do you balance security vs user experience?

**Q72: How would you implement forensic watermarking?**
- Expected:
  - Unique watermark per viewing session
  - Imperceptible to users
  - NexGuard technology
  - Embed session ID + timestamp
  - Survives screen recording
  - Extraction from pirated copies
  - Legal evidence for prosecution
- Follow-up: What's the performance impact?

### Senior Level

**Q73: You discover a device is being used to strip DRM from content. Design your response.**
- Expected:
  - Immediate: Revoke device certificate
  - Identify affected users (ban accounts)
  - Security patch deployment
  - Forensic watermark analysis
  - Legal action against exploiter
  - Industry notification (MPAA)
  - Hardened DRM in next update
  - Monitor for exploit spread
- Follow-up: How do you prevent false positives?

**Q74: Design a zero-trust security architecture for Netflix microservices.**
- Expected:
  - Mutual TLS between all services
  - Service-to-service authentication
  - No implicit trust based on network
  - JWT tokens with short expiry
  - Encryption at rest and in transit
  - Least privilege access (IAM roles)
  - Security monitoring and audit logs
  - Regular penetration testing
- Follow-up: What's the performance overhead of mTLS?

**Q75: Your DRM infrastructure costs $125M/year. How do you justify this to executives?**
- Expected:
  - Protected revenue: $12-15 billion/year (studio contracts)
  - Piracy prevention: $2-3 billion/year saved
  - Studio relationship maintenance (mandatory requirement)
  - Risk mitigation: one breach could cost $1 billion+
  - Competitive advantage: best security in industry
  - ROI: 100x+ return
  - No viable cheaper alternative
- Follow-up: What if studios accept weaker DRM?

---

## Performance & Scalability

### Junior Level

**Q76: What is the difference between latency and throughput?**
- Expected: Latency = time to first byte, Throughput = bytes per second
- Follow-up: Which matters more for streaming startup time?

**Q77: What is caching and why does Netflix use it extensively?**
- Expected: Store frequently accessed data closer to users, reduce origin load, faster delivery
- Follow-up: What's Netflix's cache hit rate?

**Q78: How many concurrent streams can Netflix handle?**
- Expected: Tens of millions globally, limited by CDN capacity not origin
- Follow-up: What happens during peak hours?

### Mid Level

**Q79: Design a caching strategy for video segments.**
- Expected:
  - L1: OCA flash storage (60TB, top 20% content)
  - L2: OCA HDD storage (720TB, next 60%)
  - L3: CloudFront (200+ locations)
  - L4: S3 origin
  - TTL: 30 days for active content
  - Cache-Control headers
  - Conditional requests (ETag)
- Follow-up: How do you invalidate cache for content updates?

**Q80: Calculate the bandwidth needed for 1 billion viewing hours per day.**
- Expected:
  - 1 billion hours/day = 41.67 million hours/hour
  - Average bitrate: 5 Mbps
  - Bandwidth: 41.67M × 5 Mbps = 208 Tbps sustained
  - Peak (8-11 PM): 2x average = 416 Tbps
  - Actual: 270 PB/month = ~830 Tbps peak
- Follow-up: How is this distributed across CDN tiers?

**Q81: Implement rate limiting for API requests.**
- Expected:
```python
from redis import Redis
from time import time

class RateLimiter:
    def __init__(self):
        self.redis = Redis()
        self.limits = {
            'playback': 100,      # requests per minute
            'catalog': 1000,
            'profile': 50
        }
    
    def check_rate_limit(self, user_id, endpoint):
        key = f"ratelimit:{user_id}:{endpoint}"
        limit = self.limits[endpoint]
        window = 60  # seconds
        
        current_time = int(time())
        window_start = current_time - window
        
        # Remove old requests
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        request_count = self.redis.zcard(key)
        
        if request_count >= limit:
            return False, limit - request_count
        
        # Add new request
        self.redis.zadd(key, {current_time: current_time})
        self.redis.expire(key, window)
        
        return True, limit - request_count - 1
```
- Follow-up: What's the appropriate limit for playback API?

**Q82: How would you implement auto-scaling for encoding services?**
- Expected:
  - Metrics: job queue depth, processing time
  - Scale up: queue depth > 1000 jobs
  - Scale down: queue depth < 100 jobs
  - Min instances: 100 (baseline)
  - Max instances: 10,000 (spot instances)
  - Cool-down period: 5 minutes
  - Target: <6 hour encoding time
- Follow-up: How do you handle spot instance interruptions?

### Senior Level

**Q83: Design a global load balancing strategy for 200 million users.**
- Expected:
  - Route 53 with latency-based routing
  - Geographic DNS routing by region
  - Health checks on all endpoints
  - Weighted routing for gradual rollouts
  - Failover to backup regions
  - CDN-level load balancing (OCA selection)
  - Connection pooling and reuse
  - HTTP/2 and HTTP/3 optimization
- Follow-up: How do you handle a region failure?

**Q84: You're seeing p99 API latency at 500ms (target: 100ms). How do you debug and fix?**
- Expected:
  - Distributed tracing (X-Ray, Jaeger)
  - Identify slowest service in chain
  - Database query optimization
  - Add caching layers
  - Connection pool tuning
  - Async processing for non-critical paths
  - CDN for static responses
  - Code profiling and optimization
- Follow-up: Show me the tracing data.

**Q85: Design a chaos engineering strategy for Netflix.**
- Expected:
  - Chaos Monkey: random instance termination
  - Chaos Kong: region failure simulation
  - Latency Monkey: inject network delays
  - Failure injection: DRM, CDN, encoding
  - Gradual rollout: dev → staging → production
  - Game days: scheduled exercises
  - Metrics: MTTR, blast radius, customer impact
  - Culture: embrace failure, learn, improve
- Follow-up: How do you ensure chaos doesn't affect real users?

---

## AWS Cloud Infrastructure

### Junior Level

**Q86: What AWS services does Netflix use for storage?**
- Expected: S3 (primary), S3 Glacier (archival), EBS (instance storage), EFS (shared storage)
- Follow-up: Why S3 over EBS for content?

**Q87: What is AWS Lambda and how does Netflix use it?**
- Expected: Serverless compute, Netflix uses for ingestion validation, metadata extraction, notifications
- Follow-up: What are the limitations of Lambda?

**Q88: What is the purpose of AWS CloudFront?**
- Expected: CDN for content delivery, caching at edge locations, reduce latency
- Follow-up: How is it different from Open Connect?

### Mid Level

**Q89: Design a multi-region deployment strategy on AWS.**
- Expected:
  - Primary: us-east-1 (N. Virginia)
  - Secondary: us-west-2, eu-west-1, ap-southeast-1
  - Services: ECS/EKS for microservices
  - Database: Aurora Global Database
  - Storage: S3 with cross-region replication
  - CDN: CloudFront + Route 53
  - Failover: Automated with health checks
- Follow-up: What's the monthly cost?

**Q90: Implement an AWS Batch encoding pipeline.**
- Expected:
```yaml
Batch_Job_Definition:
  jobDefinitionName: "netflix-encoding-job"
  type: "container"
  containerProperties:
    image: "netflix/encoder:latest"
    vcpus: 16
    memory: 32768
    command: ["encode.sh", "Ref::input_file", "Ref::output_bucket"]
    jobRoleArn: "arn:aws:iam::123456:role/batch-job-role"
  
Batch_Compute_Environment:
  type: "EC2"
  instanceTypes: ["c5.4xlarge", "c5.9xlarge"]
  minvCpus: 0
  maxvCpus: 10000
  spotIamFleetRole: "arn:aws:iam::123456:role/spot-fleet"
  bidPercentage: 70  # Use spot instances
```
- Follow-up: How many concurrent jobs can you run?

**Q91: Design a disaster recovery strategy using AWS.**
- Expected:
  - RTO: 1 hour, RPO: 15 minutes
  - Backup: Continuous S3 replication
  - Database: Aurora snapshots every 15 minutes
  - Compute: Warm standby in secondary region
  - DNS: Route 53 automatic failover
  - Testing: Monthly DR drills
  - Cost: $5M/year (10% of infrastructure)
- Follow-up: How do you test DR without impacting production?

**Q92: How would you optimize AWS costs for Netflix's workload?**
- Expected:
  - Spot instances for encoding (70% savings)
  - Reserved instances for baseline (40% savings)
  - S3 Intelligent-Tiering (auto cost optimization)
  - CloudFront reserved capacity
  - Right-sizing EC2 instances
  - Lifecycle policies for storage
  - Lambda for serverless (pay per use)
  - Target: 30% cost reduction
- Follow-up: What's the risk of spot instance interruption?

### Senior Level

**Q93: Netflix's AWS bill is $200M/year. Reduce by $50M without impacting performance.**
- Expected:
  - Spot instances: $30M savings (encoding, batch)
  - Reserved instances: $15M savings (baseline compute)
  - S3 optimization: $10M savings (lifecycle, compression)
  - Right-sizing: $5M savings (underutilized instances)
  - CloudFront optimization: $5M savings (better caching)
  - Reserved capacity: $5M savings (long-term commitments)
  - Total: $70M savings (35% reduction)
- Follow-up: Show me the cost breakdown by service.

**Q94: Design a multi-cloud strategy (AWS + GCP/Azure).**
- Expected:
  - Primary: AWS (90% of workload)
  - Secondary: GCP or Azure (10% for redundancy)
  - Use cases for secondary:
    - Disaster recovery
    - Price comparison leverage
    - Specific services (GCP ML, Azure Media Services)
  - Challenges: Cross-cloud networking, data transfer costs
  - Terraform for infrastructure as code
  - Kubernetes for portability
- Follow-up: Is multi-cloud worth the complexity?

**Q95: Implement a cost allocation and chargeback system for AWS resources.**
- Expected:
  - Tagging strategy: team, service, environment, cost-center
  - AWS Cost Explorer API
  - Daily cost reports per tag
  - Showback/chargeback to teams
  - Budget alerts and quotas
  - Reserved instance recommendations
  - Cost optimization dashboard
  - Monthly review process
- Follow-up: How do you enforce tagging compliance?

---

## Behavioral & Scenario-Based

### Mid Level

**Q96: A new season of Stranger Things drops and crashes your CDN. How do you respond?**
- Expected:
  - Immediate: Scale up CloudFront distribution
  - Activate backup OCAs
  - Throttle non-critical services
  - Pre-position content on more OCAs
  - Monitor queue depths and latencies
  - Communication to users (status page)
  - Postmortem: capacity planning improvements
- Follow-up: How do you prepare for next major release?

**Q97: You discover a critical bug in the DRM system that allows content downloading. What do you do?**
- Expected:
  - Assess impact (how many users affected)
  - Immediately push hotfix
  - Revoke compromised keys
  - Forensic analysis of downloads
  - Legal team involvement
  - Studio notification (contractual obligation)
  - Long-term fix development
  - Security audit
- Follow-up: How do you prevent similar bugs?

**Q98: Your encoding pipeline has a backlog of 500 titles and SLA is breached. How do you recover?**
- Expected:
  - Prioritize: Originals > licensed content
  - Scale up: 10,000 spot instances
  - Parallel processing: 3x normal capacity
  - Skip lower priority profiles temporarily
  - Reduce quality thresholds slightly (VMAF 93 vs 95)
  - Clear backlog in 24-48 hours
  - RCA: prevent future backlogs
- Follow-up: What caused the backlog?

### Senior Level

**Q99: Netflix wants to launch in a country with strict content censorship. Design the system.**
- Expected:
  - Content filtering by region
  - Separate catalog database
  - Compliance automation
  - Local content moderation team
  - Government content review workflow
  - Encrypted content keys (anti-censorship)
  - Legal entity in-country
  - Exit strategy if regulations change
- Follow-up: Is it worth the complexity?

**Q100: You're asked to design Netflix for Mars colonists (400M km away, 20-minute latency). How?**
- Expected:
  - Challenge: 20-minute round-trip delay makes streaming impossible
  - Solution: Pre-download everything
  - Sync schedule:
    - Weekly catalog sync (overnight)
    - Download entire catalog to Mars CDN
    - Local OCA equivalent on Mars
  - Bandwidth: Use optimal orbital windows
  - Storage: 1PB+ local storage
  - Recommendations: Local computation
  - Reality: This is a fun thought experiment!
- Follow-up: What about new releases?

---

## Answer Key - Expected Proficiency Levels

### Question Difficulty Distribution
- **Junior (1-3 years)**: Q1-Q5, Q16-Q18, Q26-Q28, Q36-Q38, Q46-Q48, Q56-Q58, Q66-Q68, Q76-Q78, Q86-Q88
- **Mid (3-6 years)**: Q6-Q10, Q19-Q22, Q29-Q32, Q39-Q42, Q49-Q52, Q59-Q62, Q69-Q72, Q79-Q82, Q89-Q92, Q96-Q98
- **Senior (6+ years)**: Q11-Q15, Q23-Q25, Q33-Q35, Q43-Q45, Q53-Q55, Q63-Q65, Q73-Q75, Q83-Q85, Q93-Q95, Q99-Q100

### Key Topics Coverage
- System Architecture: 15 questions
- Content Ingestion: 10 questions
- Storage: 10 questions
- Encoding/Transcoding: 10 questions
- Streaming/Playback: 10 questions
- CDN/Distribution: 10 questions
- DRM/Security: 10 questions
- Performance/Scalability: 10 questions
- AWS Infrastructure: 10 questions
- Behavioral/Scenarios: 5 questions

---

## Key Metrics Summary

### Scale
- **Subscribers**: 200+ million globally
- **Content**: 15,000+ titles
- **Streaming**: 1 billion+ hours/day
- **Bandwidth**: 270 PB/month
- **Storage**: 175 PB total
- **OCAs**: 10,000+ servers

### Performance
- **Startup Time**: <2 seconds (target)
- **Cache Hit Rate**: 95%+
- **Latency**: <5ms (OCA), <50ms (CloudFront)
- **VMAF Score**: >95 (quality threshold)
- **Availability**: 99.99%

### Costs (Annual)
- **Total**: ~$500M/year
- **Storage**: $50M (S3, Glacier)
- **Encoding**: $50M (AWS Batch, EC2)
- **CDN**: $300M (CloudFront)
- **OCA**: $50M (hardware, support)
- **DRM/Security**: $125M (licensing, infrastructure)

---

**Total Questions**: 100
**Estimated Interview Time**:
- Junior: 45-60 minutes (10-15 questions)
- Mid: 60-90 minutes (15-20 questions)
- Senior: 90-120 minutes (20-30 questions)

**Note**: These questions are based on Netflix's production architecture and reflect real-world challenges in building a global streaming platform serving 200+ million subscribers. Questions include specific numbers, costs, and technical details from the documentation to ensure practical, implementation-focused discussions.
