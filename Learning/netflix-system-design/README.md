# Netflix System Design - Complete Overview

## Table of Contents

This repository contains comprehensive technical documentation for Netflix's streaming platform architecture. Each document covers a specific aspect of the system with in-depth technical details, cloud service specifications, and real-world implementation considerations.

## Documents

### 1. [Content Ingestion Pipeline](./01-content-ingestion-pipeline.md)
**How Netflix receives and processes content from studios**

- **Content Sources**: Studios, Netflix Originals, independent filmmakers
- **Acquisition Methods**: Direct upload, physical media, satellite feeds
- **Ingestion Architecture**: AWS S3, Lambda, API Gateway, Transfer Family
- **Validation Pipeline**: Technical validation, content analysis, metadata extraction
- **Quality Control**: AWS Rekognition, custom ML models, automated QC
- **Storage**: Multi-region S3 with lifecycle policies
- **Cost**: ~$1.5M/month for ingestion infrastructure

**Key Technologies**: AWS S3, Lambda, Step Functions, Rekognition, DynamoDB, RDS PostgreSQL

### 2. [Storage Architecture](./02-storage-architecture.md)
**How Netflix stores petabytes of video content**

- **Storage Tiers**: 
  - Hot (S3 Standard): Active streaming content
  - Warm (S3 Intelligent-Tiering): Recent additions
  - Cold (Glacier): Archived content
  - Archive (Glacier Deep Archive): Long-term preservation
- **Total Storage**: ~175PB across all tiers
- **Content Structure**: Raw source, mezzanine, encoded variants
- **Encoding Profiles**: 30-40 video profiles × 40-50 audio tracks per title
- **CDN Storage**: CloudFront caching + 10,000+ Open Connect Appliances
- **Cost**: ~$4.3M/month for storage and CDN

**Key Technologies**: AWS S3, S3 Glacier, CloudFront, RDS PostgreSQL, DynamoDB, FreeBSD (OCA)

### 3. [Video Streaming Architecture](./03-video-streaming-architecture.md)
**How streaming works for movies, series, and interactive content**

- **Streaming Protocols**: MPEG-DASH, HLS
- **Adaptive Bitrate (ABR)**: Dynamic quality switching based on bandwidth
- **Playback Session Flow**: Authentication, manifest download, DRM license, buffering
- **ABR Algorithm**: Network measurement, buffer monitoring, quality selection
- **Content Types**: 
  - Movies: Single continuous stream
  - TV Series: Binge-watching optimization with auto-play
  - Interactive Content: Branching narratives (Black Mirror: Bandersnatch)
- **Performance**: <2 second startup time, 95%+ cache hit rate
- **Bandwidth**: 270 petabytes/month, ~$25M/month cost

**Key Technologies**: MPEG-DASH, HLS, Media Source Extensions, ExoPlayer, AVPlayer, AWS CloudFront, Open Connect

### 4. [Encoding & Transcoding Pipeline](./04-encoding-transcoding-pipeline.md)
**How raw video is transformed into streaming-ready content**

- **Encoding Pipeline**: Pre-processing, parallel encoding, post-processing
- **Per-Title Encoding**: Custom bitrate ladder per content (20-30% savings)
- **Codecs**: H.264 (legacy), H.265/HEVC (current), AV1 (future)
- **Encoding Profiles**: 240p to 4K HDR, 0.3 Mbps to 25 Mbps
- **Audio Encoding**: AAC, Dolby Digital, Dolby Atmos
- **Quality Assurance**: VMAF scoring (target >95)
- **Infrastructure**: AWS Batch, 10,000+ spot instances, x265/x264 encoders
- **Cost**: $100-200 per title encoding

**Key Technologies**: FFmpeg, x264, x265, AWS Batch, EC2 Spot Instances, VMAF, Dolby Atmos

### 5. [CDN & Global Distribution](./05-cdn-global-distribution.md)
**How content is delivered to 200+ million subscribers worldwide**

- **Multi-Tier CDN**:
  - Tier 1: Netflix Open Connect (95% of traffic)
  - Tier 2: AWS CloudFront (4% of traffic)
  - Tier 3: AWS S3 Origin (1% of traffic)
