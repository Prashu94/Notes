# Netflix CDN & Global Distribution - System Design

## Overview
Netflix's content delivery network serves 200+ million subscribers across 190+ countries, delivering billions of hours of streaming monthly with 99.99% availability and sub-second startup times. This combines AWS CloudFront with Netflix's proprietary Open Connect CDN.

## 1. CDN Architecture Overview

### 1.1 Multi-Tier CDN Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                    Global CDN Architecture                      │
│                                                                 │
│  Tier 1: Netflix Open Connect (OCA) - 95% of traffic          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  10,000+ OCA appliances deployed globally                 │ │
│  │  - Inside ISP networks (Comcast, Verizon, AT&T, etc.)    │ │
│  │  - Internet Exchange Points (IXPs)                        │ │
│  │  - Delivers 95% of Netflix traffic                        │ │
│  │  - Zero internet transit cost for Netflix                 │ │
│  │  - <5ms latency to end users                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ▲                                    │
│                            │ Fill (overnight)                   │
│                            │                                    │
│  Tier 2: AWS CloudFront - 4% of traffic                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  200+ Edge Locations worldwide                            │ │
│  │  - Serves users not near OCA                              │ │
│  │  - Handles OCA cache misses                               │ │
│  │  - New content pre-distribution                           │ │
│  │  - 10-50ms latency                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ▲                                    │
│                            │ Cache miss                         │
│                            │                                    │
│  Tier 3: AWS S3 Origin - 1% of traffic                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Multi-region S3 buckets                                  │ │
│  │  - Primary origin storage                                 │ │
│  │  - Only for cache misses                                  │ │
│  │  - Cross-region replication                               │ │
│  │  - 50-200ms latency                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## 2. Netflix Open Connect (OCA)

### 2.1 OCA Appliance Specifications

**Hardware Configuration (Generation 5)**:
```
┌────────────────────────────────────────────────────────────────┐
│               OCA Server Specifications (2026)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Chassis: Custom 2U Rack-mount Server                          │
│                                                                 │
│  CPU:                                                           │
│  - 2× Intel Xeon Gold 6330 (28 cores, 2.0 GHz)                │
│  - 56 cores / 112 threads total                                │
│  - Purpose: Metadata serving, TLS, logging                     │
│                                                                 │
│  Memory:                                                        │
│  - 256 GB DDR4 ECC RAM                                         │
│  - Purpose: File system cache, connection state                │
│                                                                 │
│  Storage (Flash Tier - Hot Content):                           │
│  - 8× 7.68TB NVMe SSDs (Samsung PM9A3)                        │
│  - Total: 61.44 TB usable                                      │
│  - RAID: None (software manages redundancy)                    │
│  - Performance: 28 GB/s read throughput                        │
│  - Latency: <100μs                                             │
│  - Purpose: Top 20% most popular content (24-48 hours)        │
│                                                                 │
│  Storage (HDD Tier - Warm Content):                            │
│  - 36× 20TB HDDs (Seagate Exos X20)                           │
│  - Total: 720 TB usable                                        │
│  - RAID: None (software erasure coding)                        │
│  - Performance: 8 GB/s read throughput                         │
│  - Purpose: Next 60% popular content (7-30 days)              │
│                                                                 │
│  Network:                                                       │
│  - 2× 100 Gigabit Ethernet (QSFP28)                           │
│  - Purpose: Serve 40-80 Gbps sustained traffic                │
│  - Redundancy: Active-active bonding                           │
│                                                                 │
│  Power:                                                         │
│  - Dual redundant 1600W power supplies                         │
│  - Power consumption: 600-800W typical, 1200W peak             │
│                                                                 │
│  Operating System:                                              │
│  - FreeBSD 13.x (customized)                                   │
│  - Netflix's custom delivery software (closed-source)          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Performance Capacity (Per OCA)**:
- **Concurrent Streams**: 8,000-15,000 simultaneous users
- **Throughput**: 40-80 Gbps sustained (peak 100 Gbps)
- **IOPS**: 1M+ IOPS (NVMe tier)
- **Storage**: 780TB total (60TB SSD + 720TB HDD)
- **Content**: 15,000-30,000 movies/episodes cached
- **Serving Ratio**: 1 OCA per 10,000-50,000 subscribers (varies by ISP)

### 2.2 OCA Deployment Models

**Model 1: ISP Embedded**
```
Internet Service Provider (e.g., Comcast, Verizon)
├── ISP Core Network
│   ├── Regional Data Center (e.g., Chicago)
│   │   └── OCA Cluster (10-50 servers)
│   │       - Serves millions of subscribers in region
│   │       - Inside ISP's private network
│   │       - Zero internet transit cost
│   │       - 1-5ms latency to subscribers
│   │
│   ├── Regional Data Center (e.g., New York)
│   │   └── OCA Cluster (20-100 servers)
│   │
│   └── [50+ regions across US]

