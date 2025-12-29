import React, { useState } from 'react';

export default function VideoEmbed({ url, title, privacyEnhanced = false, transcript }) {
  const [showTranscript, setShowTranscript] = useState(false);

  // Convert YouTube watch URL to embed URL
  const getEmbedUrl = (videoUrl) => {
    if (!videoUrl) return null;

    // Handle YouTube URLs
    if (videoUrl.includes('youtube.com/watch')) {
      const videoId = new URL(videoUrl).searchParams.get('v');
      const domain = privacyEnhanced ? 'youtube-nocookie.com' : 'youtube.com';
      return `https://www.${domain}/embed/${videoId}`;
    }

    // Handle youtu.be URLs
    if (videoUrl.includes('youtu.be/')) {
      const videoId = videoUrl.split('youtu.be/')[1].split('?')[0];
      const domain = privacyEnhanced ? 'youtube-nocookie.com' : 'youtube.com';
      return `https://www.${domain}/embed/${videoId}`;
    }

    // Already an embed URL or other video platform
    return videoUrl;
  };

  const embedUrl = getEmbedUrl(url);

  return (
    <div style={{ margin: '2rem 0' }}>
      <div style={{
        position: 'relative',
        paddingBottom: '56.25%',
        height: 0,
        overflow: 'hidden',
        maxWidth: '100%',
        borderRadius: '8px',
        backgroundColor: '#000',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
      }}>
        {embedUrl ? (
          <iframe
            src={embedUrl}
            title={title || 'Video'}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              border: 0
            }}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#fff',
            textAlign: 'center',
            padding: '2rem'
          }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              📹 Video: {title || 'Coming Soon'}
            </p>
            <p style={{ fontSize: '0.9rem', opacity: 0.7 }}>
              Video content will be available soon
            </p>
          </div>
        )}
      </div>

      {transcript && (
        <div style={{
          marginTop: '1rem',
          border: '1px solid var(--ifm-color-emphasis-200)',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              backgroundColor: 'var(--ifm-color-emphasis-100)',
              border: 'none',
              cursor: 'pointer',
              textAlign: 'left',
              fontSize: '0.9rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              color: 'var(--ifm-font-color-base)'
            }}
          >
            <span>📝 Video Transcript & Key Points</span>
            <span style={{ fontSize: '1.2rem' }}>
              {showTranscript ? '▼' : '▶'}
            </span>
          </button>
          {showTranscript && (
            <div style={{
              padding: '1rem',
              backgroundColor: 'var(--ifm-background-surface-color)',
              borderTop: '1px solid var(--ifm-color-emphasis-200)',
              fontSize: '0.9rem',
              lineHeight: '1.7',
              whiteSpace: 'pre-line'
            }}>
              {transcript}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