- **Open Connect Appliances (OCA)**: 10,000+ servers in ISP networks
  - Hardware: 256GB RAM, 60TB SSD, 720TB HDD, 100Gbps networking
  - Capacity: 8,000-15,000 concurrent streams per OCA
- **Content Distribution**: Overnight fills based on popularity prediction
- **Performance**: <5ms latency to end users, 95%+ hit rate
- **Cost Savings**: $422M/year vs pure cloud CDN

**Key Technologies**: Custom FreeBSD servers, AWS CloudFront, S3, Route 53, HTTP/2, HTTP/3

### 6. [DRM & Security Architecture](./06-drm-security-architecture.md)
**How Netflix protects premium content and prevents piracy**

- **Multi-DRM**: Widevine (60%), FairPlay (30%), PlayReady (10%)
- **DRM Workflow**: License acquisition, key encryption, secure playback
- **Forensic Watermarking**: NexGuard technology, unique per session
- **HDCP Requirements**: Version 1.4 for HD, 2.2 for 4K
- **Secure Playback**: Trusted Execution Environment (TEE), secure video path
- **Output Protection**: Screen capture prevention, HDMI encryption
- **Account Security**: Multi-factor auth, password sharing detection
- **Cost**: ~$125M/year for security infrastructure
- **Protected Revenue**: $12-15 billion annually

**Key Technologies**: Widevine, FairPlay, PlayReady, NexGuard, TEE, AWS KMS, HDCP

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Netflix System Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Content Sources → Ingestion → Storage → Encoding → CDN → Users│
│                                                                  │
│  ┌────────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐   │
│  │  Studios   │   │  AWS S3  │   │ x265/AV1│   │CloudFront│   │
│  │  Netflix   │──▶│  Lambda  │──▶│  Batch  │──▶│   Open   │──▶│
│  │  Originals │   │ Step Func│   │ Encoders│   │  Connect │   │
│  └────────────┘   └──────────┘   └─────────┘   └──────────┘   │
│                         │                            │          │
│                         ▼                            ▼          │
│                   ┌──────────┐             ┌──────────────┐    │
│                   │  Catalog │             │ DRM License  │    │
│                   │ Database │             │    Server    │    │
│                   │ DynamoDB │             │  (Widevine)  │    │
│                   │    RDS   │             └──────────────┘    │
│                   └──────────┘                                  │
│                                                                  │
│  Client Devices:                                                │
│  - Web browsers (Chrome, Safari, Edge)                         │
│  - Mobile apps (iOS, Android)                                  │
│  - Smart TVs (Samsung, LG, Sony)                               │
│  - Streaming devices (Roku, Fire TV, Apple TV)                 │
│  - Game consoles (PlayStation, Xbox)                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Metrics

### Scale
- **Subscribers**: 200+ million globally
- **Countries**: 190+ countries
- **Content**: 15,000+ titles (movies + series)
- **Streaming Hours**: 1+ billion hours per day
- **Bandwidth**: 270+ petabytes per month
- **Storage**: 175+ petabytes
- **CDN Servers**: 10,000+ Open Connect Appliances

### Performance
- **Startup Time**: <2 seconds
- **Cache Hit Rate**: 95%+
- **Latency**: <50ms (p95)
- **Quality**: VMAF score >95
- **Availability**: 99.99%

### Infrastructure
- **AWS Services**: S3, CloudFront, EC2, Lambda, DynamoDB, RDS, Batch, Route 53
- **Encoding**: 10,000+ EC2 instances (spot)
- **License Servers**: Multi-region, 100K+ licenses/second
- **Databases**: PostgreSQL (catalog), DynamoDB (metadata)

### Costs (Estimated Annual)
- **CDN & Bandwidth**: $300M
- **Storage**: $50M
- **Encoding**: $20M
- **DRM & Security**: $125M
- **Infrastructure**: $200M
- **Total**: ~$700M/year

## Technology Stack Summary

### Storage & Databases
- **Object Storage**: AWS S3, S3 Glacier
- **Databases**: RDS PostgreSQL (relational), DynamoDB (NoSQL)
- **Caching**: Redis, Memcached
- **CDN**: AWS CloudFront, Netflix Open Connect (FreeBSD)

