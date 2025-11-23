import React from 'react';
import styles from './EventCard.module.css';
import { Link } from 'react-router-dom';

export default function EventCard({ title, event_type, place, date, time, image, url }) {
  const getEventTypeColor = (type) => {
    const colors = {
      'workshop': '#10b981',
      'seminar': '#3b82f6', 
      'conference': '#f59e0b',
      'meetup': '#ef4444',
      'lecture': '#8b5cf6'
    };
    return colors[type?.toLowerCase()] || '#6b7280';
  };

  const eventColor = getEventTypeColor(event_type);

  return (
    <Link 
      to="/event-detail" 
      state={{ title, event_type, place, date, time, image, url }}
      className={styles.eventCardContainer}
    >
      <div className={styles.eventCardGlow}></div>
      
      <div className={styles.eventCardPreview}>
        {image ? (
          <img src={image} alt={title} className={styles.eventCardImg} />
        ) : (
          <div className={styles.eventPlaceholder}>
            <div className={styles.placeholderIcon}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M8 2v4"/>
                <path d="M16 2v4"/>
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <path d="M3 10h18"/>
              </svg>
            </div>
            <div className={styles.placeholderText}>Событие</div>
          </div>
        )}
        
        <div className={styles.imageOverlay}>
          <div 
            className={styles.eventTypeBadge}
            style={{ '--event-color': eventColor }}
          >
            {event_type}
          </div>
        </div>
      </div>

      <div className={styles.eventCardInfo}>
        <div className={styles.eventCardInfoTop}>
          <h3 className={styles.eventCardInfoTopTitle}>{title}</h3>
          
          <div className={styles.eventDetails}>
            <div className={styles.eventDetail}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              <span>{date} в {time}</span>
            </div>
            
            <div className={styles.eventDetail}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              <span>{place}</span>
            </div>
          </div>
        </div>

        <div className={styles.eventCardFooter}>
          <button className={styles.attendBtn}>
            <span>Посетить</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
          
          <button className={styles.shareBtn}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="18" cy="5" r="3"/>
              <circle cx="6" cy="12" r="3"/>
              <circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
          </button>
        </div>
      </div>
    </Link>
  );
}