Benefits:
- Zero peering/transit costs for ISP
- Improved subscriber experience (ultra-low latency)
- Reduced backbone traffic (90%+ hit rate locally)
- Free hardware provided by Netflix
```

**Model 2: Internet Exchange Point (IXP)**
```
Internet Exchange Point (e.g., DE-CIX Frankfurt, AMS-IX)
├── Neutral Facility
│   ├── Netflix OCA Rack (5-20 servers)
│   │   - Serves multiple ISPs peering at IXP
│   │   - Reduces transit for smaller ISPs
│   │   - 5-15ms latency
│   │
│   └── Connected ISPs:
│       ├── ISP A (peering)
│       ├── ISP B (peering)
│       └── [50+ ISPs]

Benefits:
- Serves multiple smaller ISPs without individual deployments
- Reduced transit costs for ISPs
- Better routing efficiency
```

**Global OCA Deployment Statistics**:
- **Total OCAs**: 10,000+ servers worldwide
- **Countries**: 75+ countries
- **ISP Partners**: 1,500+ ISPs
- **IXPs**: 100+ major IXPs
- **Traffic Served**: 95%+ of all Netflix streams
- **Cost to Netflix**: ~$50M/year (hardware replacement, support)
- **Savings**: $500M+/year in bandwidth costs

### 2.3 OCA Content Fill Strategy

**Content Popularity Prediction**:
```python
class ContentPopularityPredictor:
    def predict_popularity(self, content_id, oca_location):
        """
        Predict if content should be pre-positioned on OCA
        """
        features = {
            # Content features
            'release_date': self.get_release_date(content_id),
            'content_type': self.get_content_type(content_id),  # movie, series
            'genre': self.get_genre(content_id),
            'runtime': self.get_runtime(content_id),
            'cast_popularity': self.get_cast_popularity(content_id),
            
            # Regional features
            'region': oca_location['region'],
            'language_match': self.language_match_score(content_id, oca_location),
            'local_trends': self.get_regional_trends(oca_location),
            
            # Historical features
            'similar_content_performance': self.get_similar_performance(content_id),
            'trailer_views': self.get_trailer_engagement(content_id),
            'marketing_spend': self.get_marketing_score(content_id),
            
            # Time features
            'day_of_week': datetime.now().weekday(),
            'hour_of_day': datetime.now().hour,
            'upcoming_holiday': self.check_holidays(oca_location),
        }
        
        # ML model prediction (Random Forest, 85% accuracy)
        popularity_score = self.ml_model.predict(features)
        
        # Threshold: >70% predicted popularity = pre-fill
        return popularity_score > 0.70
    
    def prioritize_content_for_fill(self, oca_id):
        """
        Generate fill list for OCA (run nightly)
        """
        oca_location = self.get_oca_location(oca_id)
        all_content = self.get_catalog()
        
        fill_list = []
        for content in all_content:
            popularity = self.predict_popularity(content['id'], oca_location)
            
            if popularity > 0.70:
                fill_list.append({
                    'content_id': content['id'],
                    'priority': popularity,
                    'size_gb': content['size'],
                    'profiles': self.select_profiles(content, oca_location)
                })
        
        # Sort by priority, fit into available storage
        fill_list.sort(key=lambda x: x['priority'], reverse=True)
        
        # Capacity planning (fit into 780TB)
        total_size = 0
        final_fill_list = []
        
        for item in fill_list:
            if total_size + item['size_gb'] < 780000:  # 780TB limit
                final_fill_list.append(item)
                total_size += item['size_gb']
            else:
                break  # OCA full
        
        return final_fill_list
