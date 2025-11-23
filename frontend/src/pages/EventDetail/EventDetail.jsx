import React from 'react';
import styles from './EventDetail.module.css';
import {useLocation} from 'react-router-dom';


const EventDetail = () => {
    const location = useLocation();
    const {title, event_type, place, date, time, image, url} = location.state;

    return (
        <main className={styles.content}>
            <div className={styles['event-info']}>
                <div className={styles['event-preview']}>
                    <div className={styles['event-preview__container']}>
                        <img className={styles['event-preview__container-img']} src={image}
                             alt="фото события"/>
                    </div>

                    <p className={styles['event-preview__description-info']}>
                        <p className={styles['event-preview__description-name']}>Что нас ждет?</p>
                        {event_type}
                    </p>
                </div>
                <div className={styles['event-details']}>
                    <h1 className={styles['event-details__title']}>{title}</h1>
                    <div className={styles['event-details__program']}>
                        <p className={`${styles['event-details__name']} ${styles['event-details__date']}`}>Когда?</p>
                            <p className={styles['event-details__info']}>
                                {date}
                            </p>
                            <p className={`${styles['event-details__info']} ${styles['event-details__info-time']}`}>
                                {time}
                            </p>
                        <p className={styles['event-details__name']}>Где встречаемся?
                            <p className={styles['event-details__info']}>
                                {place}
                            </p>
                        </p>

                </div>
                <a href={url} className={`${styles['event-details__link']}`}>Записаться
                </a>
            </div>
        </div>
</main>
)
    ;
};

export default EventDetail;