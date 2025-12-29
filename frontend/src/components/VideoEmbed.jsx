import React from 'react';

export default function VideoEmbed({ url, title }) {
  return (
    <div style={{
      position: 'relative',
      paddingBottom: '56.25%', // 16:9 aspect ratio
      height: 0,
      overflow: 'hidden',
      maxWidth: '100%',
      margin: '1.5rem 0',
      borderRadius: '8px',
      backgroundColor: '#000'
    }}>
      {url ? (
        <iframe
          src={url}
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
          textAlign: 'center'
        }}>
          <p>Video: {title || 'Coming Soon'}</p>
        </div>
      )}
    </div>
  );
}
