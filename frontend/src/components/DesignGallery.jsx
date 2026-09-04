import { useState } from 'react';
import designs from '../data/designsData';
import './DesignGallery.css';

function DesignGallery() {
  const [activeId, setActiveId] = useState(null);
  
  return (
    <section id="work" className="gallery">
      <div className="gallery__header">
        <h2 className="gallery__title">Selected work</h2>
        <span className="gallery__count">{designs.length} projects</span>
      </div>

      <div className="gallery__grid">
        {designs.map((design) => (
          <article
            key={design.id}
            className={`gallery__card ${
              design.featured ? 'gallery__card--wide' : ''
            }`}
            onMouseEnter={() => setActiveId(design.id)}
            onMouseLeave={() => setActiveId(null)}
          >
            <div className="gallery__image-wrap">
              <img
                src={design.image}
                alt={design.title}
                className="gallery__image"
                loading="lazy"
              />
              <div
                className={`gallery__overlay ${
                  activeId === design.id ? 'gallery__overlay--visible' : ''
                }`}
              >
                <span className="gallery__category">{design.category}</span>
                <span className="gallery__year">{design.year}</span>
              </div>
            </div>

            <div className="gallery__meta">
              <h3 className="gallery__name">{design.title}</h3>
              <p className="gallery__client">{design.client}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default DesignGallery;