### Compute & Processing
- **Serverless**: AWS Lambda
- **Batch Processing**: AWS Batch (spot instances)
- **Orchestration**: AWS Step Functions
- **Container**: Docker, Kubernetes (for some services)

### Video Technology
- **Encoding**: FFmpeg, x264, x265, SVT-AV1
- **Protocols**: MPEG-DASH, HLS
- **DRM**: Widevine, FairPlay, PlayReady
- **Quality**: VMAF (Netflix's perceptual quality metric)

### Machine Learning
- **Content Analysis**: AWS Rekognition
- **Recommendation**: Custom ML models (TensorFlow)
- **Encoding Optimization**: Per-title encoding with ML
- **Popularity Prediction**: Content pre-positioning

### Security
- **Encryption**: AES-256, TLS 1.3
- **Key Management**: AWS KMS
- **DRM**: Multi-DRM stack
- **Watermarking**: NexGuard forensic watermarking
- **Authentication**: JWT, OAuth 2.0

## Design Principles

### 1. **Redundancy**
- Multi-region deployments
- CDN with 3-tier fallback (OCA → CloudFront → S3)
- Database replication across regions

### 2. **Performance**
- Edge caching (95%+ hit rate)
- Adaptive bitrate streaming
- Pre-positioning popular content
- <2 second startup time

### 3. **Cost Optimization**
- Spot instances (70% savings)
- Per-title encoding (20-30% savings)
- OCA deployment (90% bandwidth cost reduction)
- Lifecycle policies for storage

### 4. **Security**
- Multi-layered DRM
- Forensic watermarking
- Secure playback pipeline (TEE)
- HDCP enforcement

### 5. **Scalability**
- Auto-scaling compute (0-10,000+ instances)
- Global CDN (10,000+ OCAs)
- Serverless APIs (Lambda)
- NoSQL for high throughput (DynamoDB)

## How to Read This Documentation

1. **Start with Content Ingestion** (Document 1) to understand how content enters the system
2. **Move to Storage** (Document 2) to see how content is organized and stored
3. **Explore Streaming** (Document 3) for the user-facing playback experience
4. **Dive into Encoding** (Document 4) for video processing details
5. **Study CDN** (Document 5) for global content delivery
6. **Review Security** (Document 6) for DRM and protection mechanisms

Each document is self-contained but references others where relevant. Technical depth increases progressively, with code examples, architecture diagrams, and real-world considerations.

## Real-World Considerations

### Trade-offs
- **Quality vs Bandwidth**: Per-title encoding balances quality and cost
- **Latency vs Hit Rate**: Smaller cache = lower latency, larger cache = higher hit rate
- **Security vs UX**: Stricter DRM may impact older devices

### Challenges
- **Global Scale**: Serving 200M+ users across 190+ countries
- **Network Variability**: Adapting to 2G to 5G networks
- **Device Fragmentation**: Supporting 10,000+ device types
- **Content Protection**: Balancing security with user experience

### Future Directions
- **AV1 Codec**: 40-50% bandwidth savings (rolling out 2026-2028)
- **Edge Computing**: Encoding and personalization at the edge
- **5G Integration**: Ultra-low latency streaming (<10ms)
- **AI-Powered Features**: Auto-trailer generation, smart chapters

## Contributing

This documentation represents a technical deep-dive into Netflix's architecture based on public information, conference talks, engineering blogs, and industry best practices. It's intended for educational purposes and system design learning.

## References

- Netflix Tech Blog: https://netflixtechblog.com/
- AWS Architecture Blog: https://aws.amazon.com/architecture/
- Widevine Documentation: https://www.widevine.com/
- VMAF: https://github.com/Netflix/vmaf
- Open Connect: https://openconnect.netflix.com/

## License

This documentation is provided for educational purposes. Netflix, AWS, and other mentioned technologies are trademarks of their respective owners.

---

**Last Updated**: January 2026

**Total Pages**: 250+

**Technical Depth**: Senior/Principal Engineer Level

**Topics Covered**: 6 major architectural areas with complete technical specifications