```

**Fill Process (Overnight)**:
```
23:00 UTC - Fill Window Opens
    ↓
1. Fill Server generates fill plan for each OCA
   - Analyze regional viewing patterns
   - Predict next 24-48 hours demand
   - Generate optimized content list
    ↓
2. Fill Server pushes content to OCA
   Protocol: HTTP/2 (efficient, parallel transfers)
   Bandwidth: 1-10 Gbps per OCA (off-peak)
   Duration: 2-6 hours
   Content: 5-20TB per night (new additions + replacements)
    ↓
3. OCA verifies content integrity
   - SHA-256 checksum validation
   - Segment playback test
   - Index update
    ↓
4. OCA reports status to control plane
   - Content inventory
   - Storage utilization (Flash: 95%, HDD: 85%)
   - Health metrics
    ↓
07:00 UTC - Fill Window Closes
```

**Fill Optimization**:
- **Incremental Fills**: Only transfer content not already cached
- **Delta Updates**: For content with minor changes (subtitle fixes)
- **Compression**: Transparent compression for lower bandwidth
- **Multi-source**: OCA can fill from nearest fill server or peer OCA

**Storage Tiers on OCA**:
```
┌────────────────────────────────────────────────────────────────┐
│                    OCA Storage Management                       │
│                                                                 │
│  Flash Tier (NVMe - 60TB)                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Top 20% Most Popular Content (24-48 hours)              │ │
│  │  - New releases (first week)                              │ │
│  │  - Trending shows (current binge)                         │ │
│  │  - Regional favorites                                     │ │
│  │  - Cache hit rate: 85-90%                                 │ │
│  │  - Latency: <1ms                                          │ │
│  │                                                            │ │
│  │  Example: Stranger Things (new season release week)      │ │
│  │  - All episodes, all profiles                             │ │
│  │  - Total: ~500GB                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ▼ (promotion/demotion)              │
│  HDD Tier (720TB)                                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Next 60% Popular Content (7-30 days)                    │ │
│  │  - Popular catalog titles                                 │ │
│  │  - Recent additions (week 2-4)                            │ │
│  │  - Seasonal content                                       │ │
│  │  - Cache hit rate: 70-80% (of requests to HDD tier)      │ │
│  │  - Latency: 5-10ms                                        │ │
│  │                                                            │ │
│  │  Example: The Crown (ongoing popularity)                 │ │
│  │  - All seasons, popular profiles                          │ │
│  │  - Total: ~1.5TB                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ▼ (cache miss)                      │
│  Cache Miss (20% of bottom-tier content)                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Fetch from CloudFront or Fill Server                    │ │
│  │  - Rarely watched catalog content                         │ │
│  │  - Niche titles                                           │ │
│  │  - Long-tail content                                      │ │
│  │  - Latency: 50-200ms (fetch + store)                     │ │
│  │  - Future requests served from HDD tier                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Eviction Policy**:
- **LFU (Least Frequently Used)**: Evict content with lowest view count
- **Age-based**: Evict content not accessed in 30+ days
- **Size-aware**: Prefer evicting larger files if impact is same
- **Regional**: Consider regional licensing (don't cache unavailable content)

### 2.4 OCA Request Routing

**Client-to-OCA Connection Flow**:
```
1. User clicks "Play" button
    ↓
2. Netflix app contacts API server (play.netflix.com)
    ↓
3. API server returns playback manifest
   Response includes:
   {
     "video_tracks": [
       {
         "profile": "1080p_high",
         "cdn_urls": [
           "https://oca1.isp.net/content/12345678/segment-1080p-001.m4s",
           "https://oca2.isp.net/content/12345678/segment-1080p-001.m4s",
           "https://cf-edge.netflix.com/content/12345678/segment-1080p-001.m4s"
         ]
       }
     ]
   }
    ↓
4. Client selects best CDN endpoint
   - Measures latency to each URL (HTTP HEAD request)
   - Selects fastest responding OCA
   - Fallback to CloudFront if OCAs unreachable
    ↓
5. Client requests video segments from OCA
   GET https://oca1.isp.net/content/12345678/segment-1080p-001.m4s
   
   OCA response:
   - Status: 200 OK
   - Latency: 2-5ms
   - Throughput: 20-50 Mbps (per client)
    ↓
6. Client continues requesting subsequent segments
   - Parallel requests (3-5 segments ahead)
   - Adaptive bitrate: switches profiles based on bandwidth
   - Sticky to OCA (uses same OCA for entire session)
```

**OCA Selection Algorithm** (Client-side):
```javascript
class OCASelector {
    async selectBestOCA(cdnUrls) {
        // Ping all OCAs in parallel
        const latencyPromises = cdnUrls.map(url => 
            this.measureLatency(url)
        );
        
        const latencies = await Promise.all(latencyPromises);
        
        // Sort by latency
        const sorted = latencies.sort((a, b) => a.latency - b.latency);
        
        // Select fastest (if latency < 50ms)
        if (sorted[0].latency < 50) {
            return sorted[0].url;
        }
        
        // Fallback to CloudFront
        return this.getCloudFrontURL();
    }
    
    async measureLatency(url) {
        const start = performance.now();
        
        try {
            // HEAD request (no data transfer)
            const response = await fetch(url, { method: 'HEAD' });
            const latency = performance.now() - start;
            
            return { url, latency, status: response.status };
        } catch (error) {
            // OCA unreachable
            return { url, latency: Infinity, status: 0 };
        }
    }
}
```

## 3. AWS CloudFront Integration

### 3.1 CloudFront Distribution Configuration

**Distribution Setup**:
```yaml
CloudFront Distribution:
  Id: E1234567890ABC
  DomainName: df3xj9k3lm2n.cloudfront.net
  Aliases:
    - cf-edge.netflix.com
    - assets.netflix.com
  
  Origins:
    - Id: S3-netflix-content-encoded
      DomainName: netflix-content-encoded.s3.amazonaws.com
      S3OriginConfig:
        OriginAccessIdentity: origin-access-identity/cloudfront/ABCDEFG123
      OriginShield:
        Enabled: true
        OriginShieldRegion: us-east-1  # Shield protects origin from spikes
    
    - Id: S3-netflix-assets
      DomainName: netflix-assets.s3.amazonaws.com
      S3OriginConfig:
        OriginAccessIdentity: origin-access-identity/cloudfront/HIJKLMN456
  
  DefaultCacheBehavior:
    TargetOriginId: S3-netflix-content-encoded
    ViewerProtocolPolicy: https-only
    AllowedMethods: [GET, HEAD, OPTIONS]
    CachedMethods: [GET, HEAD]
    
    ForwardedValues:
      QueryString: true
      QueryStringCacheKeys: [profile, language, version]
      Headers: [Range, Authorization]
      Cookies:
        Forward: none
    
    Compress: false  # Video already compressed
    
    MinTTL: 0
    DefaultTTL: 86400      # 24 hours
    MaxTTL: 31536000       # 1 year
    
    LambdaFunctionAssociations:
      - EventType: viewer-request
        LambdaFunctionARN: arn:aws:lambda:us-east-1:123:function:auth-check:1
      - EventType: origin-response
        LambdaFunctionARN: arn:aws:lambda:us-east-1:123:function:add-security-headers:1
  
  CacheBehaviors:
    # Manifest files (short TTL, always fresh)
    - PathPattern: "*.mpd"
      TargetOriginId: S3-netflix-content-encoded
      MinTTL: 0
      DefaultTTL: 300        # 5 minutes
      MaxTTL: 600
      Compress: true
    
    # Thumbnails and images (long TTL)
    - PathPattern: "/images/*"
      TargetOriginId: S3-netflix-assets
      MinTTL: 3600
      DefaultTTL: 2592000    # 30 days
      MaxTTL: 31536000
      Compress: true
  
  PriceClass: PriceClass_All  # Use all edge locations
  
  Enabled: true
  HttpVersion: http2
  IPV6Enabled: true
  
  Logging:
    Enabled: true
    Bucket: netflix-cloudfront-logs.s3.amazonaws.com
    Prefix: distribution-logs/
  
  ViewerCertificate:
    AcmCertificateArn: arn:aws:acm:us-east-1:123:certificate/abc-123
    SslSupportMethod: sni-only
    MinimumProtocolVersion: TLSv1.2_2021
```

### 3.2 CloudFront Edge Locations

**Global Distribution**:
```
North America: 60+ locations
- Major cities: New York (5), Los Angeles (5), Chicago (3), Dallas (3), etc.
- Coverage: 95%+ of US population within 50ms

Europe: 50+ locations
- Major cities: London (4), Frankfurt (4), Paris (3), Amsterdam (3), etc.
- Coverage: 90%+ of EU population within 50ms

Asia Pacific: 40+ locations
- Major cities: Tokyo (4), Seoul (3), Singapore (3), Mumbai (3), etc.
- Coverage: 80%+ of APAC population within 100ms

South America: 15+ locations
- São Paulo (3), Buenos Aires (2), Santiago (1), etc.

Africa: 10+ locations
- Johannesburg (2), Cairo (1), Lagos (1), etc.

Middle East: 10+ locations
- Dubai (2), Tel Aviv (1), Riyadh (1), etc.
```

**Regional Cache (Origin Shield)**:
```
┌────────────────────────────────────────────────────────────────┐
│                  Origin Shield Architecture                     │
│                                                                 │
│  User (Europe) → CloudFront Edge (London)                      │
│                       ↓                                         │
│                  Cache hit? YES → Return content               │
│                       ↓ NO                                      │
│                  Origin Shield (Ireland)                        │
│                       ↓                                         │
│                  Cache hit? YES → Return content               │
│                       ↓ NO                                      │
│                  S3 Origin (us-east-1)                         │
│                                                                 │
│  Benefits:                                                      │
│  - Consolidates requests from 50+ EU edges to 1 shield        │
│  - Reduces S3 request costs by 50-90%                          │
│  - Protects origin from traffic spikes                         │
│  - Increases cache hit ratio (larger cache)                    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 3.3 CloudFront Performance Optimization

**HTTP/2 & HTTP/3**:
- **HTTP/2**: Enabled by default
  - Multiplexing: Multiple requests over single connection
  - Header compression: Reduced overhead
  - Server push: Proactive sending of resources (not used by Netflix)
- **HTTP/3 (QUIC)**: Rolling out (2026)
  - UDP-based: Faster connection establishment
  - 0-RTT: Resume previous connection instantly
  - Better mobile performance: Handles network switching

**Byte-Range Requests**:
```http
# Client requests specific byte range of video segment
GET /content/12345678/segment-1080p-001.m4s HTTP/2
Host: cf-edge.netflix.com
Range: bytes=0-524287

# CloudFront responds with requested range (512KB)
HTTP/2 206 Partial Content
Content-Range: bytes 0-524287/10485760
Content-Length: 524288
Content-Type: video/mp4

<binary video data>
```

**Benefits**:
- **Fast Seeking**: Jump to any position without downloading entire segment
- **Resume Downloads**: Continue interrupted downloads
- **Adaptive Prefetching**: Download only what's needed

**Connection Pooling**:
```javascript
// Client-side connection management
class ConnectionPool {
    constructor() {
        this.connections = new Map();  // URL → Connection
        this.maxConnections = 6;       // HTTP/2 allows more
    }
    
    getConnection(url) {
        const host = new URL(url).host;
        
        if (!this.connections.has(host)) {
            // Create new HTTP/2 connection
            const connection = new HTTP2Connection(host);
            this.connections.set(host, connection);
        }
        
        return this.connections.get(host);
    }
    
    async downloadSegment(url) {
        const connection = this.getConnection(url);
        
        // Reuse existing connection (no TLS handshake)
        return connection.get(url);
    }
}
```

**Performance Metrics**:
- **Cache Hit Ratio**: 85-95% (at edge locations)
- **Origin Hit Ratio**: 50-70% (at origin shield)
- **Latency**: p50 < 30ms, p95 < 100ms, p99 < 200ms
- **Throughput**: 100TB/s aggregate (peak hours)

## 4. Intelligent Request Routing

### 4.1 DNS-Based Routing

**Route 53 Configuration**:
```yaml
Hosted Zone: netflix.com

Record Sets:
  # Playback API (geo-routing to nearest region)
  - Name: play.netflix.com
    Type: A
    TTL: 60
    Routing: Geolocation
    GeoLocations:
      - North America → 
          Records:
            - us-east-1: 54.239.17.7
            - us-west-2: 54.240.17.7
          Weight: Equal
          Health Check: Enabled
      
      - Europe →
          Records:
            - eu-west-1: 54.241.17.7
            - eu-central-1: 54.242.17.7
          Weight: Equal
      
      - Asia Pacific →
          Records:
            - ap-southeast-1: 54.243.17.7
            - ap-northeast-1: 54.244.17.7
          Weight: Equal
      
      - Default → us-east-1
  
  # CDN endpoints (CNAME to CloudFront)
  - Name: cf-edge.netflix.com
    Type: CNAME
    TTL: 300
    Value: df3xj9k3lm2n.cloudfront.net
  
  # OCA endpoints (dynamic, per-ISP)
  - Name: oca1.isp.comcast.net
    Type: A
    TTL: 60
    Value: 10.x.x.x  # Private IP (within ISP network)
```

### 4.2 Client-Side CDN Selection

**Multi-CDN Strategy**:
```javascript
class CDNSelector {
    constructor() {
        this.cdnEndpoints = [
            { type: 'oca', url: 'https://oca1.isp.net', priority: 1 },
            { type: 'oca', url: 'https://oca2.isp.net', priority: 1 },
            { type: 'cloudfront', url: 'https://cf-edge.netflix.com', priority: 2 },
            { type: 's3', url: 'https://s3-direct.netflix.com', priority: 3 }
        ];
        
        this.currentCDN = null;
        this.failedCDNs = new Set();
    }
    
    async selectCDN() {
        // Filter out failed CDNs
        const available = this.cdnEndpoints.filter(cdn => 
            !this.failedCDNs.has(cdn.url)
        );
        
        // Sort by priority
        available.sort((a, b) => a.priority - b.priority);
        
        // Test top 3 CDNs in parallel
        const candidates = available.slice(0, 3);
        const tests = candidates.map(cdn => this.testCDN(cdn.url));
        
        const results = await Promise.all(tests);
        
        // Select fastest
        const fastest = results
            .filter(r => r.success)
            .sort((a, b) => a.latency - b.latency)[0];
        
        if (fastest) {
            this.currentCDN = fastest.url;
            return fastest.url;
        }
        
        // All CDNs failed (rare)
        throw new Error('No CDN available');
    }
    
    async testCDN(url) {
        const start = Date.now();
        
        try {
            // Test connectivity with small HEAD request
            const response = await fetch(`${url}/health`, {
                method: 'HEAD',
                timeout: 2000  // 2 second timeout
            });
            
            return {
                url,
                success: response.ok,
                latency: Date.now() - start,
                status: response.status
            };
        } catch (error) {
            // CDN unreachable
            this.failedCDNs.add(url);
            return { url, success: false, latency: Infinity };
        }
    }
    
    markCDNFailed(url) {
        // Mark CDN as failed, trigger re-selection
        this.failedCDNs.add(url);
        this.currentCDN = null;
        
        // Retry failed CDNs after 5 minutes
        setTimeout(() => {
            this.failedCDNs.delete(url);
        }, 300000);
    }
}
```

## 5. Performance Monitoring & Optimization

### 5.1 Real-Time Monitoring

**CloudWatch Metrics**:
```python
class CDNMonitoring:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
    
    def publish_metrics(self, distribution_id, metrics):
        # Publish CloudFront metrics
        self.cloudwatch.put_metric_data(
            Namespace='Netflix/CDN',
            MetricData=[
                {
                    'MetricName': 'CacheHitRate',
                    'Value': metrics['cache_hit_rate'],
                    'Unit': 'Percent',
                    'Dimensions': [
                        {'Name': 'DistributionId', 'Value': distribution_id},
                        {'Name': 'Region', 'Value': metrics['region']}
                    ]
                },
                {
                    'MetricName': 'OriginLatency',
                    'Value': metrics['origin_latency_ms'],
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'DistributionId', 'Value': distribution_id}
                    ]
                },
                {
                    'MetricName': 'BytesDownloaded',
                    'Value': metrics['bytes_downloaded'],
                    'Unit': 'Bytes',
                    'Dimensions': [
                        {'Name': 'DistributionId', 'Value': distribution_id}
                    ]
                },
                {
                    'MetricName': '4xxErrorRate',
                    'Value': metrics['error_4xx_rate'],
                    'Unit': 'Percent',
                    'Dimensions': [
                        {'Name': 'DistributionId', 'Value': distribution_id}
                    ]
                },
                {
                    'MetricName': '5xxErrorRate',
                    'Value': metrics['error_5xx_rate'],
                    'Unit': 'Percent',
                    'Dimensions': [
                        {'Name': 'DistributionId', 'Value': distribution_id}
                    ]
                }
            ]
        )
