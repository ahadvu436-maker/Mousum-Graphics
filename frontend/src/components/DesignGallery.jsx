import React from 'react';
import './DesignGallery.css';

export default function DesignGallery({ designs }) {
  return (
    <section className="gallery" id="gallery">
      <h2 className="section-title">Design Gallery</h2>
      <div className="gallery-grid">
        {designs.map((item) => (
          <div key={item.id} className="gallery-card">
            <img src={item.image} alt={item.title} className="card-img" />
            <div className="card-info">
              <span className="card-category">{item.category}</span>
              <h3>{item.title}</h3>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