```

**Alerting Thresholds**:
- Cache hit rate < 80%: Warning
- Origin latency > 500ms (p95): Warning
- 4xx error rate > 1%: Warning
- 5xx error rate > 0.1%: Critical
- Bandwidth utilization > 80%: Scale up

### 5.2 Cost Optimization

**CloudFront Pricing (2026)**:
```
Data Transfer Out (per GB):
- First 10 TB: $0.085
- Next 40 TB: $0.080
- Next 100 TB: $0.060
- Next 350 TB: $0.040
- Over 500 TB: $0.030

Requests (per 10,000):
- HTTP: $0.0075
- HTTPS: $0.0100

Monthly Netflix CloudFront Cost (estimated):
- Data transfer: 50PB × $0.030 = $1.5M
- HTTPS requests: 500B requests × $0.0100 / 10K = $5M
- Total: ~$6.5M/month = $78M/year

OCA Cost (estimated):
- Hardware: $50M/year (10K servers × $5K amortized)
- Support: $10M/year
- Total: $60M/year

Total CDN Cost: $138M/year

Savings from OCA:
- Without OCA: 95% of traffic via CloudFront = $500M+/year
- With OCA: Only 5% via CloudFront = $78M/year
- Net savings: $422M/year (ROI: 7x)
```

## 6. Future CDN Technologies

### 6.1 Edge Computing
- **Compute@Edge**: Run encoding/transcoding at edge
- **Personalization**: Real-time thumbnail generation per user
- **A/B Testing**: Edge-based experimentation

### 6.2 5G Integration
- **MEC (Multi-Access Edge Compute)**: Cache at mobile operator edge
- **Ultra-Low Latency**: <10ms for interactive content
- **Mobile Optimization**: Adaptive streaming for 5G

### 6.3 P2P-Assisted Delivery
- **WebRTC**: Peer-to-peer content sharing (experimental)
- **Use Case**: Popular events (live releases)
- **Benefit**: Reduce CDN load by 20-30%

